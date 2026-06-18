# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/TableListing.java

Purpose: `TableListing` formats command output as aligned text tables with optional headers, left/right justification, and wrapping of selected columns.

Important APIs and types: `Justification` enum supplies `LEFT` and `RIGHT`. `Builder` supports `addField`, `hideHeaders`, `showHeaders`, `wrapWidth`, and `build`. `TableListing.addRow` appends rows, and `toString` renders the table. Private `Column` tracks row values, max width, wrap mode, and per-row wrapped lines.

Control flow: builders create columns containing header rows. `addRow` validates row length and appends values. `toString` computes total width, shrinks wrappable columns down to a minimum width of 10 until the target wrap width is met or no more shrink is possible, then renders header/data rows, expanding wrapped cells into multiple output lines and padding missing wrapped lines.

State and persistence behavior: table content is kept in memory as column arrays and row strings. `toString` mutates column wrap widths, so repeated rendering after a narrow wrap may preserve narrower internal max widths.

Dependencies and integration points: used by Hadoop command-line tools. It depends on Apache Commons Lang `StringUtils` for padding and Hadoop `StringUtils.wrap` for line wrapping.

Risks: `addRow` throws a generic `RuntimeException` on wrong arity. Wrapping/padding is character-count based and not display-width aware. Long unwrappable columns can exceed requested width. Null cell values become empty strings.

Test signals: cover left/right padding, headers hidden/shown, row arity errors, null cells, wrapping multi-line cells, repeated `toString`, minimum wrap width behavior, and tables with no data rows.
