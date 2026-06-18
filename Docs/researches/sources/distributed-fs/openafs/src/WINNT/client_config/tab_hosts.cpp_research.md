# sources/distributed-fs/openafs/src/WINNT/client_config/tab_hosts.cpp

## Purpose
`tab_hosts.cpp` implements the Cells/Hosts tab for viewing and editing CellServDB cell entries and their database servers. In Control Center mode it also validates and persists the default cell.

## Important APIs, Types, and Functions
Main routines are `HostsTab_DlgProc`, `HostsTab_OnInitDialog`, `HostsTab_CommitChanges`, `HostsTab_OnApply`, `HostsTab_FillList`, `HostsTab_OnAdd/Edit/Remove`, `CellEdit_*`, `ServerEdit_*`, and `TextToAddr`.

## Control Flow
Initialization reads CellServDB once into `g.Configuration.CellServDB` and fills a fastlist with cell lines. Add/edit opens a cell property sheet; server add/edit resolves addresses or names and stores formatted CellServDB lines; cell apply replaces the cell line and following server entries in the in-memory list. Hosts apply writes the file and, in Control Center mode, validates/persists the default cell.

## State and Persistence Behavior
CellServDB edits are staged in memory until `CSDB_WriteFile` during apply. Cell edit dialogs use temporary copied `CELLDBLINE` entries in list item params and free them on destroy. Control Center default cell persists through `Config_SetCellName`.

## Dependencies and Integration Points
The General tab calls `HostsTab_CommitChanges` before applying service settings. Cell validation uses `cm_SearchCellRegistry`, `CSDB_FindCell`, and `cm_SearchCellByDNS`. Server editing uses Winsock DNS and the custom sockaddr control.

## Risks and Edge Cases
Server dialog specific-address mode overwrites the comment with the numeric address before lookup, losing user-entered comments. `CellEdit_SortFunction` stores order in `pNext` cast to an integer, reusing a linked-list field as UI metadata. `TextToAddr` rejects `inet_addr` result zero, which can reject valid `0.0.0.0`, and uses legacy `gethostby*` APIs.

## Test Signals
Tests should cover reading/writing CellServDB, add/edit/remove cells, multiple server ordering, DNS success/failure, Control Center default-cell validation through registry/file/DNS, cancellation without file writes, and comments/linked-cell preservation.
