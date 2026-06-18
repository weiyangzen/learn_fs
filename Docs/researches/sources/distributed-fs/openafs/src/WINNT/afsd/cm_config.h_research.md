# sources/distributed-fs/openafs/src/WINNT/afsd/cm_config.h

## Purpose
`cm_config.h` provides default Windows cache-manager configuration constants and declares the cell/configuration access functions implemented by `cm_config.c`. It is the interface used by cell initialization, administrative tools, and service startup code to locate and update client configuration.

## Important APIs and Types
Defaults include cache size, block size, async store size, cell count, stat count, chunk size, daemon count, server thread count, and trace buffer size. `cm_configFile_t` aliases `FILE`, `cm_configProc_t` receives resolved server addresses/hostnames/ranks, and `cm_enumCellProc_t` receives enumerated cell names. The header declares file, registry, DNS, and write helpers plus `AFS_THISCELL`, `AFS_CELLSERVDB_UNIX`, and `AFS_CELLSERVDB` names.

## Control Flow
Callers typically obtain a root cell with `cm_GetRootCellName`, search one or more sources for a cell with `cm_SearchCellRegistry`, `cm_SearchCellFileEx`, or `cm_SearchCellByDNS`, and receive each server through a callback such as `cm_AddCellProc`. Administrative changes use registry write helpers or the open/append/close file sequence for CellServDB.

## State and Persistence
The declared functions read and write registry values and CellServDB files, but the header itself contains no storage. The defaults are compile-time values used when registry or command-line configuration is absent.

## Dependencies and Integration Points
The interface requires Windows networking structures, `stdio.h` unless `__CM_CONFIG_INTERFACES_ONLY__` is set, and `CELL_MAXNAMELEN` expectations from the cell layer. It is consumed by `cm_cell.c`, startup configuration, and management paths that create cells.

## Risks and Test Signals
Tests should verify ABI compatibility of callback signatures, default values used by startup, buffer sizes promised by the APIs, and correct behavior when `__CM_CONFIG_INTERFACES_ONLY__` excludes implementation-facing declarations.
