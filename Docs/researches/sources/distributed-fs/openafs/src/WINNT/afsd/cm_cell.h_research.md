# sources/distributed-fs/openafs/src/WINNT/afsd/cm_cell.h

## Purpose
`cm_cell.h` defines the Windows cache manager's cell object contract: identity, global linkage, hash linkage, VLDB server references, mutable flags, DNS expiration, linked-cell name, hash macros, and the public lookup/update APIs used throughout the cache manager.

## Important APIs and Types
`cm_cell_t` contains `magic`, `cellID`, global/name/ID/free list links, fixed cell `name`, `vlServersp`, mutex `mx`, `flags`, `timeout`, and `linkedName`. Flags identify DNS-derived server lists, invalid VL servers, freelance cells, and hash membership. `CM_CELL_NAME_HASH` and `CM_CELL_ID_HASH` map names/IDs into `cm_data` hash tables. Public routines include initialization/shutdown/validation, lookup by name or ID, server-rank changes, hash insertion/removal, server-add callback `cm_AddCellProc`, update and create-with-info paths.

## Control Flow
Most callers enter through `cm_GetCell`/`cm_GetCell_Gen` or `cm_FindCellByID`; these return cells that may have been refreshed by `cm_UpdateCell`. Configuration import and administrative updates use `cm_CreateCellWithInfo`, while config parsers pass discovered VL servers to `cm_AddCellProc`.

## State and Persistence
The header describes in-memory structures only. Persistent cell sources live in registry, CellServDB, and DNS, but the fields here cache their resolved results and expiration. `name` is documented as immutable once set, while `flags`, `timeout`, `vlServersp`, and `linkedName` have explicit lock ownership.

## Dependencies and Integration Points
The type references `cm_serverRef_t`, `cm_server_t`, `struct sockaddr_in`, and global `cm_data` sizing. It is central to connection selection, volume lookup, callback server ownership, and configuration enumeration.

## Risks and Test Signals
Consumers must respect the split between `cm_cellLock`, `cm_serverLock`, and `cellp->mx`. Tests should cover hash-table membership flags, cellID hash behavior, name length boundaries, DNS invalidation flags, and linked-cell name handling.
