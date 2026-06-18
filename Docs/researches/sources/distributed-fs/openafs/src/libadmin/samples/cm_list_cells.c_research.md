<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/cm_list_cells.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/cm_list_cells.c

## Purpose
Demonstrates iterating over the cell database known by a cache manager through libadmin utility CM stats calls.

## Important APIs, Types, And Functions
The program uses `Usage`, `ParseArgs`, and `main`, then calls `afsclient_Init`, `afsclient_NullCellOpen`, `afsclient_CMStatOpenPort`, `util_CMListCellsBegin/Next/Done`, `afsclient_CMStatClose`, and `afsclient_CellClose`. It prints `afs_CMListCell_t` records and `UTIL_MAX_CELL_HOSTS` server addresses.

## Control Flow
After host/port parsing and CM stats connection setup, it starts a cell-list iterator, loops until `util_CMListCellsNext` fails, prints each cell name with nonzero server addresses, validates the terminal status is `ADMITERATORDONE`, closes the iterator, connection, and cell.

## State And Persistence
No persistent state is written. The iterator state is owned by the util layer and released by `Done`; the sample holds one current `afs_CMListCell_t`.

## Dependencies And Integration Points
It integrates with the OpenAFS cache manager's CM stats service and admin utility iterator API. Network address printing assumes the returned address value is in display-ready big-endian order.

## Risks And Test Signals
Failure exits can leak handles/iterators. The address output is manual byte shifting, which is easy to misread if address byte order changes. Tests should cover iterator completion, empty cell lists, multi-host cells, and error status when `Next` stops for reasons other than `ADMITERATORDONE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/cm_list_cells.c -->
