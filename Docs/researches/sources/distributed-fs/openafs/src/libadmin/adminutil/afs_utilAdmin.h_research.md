# sources/distributed-fs/openafs/src/libadmin/adminutil/afs_utilAdmin.h

## Purpose
Declares the public utility-admin API for libadmin. It exposes error translation, CellServDB database-server iteration, server-name address resolution, cell-handle validation, generic RPC stats controls, cache-manager callback inspection helpers, and rxdebug helper wrappers.

## Important APIs, Types, And Functions
Constants define fixed public buffer sizes: `UTIL_MAX_DATABASE_SERVER_NAME`, `UTIL_MAX_CELL_NAME_LEN`, `UTIL_MAX_CELL_HOSTS`, and `UTIL_MAX_RXDEBUG_VERSION_LEN`. Public data structures include `util_databaseServerEntry_t`, `afs_CMServerPref_t`, `afs_CMListCell_t`, `afs_CMCellName_t`, and `rxdebugVersion_t`. Function prototypes mirror the implementation in `afs_utilAdmin.c` and use the `ADMINAPI` calling convention plus `afs_status_p` error reporting.

The RPC stats prototypes are intentionally generic: callers provide a `struct rx_connection *` and function pointer matching each server's stats RPC, while the utility layer normalizes results into `afs_RPCStats_t`, `afs_RPCStatsState_t`, `afs_RPCStatsClearFlag_t`, and `afs_RPCStatsVersion_t` from `afs_Admin.h`.

## Control Flow
The header defines begin/next/done iterator flows for database servers, RPC stats, cache-manager server preferences, cache-manager cells, rxdebug connections, and rxdebug peers. Single-call helpers retrieve local cell name, cache-manager config, rxdebug version/basic stats/rx stats, RPC stats state, and stats version.

## State And Persistence
No state is stored in the header. It defines caller-visible fixed-size structures used to receive snapshots of configuration, RPC statistics, cache-manager callback state, and rxdebug state. Callers must treat iterator IDs as opaque and terminate them through the matching `Done` functions.

## Dependencies And Integration Points
The header includes `afs_Admin.h` and `afs_AdminErrors.h` and forward-declares `struct rpcStats`. It depends on Rx connection types and rxdebug handle types defined by `afs_Admin.h`. Higher-level admin libraries include it for common validation, enumeration, stats, and cache-manager inspection.

## Risks And Test Signals
The main risks are ABI drift in fixed-size buffers and function-pointer signatures, especially for RPC stats retrieval. Since buffers are caller-provided, tests should compile consumers that allocate the documented sizes and exercise all begin/next/done APIs against empty, one-item, and multi-item data sources.
