<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/budb_internal.h -->
# sources/distributed-fs/openafs/src/budb/budb_internal.h

## Purpose
Centralizes internal budb server prototypes across allocation, hash, dump, lock, verification, RPC, logging, and structure conversion modules. It is the glue header for the C files in this group.

## Important APIs, Types, And Functions
It declares database allocation (`InitDBalloc`, `AllocStructure`, `FreeStructure`, `AllocBlock`, `FreeBlock`), hash operations (`InitDBhash`, `ht_DBInit`, `ht_HashIn`, `ht_HashOut`, `ht_LookupEntry`, `scanHashTable`, `RemoveFromList`), dump streaming (`writeDatabase`), lock validation (`checkLockHandle`), address validation (`checkDiskAddress`), RPC initialization (`InitProcs`, `callPermitted`, `InitRPC`), and server logging. It also exposes conversion/printing helpers from `struct_ops.c`.

## Control Flow
The declarations reveal the layering: every RPC starts through `InitRPC`, primitive reads/writes live in `database.c`, fixed-size block allocation is in `db_alloc.c`, lookup/indexing goes through `db_hash.c`, and high-level RPCs in `procs.c` compose those pieces.

## State And Persistence
The prototypes operate on the global in-memory `db` cache and persistent Ubik database blocks. Helpers use network-byte-order structures on disk and convert at RPC boundaries.

## Dependencies And Integration Points
The header depends on `database.h` types, generated budb RPC types, Ubik transactions, RX calls, and shared struct conversion helpers. It is included by most budb server modules.

## Risks And Test Signals
Prototype drift can silently corrupt cross-module calls in C. Useful signals are a full budb build with warnings enabled, RPC smoke tests, database create/delete cycles, dump/restore, and online verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/budb_internal.h -->
