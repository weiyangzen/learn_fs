<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/sphinx/rstFlatTable.py -->
# sources/distributed-fs/ceph-client/Documentation/sphinx/rstFlatTable.py

## Purpose
Docutils/Sphinx extension implementing the `flat-table` directive, a two-level bullet-list table format with row-span, column-span, automatic right-edge spanning, and optional empty-cell filling.

## Important APIs, Types, And Functions
- `FlatTable` subclasses docutils `Table` and registers directive options `header-rows`, `stub-columns`, `widths`, `fill-cells`, `class`, and `name`.
- Roles `cspan` and `rspan` produce `colSpan` and `rowSpan` marker nodes.
- `ListTableBuilder` parses the nested bullet list, normalizes spans, and builds docutils `table`, `tgroup`, `thead`, `tbody`, `row`, and `entry` nodes.
- `parseRowItem()`, `parseCellItem()`, and `roundOffTableDefinition()` contain the core validation and table-shape logic.

## Control Flow
`FlatTable.run()` validates that content exists, parses the directive body into an anonymous node, and delegates to `ListTableBuilder`. The builder requires exactly one top-level bullet list, treats each first-level item as a row, and requires each row to contain exactly one second-level bullet list. Cell span markers are removed from the first child node and translated into `morecols`/`morerows` entry attributes.

## State And Persistence
All state is in memory in `ListTableBuilder.rows` and `max_cols`. The builder inserts `None` placeholders to represent cells covered by spans, then recalculates the column count and either extends the last cell or appends empty cells for short rows.

## Dependencies And Integration Points
Integrates with docutils roles, directives, table nodes, and Sphinx extension setup. It exists to make kernel documentation tables more maintainable than grid tables while still producing normal docutils table nodes for all builders.

## Risks And Edge Cases
Span normalization swallows ambiguous row/column span insertion errors with bare `except`, so bad input can produce surprising output instead of a precise diagnostic. `line[0]` assumptions are avoided here, but malformed nested lists still raise docutils system messages. Stub columns and row spans are called out as potentially problematic for some builders.

## Test Signals
Exercise empty content, non-list content, malformed row nesting, header rows, stub columns, `:cspan:`, `:rspan:`, auto-span, and `:fill-cells:` across HTML and XML/text builders. Table dimensions and generated `morecols`/`morerows` attributes are the key assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/sphinx/rstFlatTable.py -->
