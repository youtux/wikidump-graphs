import sys

import pygal
import lxml
import collections


def get_data(filepath):
    stats = {
        'section_names_per_revision': {},
        'sections_per_revision': {},
        'revisions': {},
    }

    xml = lxml.etree.parse(filepath)

    for type_ in ['global', 'last_revision']:
        section_names = xml.xpath(
            '/stats/section_names_per_revision/{type_}/section'.format(type_=type_))

        c = collections.Counter({
            el.get('name'): int(el.get('count')) for el in section_names
            })
        stats['section_names_per_revision'][type_] = c

        sections_counts = xml.xpath(
            '/stats/sections_per_revision/{type_}/sections'.format(type_=type_))
        c = collections.Counter({
            int(el.get('number')): int(el.get('count')) for el in sections_counts
            })
        stats['sections_per_revision'][type_] = c

        revisions = xml.xpath(
            '/stats/revisions/{type_}'.format(type_=type_))[0]
        stats['revisions'][type_] = int(revisions.get('count'))

    return stats


def fill_serie(list_key_values, stop, start=0):
    serie = [None for i in range(start, stop)]
    for key, value in list_key_values:
        if key >= len(serie):
            continue
        serie[key] = value

    return serie

def draw_section_counts(stats, output_path, x_axis_length=50):
    revisions_count = stats['revisions']

    section_counts_graph = pygal.Bar(
        width=1200,
    )
    section_counts_graph.x_labels = [str(x) for x in range(x_axis_length)]
    section_counts_graph.x_title = '# sections'
    section_counts_graph.y_title = 'Frequency'
    section_counts_graph.title = 'Distribution of # sections per revision'

    for type_name, type_key in [('All revisions', 'global'), ('Last revision', 'last_revision')]:
        serie_raw = stats['sections_per_revision'][type_key]

        serie_raw_normalized = [(number, count / revisions_count[type_key])
                                for number, count in serie_raw.items()]

        serie = fill_serie(serie_raw_normalized, x_axis_length)

        serie_for_graph = [{
            'label': str(number),
            'value': frequency
            } for number, frequency in enumerate(serie)]

        section_counts_graph.add(type_name, serie_for_graph)

    section_counts_graph.render_to_png(output_path + '.png')


def draw_section_names(stats, output_path_prefix, x_axis_length=50):
    revisions_count = stats['revisions']

    for type_name, type_key in [('All revisions', 'global'), ('Last revision', 'last_revision')]:
        section_counts_graph = pygal.HorizontalBar(
            height=1200,
            # width=2000,
            # print_labels=True,
        )
        # section_counts_graph.y_labels = [str(x) for x in range(x_axis_length)]
        section_counts_graph.y_title = 'Section names'
        section_counts_graph.x_title = 'Frequency'
        section_counts_graph.title = 'Distribution of section names per revision'
        serie_raw = stats['section_names_per_revision'][type_key]

        serie_cutted = serie_raw.most_common(x_axis_length)

        serie_raw_normalized = [(name, count / revisions_count[type_key])
                                for name, count in serie_cutted]

        serie_for_graph = [{
            'label': name,
            'value': frequency
            } for name, frequency in serie_raw_normalized]

        serie_for_graph_rev = list(reversed(serie_for_graph))

        section_counts_graph.add(type_name, serie_for_graph_rev)
        section_counts_graph.x_labels = [d['label'] for d in serie_for_graph_rev]

        section_counts_graph.render_to_png(output_path_prefix + '.' + type_key + '.png')


def aggreagate_stats(file_path_list):
    stats = {
        'section_names_per_revision': {
            'global': collections.Counter(),
            'last_revision': collections.Counter(),
        },
        'sections_per_revision': {
            'global': collections.Counter(),
            'last_revision': collections.Counter(),
        },
        'revisions': {
            'global': 0,
            'last_revision': 0,
        },
    }

    keys = list(stats.keys())

    for file_path in file_path_list:
        print('reading', file_path)
        new_stat = get_data(file_path)
        for key in keys:
            for type_key in ('global', 'last_revision'):
                stats[key][type_key] += new_stat[key][type_key]

    return stats


def main():
    paths = sys.argv[1:]

    stats = aggreagate_stats(paths)

    draw_section_counts(stats, 'output/section_counts')

    draw_section_names(stats, 'output/section_names')


if __name__ == '__main__':
    main()
