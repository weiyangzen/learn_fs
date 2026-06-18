# sources/distributed-fs/coda/coda-src/vice/codaproc.cc

## Purpose
`codaproc.cc` implements Coda file-server RPC handlers and helpers for replicated-volume operations that are specific to conflict repair, replica resolution, commit-on-piggyback completion, fid allocation, and volume-version validation. It is one of the central mutation-side files in `vice`: it translates replicated volume IDs to local read-write volume IDs, obtains volume/vnode locks, applies semantic checks, mutates recoverable vnode/volume state, spools resolution log records, breaks callbacks, and releases all state through the common `PutObjects`/RVM paths.

## Important APIs, types, and functions
- `FS_ViceAllocFids` and `FS_OldViceAllocFids` allocate bounded fid ranges, using VSG-member stride/index from `XlateVid` so disconnected clients can keep using issued fids across replication-group membership changes.
- `FS_ViceCOP2` parses piggybacked `(ViceStoreId, ViceVersionVector)` records and calls `InternalCOP2` for each completed operation.
- `InternalCOP2` dequeues a `cpent` from `CopPendingMan`, sorts/deduplicates up to `MAXFIDS`, locks affected vnodes, calls `COP2Update` in an RVM transaction, releases objects, removes the pending entry, and deallocates truncated resolution-log records.
- `FS_ViceResolve` and `ViceResolveOne` coordinate multi-server repair/resolution using VRDB entries, `res_mgrpent`, `Res_LockAndFetch`, directory/file resolution engines, and unlock multicalls.
- `FS_ViceSetVV` is a repair-tool RPC that sets an object's version vector after validating client identity and volume repair lock ownership.
- `FS_ViceRepair` drives manual repair of inconsistent file, symlink, or directory objects. It fetches repair contents, gathers related objects, validates semantics, performs mutations, adds a COP-pending entry, and spools VM log records for directory repairs.
- `PerformFileRepair`, `PerformDirRepair`, `CheckRepairSemantics`, `CheckFileRepairSemantics`, `CheckDirRepairSemantics`, `CheckRepairACLSemantics`, `SetRights`, and `SetNRights` implement the repair semantic and mutation core.
- `GetRepairObjects`, `GetSubTree`, `CheckTreeRemoveSemantics`, and `PerformTreeRemoval` support deadlock-conscious subtree traversal and recursive removal during repairs/resolution.
- `NewCOP1Update`, `COP2Update`, and `UpdateVVs` update vnode/volume version vectors and COP2-pending flags.
- `FS_ViceGetVolVS`, `GetMyVS`, `SetVSStatus`, and `FS_ViceValidateVols` expose volume version stamps and callback validation.

## Control flow
The normal COP flow is split in two phases. COP1 mutation code records this host's update with `NewCOP1Update`, sets the COP2-pending bit for replicated volumes, and adds the affected fid(s) to the pending table. Later, `FS_ViceCOP2` receives update sets, calls `InternalCOP2`, finds the pending store ID, locks affected objects in fid order, and lets `COP2Update` apply version-vector slots for other successful replicas. For directories, full-host-set COP2 can trigger resolution-log truncation.

Repair flow starts in `FS_ViceRepair`: validate RPC/client/volume, read or receive repair data, parse directory repair lists, collect all participant vnodes, run semantic checks, then perform either file or directory repair. File repair swaps inode/state, adjusts disk usage, updates data version/status, clears inconsistency, and records COP1. Directory repair replays repair opcodes such as create, remove, rmdir subtree, rename, ACL changes, owner/mode/mtime changes, then stamps the directory and spools repair records. All exits funnel through cleanup that frees repair lists and calls `PutObjects`.

Resolution flow uses VRDB membership to contact peers. `ViceResolveOne` locks and fetches status/VVs from all accessible replicas, filters failures, calls directory or file resolve engines, and unlocks all locked peers. `FS_ViceResolve` handles directory hints and loop avoidance so parent/related objects can be resolved in a bounded sequence.

## State and persistence behavior
Persistent state includes vnode disk fields, inode references, ACL contents, volume disk usage, volume/vnode version vectors, COP2-pending flags, directory resolution logs, and recoverable VM log allocation bitmaps. RVM transactions surround COP2 updates and vnode puts; repair object release goes through `PutObjects`, which handles inode/RVM cleanup and transaction semantics. The file also mutates global `OngoingRepairs`, references global `NullVV`, and depends on `NullFid` from `srv.cc`.

## Dependencies and integration points
This file integrates with RPC2/SFTP side effects, LWP scheduling, RVM, the volume/vnode package, directory handles, callbacks, access-list/protection APIs, VRDB/VLDB replication metadata, resolution communication, `coppend` pending-COP management, repair-file parsing, operation-level check/perform helpers in `operations.h`, and timing/probing instrumentation. It exports entry points reached through generated RPC dispatch in the file server.

## Risks
The code relies heavily on manual lock ordering, goto cleanup, raw pointer ownership, and `CODA_ASSERT` for invariants. Several paths mutate `repairent` copies and then write back, require `MAXFIDS` capacity, or assume directory handles are released in the right order. Bugs here can corrupt persistent vnode state, leak inode blocks, leave COP2 entries stuck until timeout, fail to truncate logs, or produce false conflicts. Recursive subtree operations can be expensive and are sensitive to cycles or malformed directory data. `GetSubTree` contains an assignment inside an assert-like cleanup path (`CODA_ASSERT(error = 0)`), which is suspicious even if compiled assertions may mask it.

## Test signals
Useful tests include replicated create/store/remove/COP2 scenarios, piggybacked COP2 buffer length validation, manual file and directory repairs with ACL/rename/subtree changes, resolution with partial host failures and hint loops, volume-version callback validation, and crash/restart tests around RVM transactions and pending-COP expiry. Regression signals are stale callbacks, unresolved COP2-pending flags, volume version stamp mismatches, leaked inodes, non-empty resolution logs after full COP2 success, and `SrvLog` messages from failed `GetFsObj`, `SpoolVMLogRecord`, or lock/unlock phases.
