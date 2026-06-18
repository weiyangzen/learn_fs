# sources/distributed-fs/openafs/src/afs/afs_cell.c

Purpose: Manages AFS cell configuration inside the cache manager: AFSDB lookup coordination, persistent cell-name-to-number mapping, aliases, cell LRU lookup, primary-cell state, cell creation/update, and shutdown cleanup.

Important APIs and functions: AFSDB functions are `afs_StopAFSDB`, `afs_AFSDBHandler`, `afs_GetCellHostsAFSDB`, and `afs_LookupAFSDB`. Cell-name persistence uses `afs_cellname_init`, `afs_cellname_write`, and helper lookups. Alias APIs include `afs_GetCellAlias`, `afs_NewCellAlias`, and `afs_CellOrAliasExists`. Cell lookup and lifecycle APIs include `afs_CellInit`, `afs_NewCell`, `afs_GetCellByName`, `afs_GetCell`, `afs_GetCellStale`, `afs_GetCellByIndex`, `afs_GetCellByHandle`, `afs_GetPrimaryCell`, `afs_SetPrimaryCell`, `afs_RemoveCellEntry`, `afs_CellNumValid`, and `shutdown_cell`.

Control flow: AFSDB lookup serializes one kernel request to a user-space handler using `afsdb_client_lock`, `afsdb_req_lock`, `pending`, and `complete`. Cell-name initialization reads records from a cache inode using a magic, cell number, name length, and name bytes; writes persist only used cell names after full initialization. `afs_NewCell` either updates an existing cell or allocates a new one, computes an MD5 cell handle, validates linked-cell requests, marks old VL servers gone, installs new server hosts, sorts them, assigns a stable cell number/index, and invalidates dynroot unless hushed.

State and persistence: Volatile state includes `CellLRU`, `afs_xcell`, `afs_thiscell`, cell objects, aliases, AFSDB request state, and cell indices. Durable state is the optional cell-name mapping file identified by `afs_cellname_inode`; only referenced/used cell names are rewritten. Static non-AFSDB cell entries are protected from being overwritten by later AFSDB timeouts unless they had no servers.

Dependencies and integration points: Integrates with server creation/sorting, dynroot invalidation, cache-file I/O, MD5 handles, AFSDB userspace upcall via `afs_call.c`, volume/VL server selection, callback debug RPCs, and primary-cell hard-mount logic in `afs_analyze.c`.

Risks: AFSDB coordination depends on wakeups and shutdown state; missed transitions can strand lookups. Persistent cell-name parsing stops silently on malformed or duplicate records. `afs_NewCell` mutates existing server host flags and linked-cell backpointers under nested locks. Some getters update LRU/ref-used state but do not visibly refcount cell objects beyond lock protocol, so callers must follow `afs_PutCell` conventions.

Test signals: Initialize with memcache and disk cache, parse/write valid and malformed cell-name files, AFSDB success/failure/alias creation/shutdown, static cell protected from AFSDB overwrite, new and updated cell host lists, linked-cell validation, alias duplicate rejection, primary-cell set/get, lookup by name/id/index/handle, dynroot invalidation, remove server entry, and shutdown memory cleanup.
