# File Research: sources/block-storage/parted/parted/table.c

## Purpose

`table.c` implements a small wide-character table renderer for Parted’s human-readable `print` output. It accepts rows, calculates display widths, pads columns, strips trailing blanks, and returns one rendered string.

## Main Responsibilities

- Own an opaque table structure containing row strings and computed column widths.
- Add rows either as raw `wchar_t **` arrays or from `StrList` rows.
- Compute column widths using display width rather than byte length when NLS is enabled.
- Render all rows with two-space column delimiters and newline row suffixes.

## Data Model

The private `Table` struct contains:

- `ncols`: fixed column count.
- `nrows`: current row count.
- `rows`: array of rows, each row an array of owned `wchar_t *` cells.
- `widths`: computed display width per column.

## Important Functions

- `table_new()` allocates an empty table with a fixed column count.
- `table_destroy()` frees every cell, row array, row list, width array, and table object.
- `table_calc_column_widths()` recomputes maximum width per column after rows change.
- `table_add_row()` appends a caller-supplied row and transfers ownership of the row and cells to the table.
- `table_add_row_from_strlist()` duplicates every `StrList` cell into a new row and adds it to the table.
- `table_render_row()` appends one padded row to the accumulating rendered output.
- `table_render_rows()` renders all rows.
- `table_render()` returns a newly allocated rendered `wchar_t *`.

## Rendering Behavior

Columns are left-aligned. Widths are calculated with `wcswidth(..., MAX_WIDTH)` where available, with a hard maximum width of 512. Cells are separated by two spaces. After each row is appended, trailing blanks are removed before the newline is added.

## Dependencies and Interactions

- Used by `parted.c` human-mode `do_print()` to render partition tables.
- Uses `StrList` as a row source.
- Uses `xmalloc()`, `xrealloc()`, and `xalloc_die()` for allocation handling.
- Under non-NLS builds, wide-character operations are macro-mapped to byte-string equivalents.

## Notable Edge Cases

- `table_new()` asserts `ncols >= 0`, but `table_destroy()` asserts `ncols > 0`; zero-column tables cannot be safely destroyed through the normal path.
- `table_add_row_from_strlist()` allocates based on `str_list_length(list)` but does not verify that the list length matches `t->ncols`.
- `table_add_row()` recalculates all column widths after every appended row.
- The public comment in `table.h` suggests ownership of `list`, but this implementation duplicates `StrList` contents and does not store or free the list itself.
