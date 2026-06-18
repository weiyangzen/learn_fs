<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/database.c -->
# sources/distributed-fs/openafs/src/budb/database.c

## Purpose
Owns the global in-memory backup database cache and the low-level Ubik read/write wrappers. It initializes allocation/hash subsystems, performs bounds-checked database I/O, and rebuilds or refreshes the cached header through Ubik cache callbacks.

## Important APIs, Types, And Functions
`db_panic` logs and exits via audited `BUDB_EXIT`. `InitDB` clears global `db`, resets `pollCount`, and initializes allocation/hash metadata. `dbwrite`, `dbread`, and `cdbread` wrap `ubik_Seek`, `ubik_Write`, and `ubik_Read`; `cdbread` first calls `checkDiskAddress`. `UpdateCache` reads and validates `db.h`, rebuilds a missing database header when allowed, initializes hash tables with `ht_DBInit`, and invalidates memory hash caches. `CheckInit` registers `UpdateCache` with `ubik_CheckCache`.

## Control Flow
Most server RPCs call `InitRPC`, which calls `CheckInit`; that refreshes `db.h` if Ubik says the cache changed. Reads and writes poll the LWP I/O manager every four operations in non-pthread builds.

## State And Persistence
`struct memoryDB db` is allocated here and mirrors the persistent Ubik database header plus memory hash-table caches. `dbwrite` rejects writes into the header unless the buffer aliases the in-core header field, and rejects writes past `eofPtr`.

## Dependencies And Integration Points
This file is below all budb RPC logic and above Ubik. It depends on `database.h`, `error_macros.h`, `budb_internal.h`, Ubik, auditing, and online verifier address checks.

## Risks And Test Signals
Bounds checks depend on `db.h.eofPtr` being current and network ordered. Header writes require exact pointer aliasing, so misuse of temporary buffers fails. Signals are empty-database initialization, corrupted version/checkVersion rejection, read/write error injection, and verifier-backed `cdbread` coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/database.c -->
