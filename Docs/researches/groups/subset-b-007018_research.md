# Research: subset-b-007018

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/codaproc.cc -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/codaproc.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/codaproc.h -->
# sources/distributed-fs/coda/coda-src/vice/codaproc.h

## Purpose
`codaproc.h` is a small shared header for repair and recursive directory-removal support in the vice server. It declares two C-style parameter blocks used to carry volume, vnode-list, store-id, RPC, and client context through directory enumeration callbacks.

## Important APIs, types, and functions
- `rmBlk` carries a `VListStruct *vlist`, volume ID, `Volume *`, `ViceStoreId *`, and `ClientEntry *` for recursive removes during repairs.
- `semBlk` carries an RPC handle, client pointer, volume pointer, parent fid, and accumulated error code for recursive semantic checking.

## Control flow
The header itself has no functions. Its structs are intended to be filled by caller code before invoking directory traversal helpers whose callback signatures only accept `void *` context. Related implementation in `codaproc.cc` and `treeremove.h` uses similar blocks to pass mutation and semantic-check state through `DH_EnumerateDir`.

## State and persistence behavior
The structs do not own persistent state. They carry borrowed pointers into persistent volume/vnode structures and store IDs, so correctness depends on the caller keeping locks and object lifetimes valid for the traversal.

## Dependencies and integration points
The header assumes prior visibility of `VListStruct`, `Volume`, `ViceStoreId`, `ClientEntry`, `RPC2_Handle`, and `ViceFid`. It is included by vice server repair/reintegration code that already includes the Coda/RPC/volume headers defining those types.

## Risks
Because the header has no include guard in the visible file and no includes of its own, it depends on include order. The callback context structs expose raw pointers and do not encode ownership or lock requirements, so misuse can lead to stale pointers or operations on unlocked vnodes.

## Test signals
Compile coverage through repair and tree-remove code is the main signal. Runtime tests should exercise recursive remove/semantic-check paths, especially nested directories and error propagation through callback context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/codaproc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/codaproc2.cc -->
# sources/distributed-fs/coda/coda-src/vice/codaproc2.cc

## Purpose
`codaproc2.cc` implements server-side reintegration of disconnected client mutations. It receives a client modification log, validates and replays CML records atomically against the local volume, performs or defers file-data transfers, records resolution logs, updates COP/version-vector state, and returns volume version/callback status.

## Important APIs, types, and functions
- `struct rle` is the parsed reintegration-log entry. It stores opcode, store ID, mtime, up to three fids/VVs, names, and opcode-specific fields for create, mkdir, symlink, remove, rmdir, store, setattr, and rename.
- `FS_ViceReintegrate` is the full reintegration RPC. It processes piggybacked COP2 data, validates parameters, gathers objects, checks/performs operations, and releases/finalizes state.
- `FS_ViceOpenReintHandle`, `FS_ViceQueryReintHandle`, `FS_ViceSendReintFragment`, and `FS_ViceCloseReintHandle` support staged transfer of large store data into a temporary inode before replaying a single-store reintegration.
- `ValidateReintegrateParms` translates volume IDs, fetches and unpacks the client reintegration log via RPC2 side effects, checks duplicate/retry store IDs, and obtains the volume in exclusive mode.
- `GetReintegrateObjects` preallocates created vnodes, builds the fid-ordered `vlist`, resolves parent/child fids by name where needed, and locks existing vnodes.
- `CheckSemanticsAndPerform` walks the log in client order, calls operation-specific semantic checks, applies mutations with `Perform*` helpers, spools resolution records, adjusts disk usage, and fetches deferred store data.
- `PutReintegrateObjects` frees log memory, finalizes COP/version state with `ReintFinalCOP`, reports stale directories, persists through `PutObjects`, and updates the volume's reintegrator replay-detection table.
- `AddChild`, `LookupChild`, and `AddParent` are helper routines also useful to repair code.
- `ReintNormalVCmp`, `ReintPrelimCOP`, `ReintFinalCOP`, and `ValidateRHandle` encode reintegration-specific version comparison, preliminary store-id stamping, final COP1/COP2 handling, and temporary handle validation.

## Control flow
The file documents reintegration as four phases. Phase 0 optionally drains piggybacked COP2. Phase 1 receives a serialized CML log into memory, unpacks entries into a linked list, translates fids from VSG to local RW volume IDs, checks replay history, validates optional reintegration handles, and locks the volume exclusively. Phase 2 allocates vnodes for creates, builds a complete fid set including parents and named children, then acquires existing objects in fid order to avoid deadlocks. Phase 3 replays each record: stores prepare a replacement inode and delay bulk transfer; setattr/create/remove/link/rename/mkdir/rmdir/symlink check semantics, update weak-equality state, perform mutations, mark stale directories, spool VM log records, and adjust block accounting. At the end of phase 3, store data is fetched back from the client under the host lock unless it was pre-sent through a reintegration handle. Phase 4 frees the parsed log, finalizes COP state, returns stale directory/version status, puts objects, and releases the exclusive volume lock.

## State and persistence behavior
The file mutates persistent vnode metadata, directory contents, file inode references, volume disk usage, resolution logs, volume version vectors, COP-pending entries, and the per-volume `reintegrators` replay table. Store reintegration can create temporary server-side inodes via `icreate`; failed side effects truncate or discard intermediate data. Successful finalization calls `NewCOP1Update` for each mutated vnode and either adds pending COP entries or spools `ResolveNULL_OP` for directories needing resolution.

## Dependencies and integration points
It depends on RPC2 side effects, callback fetches, LWP scheduling via `PollAndYield`, RVM/volume/vnode management, `coppend`, `lockqueue`, VRDB/VLDB translation, CML unpackers, `operations.h` check/perform functions, resolution-log spooling, `inconsist.h`, and callback host locks. It calls helpers from `codaproc.cc` such as `FS_ViceCOP2`, `GetMyVS`, `SetVSStatus`, `NewCOP1Update`, and `PollAndYield`.

## Risks
The replay path is high risk because it combines client-supplied serialized data, name-to-fid lookups that can change during replay, persistent mutation, bulk transfer, and manual memory cleanup. The code uses raw `malloc/free/strdup`, assumes a valid exclusive volume lock across phases, and relies on `Index` for partial failure reporting. Delayed store transfer means semantic mutations happen before file bytes arrive, so failure cleanup must be exact. Replay detection depends on store-id uniquifier ranges and can be disabled by clients using large uniquifiers. Several comments call out historical retry and rename-version comparison uncertainties.

## Test signals
Test disconnected replay for every CML opcode, mixed-operation atomicity, repeated reintegration retry detection (`VLOGSTALE`), staged store handles including partial fragments and old server start times, failed callback fetch rollback, stale directory reporting, block accounting, weak-equality file stores, and RVM crash recovery. Logs around `ValidateReintegrateParms`, `GetReintegrateObjects`, `CheckSemanticsAndPerform`, `SpoolVMLogRecord`, and `CBFetch` are primary diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/codaproc2.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/coppend.cc -->
# sources/distributed-fs/coda/coda-src/vice/coppend.cc

## Purpose
`coppend.cc` implements the in-memory pending-COP table used between COP1 and COP2. Mutating operations add affected fids under a `ViceStoreId`; later COP2 processing dequeues the entry to update version vectors. A background LWP expires old entries.

## Important APIs, types, and functions
- `InitCopPendingTable` creates the global `CopPendingMan`.
- `AddToCopPendingTable` inserts a full `MAXFIDS` fid array for a store ID.
- `AddPairToCopPendingTable` appends one fid to an existing store ID entry or creates a new entry.
- `cpent` stores the `ViceStoreId`, up to `MAXFIDS` mutated fids, creation time, dequeue-in-progress flag, and a magic value checked by the destructor.
- `coppendhashfn` hashes store IDs by host plus uniquifier.
- `cpman` owns the hash table, lock, and manager LWP. Its public methods add, remove, find-and-dequeue, and print entries.

## Control flow
Initialization constructs `cpman`, which starts `cpman_func` as an LWP. Mutations call `add` or `AddPairToCopPendingTable`; both serialize with the manager lock. `InternalCOP2` calls `findanddeq`, which marks an entry `deqing` while COP2 owns it, then later calls `remove` and deletes it. The manager loop wakes every `CPINTERVAL` seconds, removes the first expired non-dequeuing entry after `CPTIMEOUT`, optionally prints debug state, and sleeps again.

## State and persistence behavior
The pending table is process memory only. It is not recoverable across server restart, so it is a transient coordination structure for live COP completion. The authoritative persistent outcome is the vnode/volume version-vector state updated by COP2. Expired entries are dropped after 900 seconds, which can leave a late COP2 returning `ENOENT`.

## Dependencies and integration points
This file depends on LWP process creation/sleep, Coda locks, `ohashtab`, `ViceStoreId`, `ViceFid`, `NullFid`, logging, and `SrvDebugLevel`. It is used by repair and reintegration code in `codaproc.cc` and `codaproc2.cc`.

## Risks
`AddPairToCopPendingTable` assumes no operation exceeds `MAXFIDS`; overflow is a hard assertion. `find` returns a pointer after releasing the read lock, so callers that mutate the entry depend on table lifetime assumptions. The expiration daemon removes only the first entry returned by `objects.first()` per interval, so a large backlog can linger. Since the table is volatile, crashes between COP1 and COP2 require higher-level repair/resolution to reconcile state.

## Test signals
Exercise multi-fid operations, duplicate fids, COP2 dequeue/removal, late COP2 after expiration, concurrent add/findanddeq, and debug print paths. Useful signals include `ENOENT` from `InternalCOP2`, expired BusyQueue log messages, and assertions around `MAXFIDS` or `CPENTMAGIC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/coppend.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/coppend.h -->
# sources/distributed-fs/coda/coda-src/vice/coppend.h

## Purpose
`coppend.h` declares the pending-COP table interface shared by vice mutation code. It defines the entry and manager classes used to track which fids still need COP2 version-vector completion for a store ID.

## Important APIs, types, and functions
- `MAXFIDS` is the fixed maximum number of fids associated with one operation.
- `CPENTMAGIC` is the integrity marker checked by `cpent`.
- `class cpent` stores a store ID, fid array, entry timestamp, dequeue flag, and print helpers. Its internals are exposed to selected friends: table insertion, `InternalCOP2`, and `cpman`.
- `class cpman` owns the manager lock, LWP process ID, and object hash table. It exposes `add`, `remove`, `findanddeq`, and print helpers; construction/destruction and raw `find` are intentionally private/friend-mediated.
- `CopPendingMan`, `InitCopPendingTable`, `AddToCopPendingTable`, and `AddPairToCopPendingTable` are the global interface.

## Control flow
The header establishes a singleton style: server startup calls `InitCopPendingTable`, mutation paths add entries through the extern functions, and COP2 completion uses friend access from `InternalCOP2` to consume entries and inspect fids.

## State and persistence behavior
All state described by this header is in-memory and protected by a Coda `Lock`. The pending table records live coordination state, not durable state.

## Dependencies and integration points
The header includes C linkage dependencies for `stdio`, `lwp/lock.h`, `vice.h`, and `rpc2`, then includes `ohash.h` for the C++ hash table. It is consumed by `srv.cc`, `codaproc.cc`, `codaproc2.cc`, and `coppend.cc`.

## Risks
The fixed `MAXFIDS` bound is part of the ABI between operations and COP2. Adding operations that mutate more objects requires revisiting this structure. Friend-heavy encapsulation makes invariants implicit, and raw pointers are returned for entries managed by `cpman`.

## Test signals
Build coverage should catch include-order issues. Runtime COP tests should confirm all mutating operations add the right fids and COP2 consumes them exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/coppend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/printvrdb.cc -->
# sources/distributed-fs/coda/coda-src/vice/printvrdb.cc

## Purpose
`printvrdb.cc` is a small diagnostic utility that reads the on-disk Coda VRDB file and prints each volume replication entry in a textual form. It is explicitly described as "cheating" because it locally redefines the raw `vrent` disk layout instead of using the normal VRDB abstraction.

## Important APIs, types, and functions
- `struct vrent` mirrors the raw VRDB record: header, next pointer, key, replicated volume number, server count, per-server volume IDs, and server address.
- `ReadConfigFile` loads `server.conf`, resolves `vicedir`, and initializes vice path handling.
- `main` opens `db/VRDB`, reads fixed-size `vrent` records, byte-swaps numeric fields with `ntohl`, prints key/volume/server fields, closes the fd, and exits.
- `VRDB_PATH` and `VRDB_TEMP` are path macros based on `vice_config_path`, although only `VRDB_PATH` is used.

## Control flow
Startup loads configuration, then opens the VRDB read-only. Failure to open aborts with a message and `EXIT_FAILURE`. The main loop reads exactly one `vrent` at a time; only complete records are printed. There is no record validation beyond fixed-size reads.

## State and persistence behavior
The utility is read-only and does not mutate server state. It directly observes the persistent `db/VRDB` file under the configured vice directory.

## Dependencies and integration points
It depends on vice configuration helpers, `voltypes.h`, `vice_file.h`, and `vcrcommon.h` for volume and replication constants. Operationally it is a debugging/admin companion to the server's VRDB loading and checking code.

## Risks
The local `vrent` layout can drift from the real VRDB format, producing incorrect output or truncated reads. It assumes host/network byte order for selected fields and prints all `VSG_MEMBERS` slots regardless of `nServers`. It has no command-line override, locking, or corruption diagnostics.

## Test signals
Run against a known VRDB fixture and compare volume IDs/server slots to the normal VRDB tooling. Test missing file behavior and format drift by changing record sizes in fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/printvrdb.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/smon.cc -->
# sources/distributed-fs/coda/coda-src/vice/smon.cc

## Purpose
`smon.cc` implements the server monitor daemon that periodically reports vice server call statistics, resolution statistics, overflow events, and optional raw machine statistics to a Mond monitoring service.

## Important APIs, types, and functions
- `SmonInit` initializes this server's monitor identity (`SmonViceId`), overflow entry, RVM resolution queue, and init flag.
- `rvmrese` captures a snapshot of per-volume resolution stats and reports it with `SmonReportRVMResStats`.
- `smon_entry` stores an overflow event window and count.
- `CheckCallStat` reports RPC/callback/resolution/voldump call counts and raw statistics every `callReportInterval`.
- `CheckRVMResStat` drains queued resolution-stat events, or periodically snapshots `ResStatsList` into the queue.
- `CheckSOE` reports pending overflow state.
- `ValidateSmonHandle` rate-limits binding attempts, creates an RPC2 binding to `SmonHost:SmonPort`, and establishes a Mond connection.
- `CheckSmonResult` unbinds and resets the handle on report failure.
- `GetRawStatistics` returns platform-dependent kernel stats on old Mach paths and is effectively a no-op on other platforms.
- `SmonDaemon` is the LWP entry point that initializes and then runs the hourly reporting timer.

## Control flow
The server starts `SmonDaemon` as an LWP from `srv.cc`. The daemon sleeps using `IOMGR_Select`, and on timer expiry invokes call-stat, RVM-resolution-stat, and overflow checks. Each check first verifies initialization/enabled state and a valid Mond handle. Binding is retried no more often than `SmonBindInterval`; report failures drop the handle so future cycles can rebind.

## State and persistence behavior
Monitor state is in memory: `SmonHandle`, identity, pending overflow event, pending `RVMResList`, last bind attempt, and last report times. It reports live server counters and resolution stats but does not persist anything locally. Queued RVM resolution entries survive only until process exit.

## Dependencies and integration points
The file depends on RPC2, Mond client stubs, callback and resolution counter arrays, `ResStatsList`, LWP/IOMGR timing, host identity, and server globals `SmonHost`/`SmonPort` configured in `srv.cc`. It is optional telemetry: failed monitor reporting should not stop file serving.

## Risks
`SmonEnabled` defaults to 0 in this file and must be enabled elsewhere for reports to send. `CheckRVMResStat` uses `malloc` for C++-typed `rvmrese` objects containing `olink`, which is only safe if the type remains POD-like enough. The queued stats list is unbounded by explicit size, though comments assume one set at a time. The raw statistics path is obsolete and platform-specific. Reporting failures can cause repeated rebind churn every bind interval.

## Test signals
Use a fake Mond endpoint to validate bind, establish, report, failure, and rebind paths. Exercise call-stat intervals, resolution-stat queue drain, pending overflow reporting, disabled mode, and monitor host/port configuration from `srv.cc`. Logs from `ValidateSmonHandle`, `CheckRVMResStat`, and `CheckSmonResult` are useful diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/smon.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/srv.cc -->
# sources/distributed-fs/coda/coda-src/vice/srv.cc

## Purpose
`srv.cc` is the Coda vice file server main program. It owns process startup, configuration, RVM initialization, RPC2/SFTP setup, volume/callback/resolution subsystem initialization, LWP worker creation, request dispatch loops, shutdown, log rotation, database/key refresh, and runtime counters.

## Important APIs, types, and functions
- Global configuration/state includes authentication, resolution, SHA, polling/yield behavior, RVM devices, vnode cache sizes, callback intervals, worker counts, server host/IP, Smon host/port, counters, and `NullFid`.
- `main` is the full bootstrap sequence: read config, parse args/env, daemonize, initialize RVM/LWP/RPC/SFTP/directories/protection/volumes/callbacks/VRDB/COP/resolution, spawn LWPs, start the daemon parent, and wait for shutdown.
- `AuthLWP` handles new RPC2 connections on `SUBSYS_SRV`, executes the bind/connect request, and unbinds failed or suspicious clients.
- `ServerLWP` handles established client file-system requests, checks private client pointers and token expiry, updates client activity/counters, dispatches via `srv_ExecuteRequest`, and deletes/unbinds clients on fatal errors.
- `ResLWP` dispatches requests for the resolution subsystem through `resolution_ExecuteRequest`.
- `CallBackCheckLWP` periodically runs callback liveness checks and disk usage updates.
- `ShutDown`, `ViceTerminate`, and `SigTerm` coordinate graceful server shutdown and optional salvage-on-shutdown.
- `ViceUpdateDB` reloads protection database and auth keys when mtimes change, then checks VLDB/VRDB state.
- `PrintCounters` emits operation, transfer, RPC/SFTP, callback, host, RVM, and RDS statistics.
- `ReadConfigFile`, `ParseEnvVars`, and `ParseArgs` establish defaults and overrides.
- `InitServerKeys`, `SetupRVM`, `InitializeServerRVM`, `SetupRLimitAndSignals`, `SwapLog`, and `DaemonizeSrv` handle low-level process/runtime setup.

## Control flow
Startup begins with config defaults from `server.conf`, then command-line and environment overrides. The server validates RVM device settings, daemonizes unless disabled, sets signal handlers and resource limits, initializes recoverable memory and thread data, starts Coda core packages, reads auth/protection data, initializes RPC2/SFTP, directory and volume packages, callback state, VRDB, COP pending table, lock queue, resolution communication, and exports both file-server and resolution RPC subsystems. It then creates callback, auth, file-server, resolution, volume utility, resolution checker, and monitor LWPs. The main LWP signals readiness with `gogogo(parent)`, waits on `LWP_QWait`, and calls `ShutDown` when signaled.

Worker flow is split by connection stage. `AuthLWP` receives new connections, extracts peer info, rejects already-known private pointers, and dispatches the connect request. `ServerLWP` only accepts old connections, verifies `ClientEntry`, checks token expiration against packet receive time, tracks current operation/client, updates counters, dispatches generated RPC handlers, and cleans up clients marked for unbind. `ResLWP` handles old-or-new resolution subsystem RPCs independently.

## State and persistence behavior
Persistent server state is primarily RVM/RDS recoverable memory, volume/vnode metadata, protection/auth databases, VRDB/VLDB files, and server logs. `srv.cc` initializes RVM from configured log/data devices and loads the recoverable heap. It tracks nonpersistent process state such as counters, worker current-op arrays, debug levels, key/protection database mtimes, start time, and current connections. Shutdown may salvage volumes and writes a `SHUTDOWN` marker in the server directory.

## Dependencies and integration points
This file is the integration hub for RPC2, SFTP, codatunnel, LWP, IOMGR, RVM/RDS, auth2, protection lists, callbacks, directory cache, volume package, volutil, VRDB/VLDB, resolution communication, COP pending management, monitor daemon, daemonizer, config/env helpers, and generated RPC dispatch (`srv_ExecuteRequest`, `resolution_ExecuteRequest`).

## Risks
Startup ordering is fragile: many packages assume prior RVM, LWP, path, key, and volume initialization. Worker IDs are passed as addresses of the loop variable `i`, which is historically common but can race if LWP startup reads it after the loop advances. Signal handlers call functions that may not be async-signal-safe, though this is legacy LWP server code. `ParseEnvVars` assigns `MapPrivate` from `pathtiming` as the default argument, which looks like a copy/paste bug. Configuration conflicts around RVM mode are fatal, and missing keys intentionally assert. Request dispatch depends on private pointer integrity; stale or corrupted client state leads to unbinds.

## Test signals
High-value tests include startup with config/env/CLI combinations, RVM raw/UFS/VM modes, missing or rotated auth keys, token expiry, new and old RPC connection handling, worker unbind cleanup, shutdown/salvage, SIGHUP log rotation, SIGTERM graceful termination, VRDB/PDB reload via `ViceUpdateDB`, and counters under representative workloads. Operational signals are `SrvLog` startup ordering messages, worker request/failure logs, RVM/RDS statistics, RPC/SFTP counters, and `SHUTDOWN` marker creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/srv.cc -->
