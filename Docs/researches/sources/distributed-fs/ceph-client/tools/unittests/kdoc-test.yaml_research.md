# sources/distributed-fs/ceph-client/tools/unittests/kdoc-test.yaml

## Purpose

`kdoc-test.yaml` is the dynamic test corpus for the Python kernel-doc parser and output generators. It supplies C snippets, expected parsed `KdocItem` values, and expected reStructuredText/man-page output.

## Important APIs, Types, and Fields

The file has 34 named tests. Common fields are `name`, `fname`, `description`, `source`, optional `exports`, and `expected`. Expected entries exercise `kdoc_item`, `rst`, and `man` outputs. Covered cases include basic functions, exported symbols, DOC blocks, complex/simple tables, ASCII artwork, variables of multiple declarations, guarded/private declarations, lock annotations, struct groups, and kernel-doc output formatting.

## Control Flow and Data Flow

`test_kdoc_parser.py` reads the YAML, dynamically creates parser and output tests, and either parses `source` into items or converts expected items into `RestFormat`/`ManFormat` output. The YAML is data-driven: each entry expands into one or more unittest methods.

## State and Persistence Behavior

The file persists expected behavior for kernel-doc parsing and formatting. Test runs do not modify it. Some expected man output includes dates that are normalized by the test helper.

## Dependencies and Integration Points

It depends on the schema file, PyYAML, kernel-doc parser classes, output classes, and transform rules. It is the main integration point between real-ish C examples and Python unit tests.

## Risks and Edge Cases

Large literal expected blocks are sensitive to whitespace and formatter changes. Because many cases validate source-to-output without an explicit `kdoc_item`, parser regressions can be localized less precisely. The corpus intentionally includes tricky transform cases such as lock annotations and struct-group private regions.

## Test Signals

The strongest signal is all dynamically generated parser, RST, and man tests passing. Schema validation passing confirms shape, while failures in individual generated method names identify the scenario name.
