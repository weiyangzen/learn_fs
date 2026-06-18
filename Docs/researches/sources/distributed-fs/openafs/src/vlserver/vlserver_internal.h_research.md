## sources/distributed-fs/openafs/src/vlserver/vlserver_internal.h

Purpose: internal VLDB server interface between RPC procedure code and low-level Ubik/storage utilities.

Important APIs/types/functions: defines `struct vl_ctx`, the per-operation transaction context containing the active `ubik_trans`, selected host address cache, selected multihome extent cache, and selected VLDB header cache. Declares `Init_VLdbase()` from `vlprocs.c` and storage/hash/cache helpers from `vlutils.c`: `vlwrite`, `vlentrywrite`, `write_vital_vlheader`, `readExtents`, `CheckInit`, `AllocBlock`, `FindExtentBlock`, `FindByID`, `FindByName`, `EntryIDExists`, `NextUnusedID`, hash dump/thread/unthread/hash/unhash functions, `NextEntry`, `FreeBlock`, `vlsetcache`, and `vlsynccache`.

Control flow: no executable control flow, but it codifies the layering: RPC handlers call `Init_VLdbase()` to populate `vl_ctx`; helpers then operate through that context and return VLDB/Ubik error codes.

State and persistence: `vl_ctx` selects either read caches or write caches depending on lock type. Persistent mutation happens through the declared helper functions, which write Ubik database offsets and update cached headers/extent blocks.

Dependencies: requires `struct ubik_trans`, `afs_uint32`, `afs_int32`, `afsUUID`, `struct extentaddr`, `struct vlheader`, and `struct nvlentry` from included VLDB/Ubik headers.

Integration points: included by `vlserver.c`, `vlprocs.c`, and `vlutils.c`. It is the narrow private boundary that keeps generated/public RPC types out of the lower storage manipulation APIs.

Risks: because the prototypes expose raw offsets and mutable cache pointers, callers must hold the correct Ubik transaction and lock mode. Omitting a new storage helper here can push modules toward duplicate declarations. The header does not own synchronization; correctness depends on Ubik transaction discipline and `vlsetcache`/`vlsynccache` usage.

Test signals: compile/link coverage across VLDB modules, transaction tests proving read contexts never mutate write caches, write transaction commit invoking `vlsynccache`, and error-path tests for each declared helper through RPC-level operations.
