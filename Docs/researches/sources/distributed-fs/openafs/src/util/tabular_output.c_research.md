# sources/distributed-fs/openafs/src/util/tabular_output.c

Purpose: Implements a small table builder/printer supporting ASCII, CSV, and HTML output with optional row sorting.

Important APIs and types: Public functions include `util_newTable()`, `util_newCellContents()`, `util_setTableHeader()`, `util_setTableFooter()`, `util_setTableBodyRow()`, `util_addTableBodyRow()`, `util_printTable*()`, and `util_freeTable()`. Private `struct util_Table` stores output type, dimensions, column metadata, rows, footer/header, and function pointers. `struct util_TableRow` owns per-cell strings.

Control flow and state: `util_newTable()` validates type/sort key, initializes function pointers, creates a header row, and stores caller-provided column metadata. Adding a body row grows the row array in chunks, creates a temporary row for sort placement, shifts existing content if sorted, copies content into the selected row, and updates `RowLength`. Print functions dispatch by type. Sorting uses binary search and either string compare or `util_GetInt64()`.

Dependencies and integration: Includes `afs/tabular_output.h`, `afs/afsutil.h`, roken, and `opr_min`. Consumers are command-line tools that need formatted output.

Risks and test signals: `util_setTableFooter()` appears inverted: it allocates a footer only when `Footer != NULL`, then dereferences `Table->Footer`, so initial footer setting can crash. `do_setTableRow()` uses `strcpy()` into fixed 30-byte cells, while `util_addTableBodyRow()` later uses `strncpy()`, so long content can overflow in setters/header. `util_freeTable()` calls `freeTableRow()` on possibly NULL footer. CSV/HTML output does not escape cell content. Tests should cover footer use, long cells, sorting, and all output types.
