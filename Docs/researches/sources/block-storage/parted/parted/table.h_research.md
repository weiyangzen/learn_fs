# File Research: sources/block-storage/parted/parted/table.h

## Purpose

`table.h` declares Parted’s opaque table rendering API used to format human-readable partition tables.

## Contents

- Includes wide-character and standard headers.
- Includes `strlist.h`.
- If NLS is disabled, remaps `wchar_t` to `char`.
- Declares `typedef void Table;` as an opaque public handle.

## Declared API

- `table_new(int ncols)` creates a table with a fixed number of columns.
- `table_destroy(Table *t)` frees the table and owned row/cell memory.
- `table_add_row(Table *t, wchar_t **row)` appends a raw row; implementation takes ownership of the row.
- `table_add_row_from_strlist(Table *t, StrList *list)` appends a row derived from a string list.
- `table_render(Table *t)` returns the rendered wide-character string, owned by the caller.

## Dependencies and Role

This header is consumed by `parted.c` for human `print` output. It hides the actual `Table` struct layout from callers.

## Notable Details

The header comment says callers must not free either `row` or `list`, but the implementation only takes ownership of raw rows passed to `table_add_row()`. `table_add_row_from_strlist()` duplicates the list strings; callers in this tree destroy the original `StrList` after adding.
