# sources/distributed-fs/openafs/src/WINNT/afsd/cm_cell.c

## Purpose
`cm_cell.c` manages in-memory cell objects for the Windows cache manager. It resolves cell names from registry, CellServDB, or DNS; maintains VLDB server references; performs prefix and ID lookup; initializes/restores cell tables; and handles mutable cell server-list refresh while preserving stable cell names and IDs.

## Important APIs and Types
The file operates on `cm_cell_t` and `cm_cell_rock_t` from `cm_cell.h`. Main APIs include `cm_GetCell`, `cm_GetCell_Gen`, `cm_FindCellByID`, `cm_UpdateCell`, `cm_AddCellProc`, `cm_InitCell`, `cm_ShutdownCell`, `cm_ValidateCell`, `cm_CreateCellWithInfo`, hash-table add/remove helpers, `cm_ChangeRankCellVLServer`, and `cm_DumpCells`. `cm_cellLock` protects global cell lists and hashes; each cell also has `cellp->mx` for flags and timeout fields.

## Control Flow
`cm_GetCell_Gen` normalizes the requested name, strips trailing dots, checks the name hash, then falls back to unambiguous prefix matching. If `CM_FLAG_CREATE` is supplied and no existing cell is found, it allocates from the free list or `cm_data.cellBaseAddress`, populates VL servers via `cm_SearchCellRegistry`, `cm_SearchCellFileEx`, or DNS, resolves duplicate full names, inserts the cell into name/ID hashes, and sets up linked-cell relationships. `cm_UpdateCell` refreshes invalid, empty, or expired VL server lists and randomizes same-rank servers.

## State and Persistence
Cells live in cache-manager memory under `cm_data`: `allCellsp`, `freeCellsp`, name/ID hash tables, `currentCells`, and `maxCells`. Server-list data can be refreshed from persistent registry or CellServDB inputs, or from DNS with TTL-driven expiration. The cell object itself persists only as part of the cache manager's mapped data region; mutexes and VL server lists are reinitialized on restart.

## Dependencies and Integration Points
This module integrates with `cm_config.c` for cell source lookup, `cm_server` for VL server creation/ranking/list ownership, DNS lookup controls (`cm_dnsEnabled`), volume lookup through cell IDs, and freelance mode for `Freelance.Local.Cell`.

## Risks and Test Signals
Risk concentrates in lock conversion, duplicate-name races, server references temporarily attached to a discarded cell, and DNS/registry/file fallback behavior. Test signals include exact-name and prefix matching, ambiguous-prefix rejection, trailing-dot normalization, linked-cell recursion protection, DNS TTL invalidation, free-list reuse, and validation failures for corrupted cell lists or hash membership.
