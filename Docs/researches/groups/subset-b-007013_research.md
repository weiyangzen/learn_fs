# Research: subset-b-007013

Grouped research for Coda Venus files under `sources/distributed-fs/coda/coda-src/venus`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/fso_cfscalls1.cc -->
# sources/distributed-fs/coda/coda-src/venus/fso_cfscalls1.cc

Purpose: implements the first group of Venus `fsobj` CFS calls for disconnected/local mutation paths: remove, link, rename, mkdir, rmdir, symlink, and connected `SetVV`. The dominant pattern is a three-layer API: `Local*` routines mutate cached second-class state inside an RVM transaction, `Disconnected*` routines append a `repvol` CML log entry and optionally call the local mutator, and public methods choose timestamps/users and demote objects on failure.

Important APIs and flow: `LocalRemove`, `LocalLink`, `LocalRename`, `LocalMkdir`, `LocalRmdir`, and `LocalSymlink` update directory entries via `dir_Create`/`dir_Delete`, adjust `stat` fields, maintain link counts, kill unlinked objects, update cache stats, and touch hoard bindings. `Disconnected*` methods require a read-write replicated volume, allocate fids for new objects where needed, call `rv->Log*`, and use the `prepend` flag to avoid double-applying state during repair replay. `SetVV` is connected-only, calls `ViceSetVV` through multi-RPC for replicated volumes or a single connection for non-replicated volumes, collates COP2 responses, and then stores the new version vector locally.

State and persistence: all local filesystem-object mutations are wrapped with `Recov_BeginTrans`/`Recov_EndTrans` and `RVMLIB_REC_OBJECT`. New directory/symlink fsobjs are matriculated, referenced, prioritized, and have `CleanStat` initialized after local creation. Failed allocation paths kill uninitialized fsobjs and release them back to `FSDB`.

Dependencies and integration: depends on `repvol` CML logging, `FSDB`, cache accounting, directory helpers, Coda RPC2/Vice calls, mgroup/COP2 logic, hoard binding invalidation, and repair wrappers in `local_fso.cc`.

Risks and test signals: high-risk areas are link-count correctness, `prepend` repair replay semantics, cleanup after partial mkdir/symlink allocation, cross-parent rename updates including `..`, and COP2 error mapping in `SetVV`. Tests should exercise disconnected mutation replay, repair prepend paths, rename over files/directories, cache-stat deltas, non-RW volume errors, and replicated/non-replicated `SetVV` return handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/fso_cfscalls1.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/fso_cfscalls2.cc -->
# sources/distributed-fs/coda/coda-src/venus/fso_cfscalls2.cc

Purpose: implements the second group of `fsobj` CFS calls: open/close/sync, access checks, lookup/name traversal integration, readlink, pioctl-file execution, and VASTRO read-intent prefetch windows.

Important APIs and flow: `OpenPioctlFile` parses a virtual pioctl request from the object container, temporarily rebuilds `vproc` user context to resolve the target path and execute `ioctl`, truncates then rewrites the result file, and updates disk usage/valid-data metadata. `Open` fetches missing data for non-VASTROs, promotes lock when mutating, pins the object, manages openers/writers and `owriteq`, truncates through `SetAttr`, builds Unix-format directory containers with `dir_Rebuild`, and returns the backing `CacheFile`. `Sync` computes length/mtime from the container, updates cache accounting, stores to servers, and forbids `ERETRY`. `Release` and `Close` unwind pins, active segments, `owriteq`, pioctl objects, and last-writer store. `Access` handles pioctl ownership, read-only/fake/local/VASTRO restrictions, parent-directory ACL checks for non-directories, mode-bit filtering, and status refetch on stale ACLs. `Lookup` performs access, `@sys/@cpu` expansion, fake-root realm/pioctl synthesis, `FSDB->Get`, and mountpoint covering/crossing. `ReadIntent`/`ReadIntentFinish` reserve/fetch VASTRO holes and protect active segments.

State and persistence: writer state, file lengths, valid data, directory UDCF validity, pioctl container contents, active read segments, and disk-block accounting are the central state. RVM transactions protect queue flags, cache-file metadata, pioctl truncation/result metadata, and pioctl deletion.

Dependencies and integration: integrates kernel `venus_cnode` open paths, `vproc::namev`/`ioctl`, `FSDB`, access-right helpers, mountpoint covering, realms, VASTRO cache chunk APIs, workers, mariner logging macros, and repair/local flags.

Risks and test signals: risks include context restoration after pioctl, leaking opener/writer counts after truncate/open failure, stale Unix directory containers, parent-lock drop/reacquire in `Access`, fake-root fid synthesis, mountpoint recursion, and active-segment cleanup after failed read intent. Tests should cover pioctl round-trips, concurrent open/close writer paths, directory rebuild invalidation, ACL refresh, fake realm lookup, covered/uncovered mountpoints, and VASTRO allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/fso_cfscalls2.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/fso_daemon.cc -->
# sources/distributed-fs/coda/coda-src/venus/fso_daemon.cc

Purpose: implements the Venus filesystem-object daemon that periodically reclaims fsobjs and blocks, garbage-collects dying objects, recomputes priorities, and flushes volatile reference data to recoverable storage.

Important APIs and flow: `FSOD_Init` starts a `vproc` named `FSODaemon`. `FSODaemon` registers on `fsdaemon_sync`, wakes every five seconds or on explicit signal, runs `FSDB->GetDown` every 30 seconds, and calls `FSDB->FlushRefVec` every 90 seconds. `FSOD_ReclaimFSOs` forces the next reclaim by resetting `LastGetDown` and signaling the daemon. `fsdb::RecomputePriorities` recomputes priorities only when references changed or when forced. `GarbageCollect` walks `delq`, checks `DYING`, skips non-GC-able/busy objects, and calls `GC`. `GetDown` combines GC, priority recomputation, `ReclaimFsos`, and `ReclaimBlocks` against free margins. `FlushRefVec` persists `LastRef` with `rvmlib_set_range`.

State and persistence: daemon state is transient wake timing plus persistent FSDB metadata touched in transactions. `GetDown` must run inside a transaction; `FlushRefVec` opens its own transaction because ordinary object references do not persist `LastRef` immediately.

Dependencies and integration: depends on `vproc` scheduling, `FSDB`, replacement priority queues, object deletion queues, RVM recovery primitives, and worker/daemon registration.

Risks and test signals: risks are reclaim while objects remain pinned/open, stale priority calculations, negative free counts, long transactions during GC, and missed forced reclaim signals. Tests should stress cache overflow, busy dying objects, block and fso margin enforcement, priority aging after references, and daemon wake timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/fso_daemon.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/fso_dir.cc -->
# sources/distributed-fs/coda/coda-src/venus/fso_dir.cc

Purpose: provides `fsobj` directory data helpers over Coda's directory-handle (`DH_*`) library, plus synchronization of Coda-format directory data to Unix-format container files used by the kernel.

Important APIs and flow: `dir_Rebuild` validates/prints corrupt Coda directory handles, converts them to Unix directory format with `DH_Convert`, and marks the UDCF valid. `dir_Create` and `dir_Delete` mutate Coda-format entries, invalidate the Unix-format container, and update directory data cache stats by block delta. `clear_dir_container_entry` patches the Unix-format directory container after unlink to avoid `rm -rf` loops caused by session semantics. `dir_MakeDir` allocates recoverable `VenusDirData`, initializes `.`/`..`, and updates `stat.Length`. Lookup helpers map names to same-volume `VenusFid`s, reverse-map fids to names, check emptiness/parentage, translate all references from an old fid to a new fid, and print debug state.

State and persistence: `data.dir`, `data.dir->dh`, `udcf`, `udcfvalid`, `stat.Length`, and directory cache stats are the central state. Mutation callers are expected to be in a transaction; the functions assert full data availability and use recoverable allocation for new directory data.

Dependencies and integration: depends on `codadir`/`DH_*`, `CacheFile`, Coda fid conversion helpers, `FSDB` cache stats, local repair fid translation, and open-path directory rebuild logic in `fso_cfscalls2.cc`.

Risks and test signals: risks include corrupt directory handles, cross-volume translation misuse, `clear_dir_container_entry` offset assumptions, stale UDCF data, and block-accounting signs on deletion. Tests should cover create/delete/rebuild sequences, lookup flags/case sensitivity, empty directory checks, fid translation for local repair, corrupt-dir diagnostics, and repeated unlink while a directory is open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/fso_dir.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/hdb.cc -->
# sources/distributed-fs/coda/coda-src/venus/hdb.cc

Purpose: implements the Venus hoard database (HDB), which records user hoard entries, validates path bindings into cached fsobjs, performs priority-ordered status and data hoard walks, handles meta-expansion of directory entries, and reports availability.

Important APIs and flow: `HDB_Init` creates or rehydrates the recoverable `hdb`, resets transient state, scans entries, and starts `HDBDaemon`. Public commands include `Add`, `Delete`, `Clear`, `List`, `Walk`, `Verify`, `Enable`, `Disable`, and `ResetUser`. `Walk` recomputes FSDB priorities, runs `StatusWalk` to validate name contexts and callbacks, then `DataWalk` to prefetch hoardable dataless objects. `hdbent` is the persistent table entry keyed by `<vid, realm, name>` with owner, priority, and meta-expansion flags. `namectxt` is transient binding state: it tracks a path under a root fid, its owner/priority, expansion bindings to fsobjs, children from meta-expansion, and state `PeValid`, `PeSuspect`, `PeIndigent`, or `PeInconsistent`. `CheckExpansion` drives `vproc::namev` with `u_nc` so successful component lookups call `CheckComponent`; `MetaExpand` enumerates directories to create/retain child name contexts.

State and persistence: `hdb` and `hdbent` storage is recoverable RVM; `namectxt`, priority queues, child lists, state counters, tally state, and Mariner progress are transient. Add/delete/clear use RVM transactions; demand walk time is persistent. Binding lists attach HDB contexts to fsobjs and are discarded on context destruction.

Dependencies and integration: depends on `FSDB`, `VDB`, `REALMDB`, `vproc::namev`, directory enumeration, Coda fid/version helpers, cache replacement priorities, tally reporting, Mariner progress logging, users/authorization, and RVM recovery.

Risks and test signals: notable risks include iterator invalidation after yields/prefetches, the apparent bug in `ValidateCacheStatus` adding to the pointer `statusBytesFetched` instead of `*statusBytesFetched`, state-counter imbalance, meta-expanded child lifetime, ENOSPC clean-up mode, stale bindings after fsobj replacement, and large clear/list transactions. Tests should cover add/delete authorization, status walk retries, ENOSPC indigent transitions, inconsistent path handling, meta-expansion after directory version changes, data walk progress/tally output, and recovery restart of HDB entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/hdb.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/hdb.h -->
# sources/distributed-fs/coda/coda-src/venus/hdb.h

Purpose: declares the hoard database public pioctl messages, daemon request enum, persistent `hdb`/`hdbent` classes, transient `namectxt` path-expansion model, iterators, constants, and helper macros.

Important APIs and types: external message structs describe add/delete/clear/list/walk/verify commands. Hoard priorities range from `H_MIN_PRI` to `H_MAX_PRI`, and attributes `H_INHERIT`, `H_CHILDREN`, and `H_DESCENDENTS` control directory meta-expansion. `hdb` owns the recoverable hash table, freelist, transient priority queue, advice counters, and command methods. `hdbent` stores key, uid, priority, expansion flags, and one root `namectxt`. `namectxt` stores root directory fid, path, uid, priority, state, in-use/death/demote flags, expansion bindings, child meta-expansions, version state of expanded directories, parent/child links, and priority-queue/free-list handles. `hdb_iterator` filters by uid or key.

State and persistence: the header explicitly separates recoverable members from transient members with comments. `hdb` and `hdbent` are RVM-managed; `namectxt` instances are VM-only and rebuilt in `ResetTransient`.

Dependencies and integration: depends on Coda/Vice types, util containers (`rec_ohash`, `rec_olist`, `bstree`, `dlist`), FSDB/fsobj declarations, recovery annotations, daemon entry points, and `struct uarea` for request authorization context.

Risks and test signals: risks are ABI drift for pioctl message structs, invalid state transitions not caught until `CHOKE`, memory-ownership confusion for `namectxt::path` because root contexts borrow `hdbent::name` while meta contexts allocate, and mismatch between persistent and transient initialization. Tests should compile both Venus and hoard-tool users, exercise restart reconstruction, verify priority ordering, and validate `PRINT_*` macros for diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/hdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/hdb_daemon.cc -->
# sources/distributed-fs/coda/coda-src/venus/hdb_daemon.cc

Purpose: implements the HDB daemon that serializes hoard pioctl requests and runs periodic hoard walks.

Important APIs and flow: `HDBD_Init` starts a priority-adjusted `HDBDaemon` vproc. `HDBD_GetNextHoardWalkTime` reports seconds until the next periodic walk. `HDBDaemon` registers a five-minute wake interval, skips the initial startup walk, handles queued requests before periodic work, runs `HDB->Walk` every ten minutes when `PeriodicWalksAllowed` is set, handles requests again afterward, logs elapsed time, and advances its sequence number. `HDBD_Request` enforces `AuthorizedUser`, builds a stack `hdbd_msg`, appends it to `hdbd_msgq`, signals the daemon, waits on the message wait block, and returns the result. `HDBD_HandleRequests` drains the queue and dispatches to the corresponding `HDB` method.

State and persistence: the daemon state is transient: last walk time, synchronization byte, and in-memory request queue. Persistence is delegated to `hdb` methods, which open their own recovery transactions where needed.

Dependencies and integration: depends on `vproc` scheduling, LWP priorities, user authorization, HDB command APIs, and the global periodic-walk flag defined in `hdb.cc`.

Risks and test signals: risks include stack-address request messages that require synchronous completion, no explicit queue lock beyond cooperative vproc assumptions, long blocking hoard walks delaying request replies, root/authorized user policy changes, and inaccurate next-walk reporting before daemon initialization. Tests should cover unauthorized requests, each dispatch type, request/walk interleaving, periodic enable/disable, and daemon wake-up behavior while a demand walk is running.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/hdb_daemon.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/local.h -->
# sources/distributed-fs/coda/coda-src/venus/local.h

Purpose: declares local-repair support utilities, lightweight list-entry wrappers, mutation/repair bit constants, and an object-aware assertion macro used by Venus local repair code.

Important APIs and types: exported repair helpers include `DiscardLocalMutation`, `PreserveLocalMutation`, `PreserveAllLocalMutation`, and `ListCML`. `vdirent` stores a directory-entry fid/name pair, `optent` stores an `fsobj *` plus tag, and `vptent` stores a `repvol *`; each has iterator wrappers over `dlist_iterator`. Mutation check flags distinguish missing target/parent, ACL failure, version-vector conflict, name/name conflict, and remove/update conflict. Repair flags encode failure, overwrite, and force-remove actions. `REP_INIT_TID` initializes local repair transaction id generation.

State and persistence: the header itself owns no state, but its classes are list nodes used to accumulate transient repair work and its constants drive persistent CML repair flags and transaction ids elsewhere.

Dependencies and integration: depends on `dlist`, `rec_dlist`, `fso`, `venusvol`, and LWP lock declarations. It is included by local CML, fake-object, repair, fsobj, and volume repair modules.

Risks and test signals: risks are mismatched bit interpretation between `CheckRepair` and `DoRepair`, raw pointer list entries with unclear ownership, and assertion behavior that prints object state before aborting. Tests should verify every mutation flag maps to repair-tool messages and that iterator wrappers preserve list traversal semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/local_cml.cc -->
# sources/distributed-fs/coda/coda-src/venus/local_cml.cc

Purpose: implements local repair logic for CML entries: diagnosing whether a disconnected mutation can be reintegrated against current server state, replaying approved repair operations, formatting local operation messages, and exposing fid/version metadata.

Important APIs and flow: `GetGlobalReplica` finds a consistent server replica for a replicated fid. `CheckRepair_GetObjects`, `CheckRepair_CheckAccess`, `CheckRepair_CheckVVConflict`, and `CheckRepair_CheckNameConflict` are shared validation steps. `cmlent::CheckRepair` switches by CML opcode, fetches local/global operands, verifies ACLs, checks semantic constraints, and sets mutation/repair codes such as overwrite or force-remove. `cmlent::DoRepair` replays the chosen operation using `Repair*` wrappers; stores copy local cache data to each replica then call `RepairStore`, while create/mkdir/symlink/link/remove/rmdir/rename call the corresponding disconnected repair wrappers with prepend semantics. `GetLocalOpMsg`, `GetVVandFids`, `GetAllFids`, `SetRepairFlag`, `SetTid`, `ContainLocalFid`, and `ClientModifyLog::HaveElements` provide diagnostics and metadata.

State and persistence: CML entries carry opcodes, fids, stored version vectors, names, repair flags, expansion counts, and transaction ids. Mutations to repair flags and tids are RVM-protected. Repair replay relies on local/global fsobjs and may create new logged mutations with `prepend=1`.

Dependencies and integration: depends on `FSDB`, `VDB`, replicated volumes, CML data structures, version-vector comparison, ACL checks, path recovery, repair wrappers in `local_fso.cc`, and local fake fid helpers.

Risks and test signals: risks include fragile object lifetime in `GetGlobalReplica` after `FSDB->Put` then `Find`, several suspicious field references (`CML_Utimes_OP` uses `u.u_chown.Fid`; mkdir repair starts with `u.u_link.PFid`), mismatched global/local path formatting, partial multi-replica store repair, and repair replay that assumes split renames. Tests should cover every opcode in both check and repair phases, ACL failures, version conflicts, name conflicts, missing server targets, local fake fids, transaction-id grouping, and multi-server store failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/local_cml.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/local_fake.cc -->
# sources/distributed-fs/coda/coda-src/venus/local_fake.cc

Purpose: implements expanded repair views for conflicts by replacing an object or mountpoint with a fake directory in the local Repair volume containing mountlinks to `_localcache` and individual server replicas.

Important APIs and flow: `fsobj::ExpandObject` rejects already-expanded/local/non-replicated objects, detaches the object or mount root from its parent, creates a fake repair directory, inserts a local-cache mountlink, inserts one mountlink per replica server, replaces the original parent entry or mountlink with a fake mountlink to the repair directory, marks involved objects local/modified/expanded, increments bound CML expansion counts, pins the local object, and purges kernel cache entries. `volent::NewFakeDirObj` and `NewFakeMountLinkObj` allocate fake fids, initialize directory/symlink metadata, mark objects local, and matriculate them. `SetMtLinkContents` formats Coda mountlink target strings. `CollapseObject` normalizes calls from several possible expanded-view objects, finds `_localcache`, detaches fake mountlinks, restores the original object or mountlink, clears flags, decrements CML expansion counts, kills the fake tree, and releases references. `IsToBeRepaired`, `WhoIsLastAuthor`, `ExpandCMLEntries`, `CollapseCMLEntries`, and `HasExpandedCMLEntries` inspect/update CML bindings.

State and persistence: fake fsobjs, directory entries, mountlink symlink data, parent/child pointers, mountpoint root links, flags, and CML expansion counters are modified under RVM transactions. Kernel name cache purges make expanded/collapsed views visible.

Dependencies and integration: depends on replicated volumes, `VDB`, `REALMDB`, `FSDB`, fake fid generation, directory helpers, mountpoint cover/uncover logic, CML bindings, server host/vid lists, and worker/user context for collapse lookup.

Risks and test signals: risks include reference leaks around `FSO_HOLD`, parent/mountpoint restoration after crashes, recursive expansion prevention, fake symlink formatting, collapse from any view node, and CML expansion counts under nested repair views. Tests should expand/collapse root and non-root objects, directories and files, hidden localcache cases, replica mountlinks, crash/restart recovery, and kernel purge visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/local_fake.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/local_fso.cc -->
# sources/distributed-fs/coda/coda-src/venus/local_fso.cc

Purpose: provides local-repair related `fsobj` helpers for display names, local-object flags, CML lookup by transaction id, repair-mode mutation wrappers, and local version-vector assignment.

Important APIs and flow: `SetComp` replaces the recoverable component string, and `GetComp` returns it or a fid string fallback. `SetLocalObj`/`UnsetLocalObj` toggle the local flag. `FinalCmlent` scans `mle_bindings` to return the last CML entry for an IOT transaction id. `RepairStore`, `RepairSetAttr`, `RepairCreate`, `RepairRemove`, `RepairLink`, `RepairRename`, `RepairMkdir`, `RepairRmdir`, and `RepairSymlink` capture current user/time and call the corresponding disconnected operation with `prepend=1`, meaning the repair path logs the action without applying second-class local state again. `SetLocalVV` directly writes `stat.VV`.

State and persistence: component strings, local flags, version vectors, and repair log side effects are recoverable. The repair wrappers rely on transactions opened by the disconnected methods they call.

Dependencies and integration: depends on CML bindings, `Disconnected*` mutation methods from CFS call files, `VprocSelf` user context, RVM macros, and repair replay in `local_cml.cc`.

Risks and test signals: risks include component string ownership, asserting when no final CML entry exists, misuse of repair wrappers outside already-updated local state, and direct local VV updates that bypass server validation. Tests should cover name changes, local flag transitions, final CML lookup with multiple tids, each repair wrapper’s prepend behavior, and local VV repair updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/local_fso.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/local_repair.cc -->
# sources/distributed-fs/coda/coda-src/venus/local_repair.cc

Purpose: implements user-facing local mutation repair commands over a volume's `ClientModifyLog`: check the head mutation, discard it, preserve/reintegrate one mutation, preserve all possible mutations, and list CML entries.

Important APIs and flow: `ClientModifyLog::CheckCMLHead` formats the head CML entry and its `CheckRepair` diagnostic. `DiscardLocalMutation` validates that the head exists and is marked for repair, cancels freezes, calls `m->cancel()` in a recovery transaction, and reports success/failure. `reintvol::DiscardAllLocalMutation` is intentionally disabled in favor of `purgeml`. `PreserveLocalMutation` checks repair feasibility, calls `DoRepair`, and cancels the local CML entry after successful reintegration. `PreserveAllLocalMutation` iterates commit order until it hits an IOT transaction entry or an unrecoverable conflict, preserving entries that repair cleanly or have non-fatal check codes. `ListCML` writes all CML entries.

State and persistence: CML cancellation and freeze toggling are recoverable. User-visible messages are transient but depend on persistent CML opcodes, flags, and tids.

Dependencies and integration: depends on `cmlent::CheckRepair`, `DoRepair`, `GetLocalOpMsg`, `cancelFreezes`, `cml_iterator`, `vproc` repair context, and `reintvol` command dispatch.

Risks and test signals: risks include TODO dependency checks before discard, preserving entries with non-zero mutation codes, interaction with transaction-grouped CML entries, message buffer sizing, and proper freeze cancellation around `cancel`. Tests should cover empty logs, non-conflicting head discard rejection, discard success, preserve success/failure per opcode, preserve-all stopping at tids, and list output order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/local_repair.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/local_vol.cc -->
# sources/distributed-fs/coda/coda-src/venus/local_vol.cc

Purpose: provides small local-repair helpers on `reintvol` for abort accounting, unrepaired-CML detection, and repair transaction id generation.

Important APIs and flow: `IncAbort` increments CML abort state for a tid and clears `CML.owner` when the log becomes empty. `ContainUnrepairedCML` walks the CML in commit order and returns true if any entry is marked `IsToBeRepaired`. `GetReintId` increments the recoverable `reint_id_gen` and returns the new id.

State and persistence: CML abort state and owner live in the volume's modify log; `reint_id_gen` is recoverable and updated under an RVM transaction. The unrepaired scan is read-only.

Dependencies and integration: depends on `ClientModifyLog`, `cml_iterator`, `cmlent::IsToBeRepaired`, recovery macros, and `venusvol` reint volume state.

Risks and test signals: risks are owner clearing when abort removes the last entry, transaction id wraparound/uniqueness over restart, and scans racing with log mutation in cooperative scheduling. Tests should cover abort of last and non-last entries, unrepaired CML detection, and persistent monotonic ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/local_vol.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/mariner.cc -->
# sources/distributed-fs/coda/coda-src/venus/mariner.cc

Purpose: implements the Mariner monitoring/control facility: Unix/TCP listener setup, per-client `mariner` vprocs, async queued writes, fetch/path/volume-state reporting, diagnostic commands, and optional 9PFS handoff.

Important APIs and flow: `MarinerInit` creates a world-accessible Unix socket when available and optional TCP listeners for service `venus`, then registers MUX callbacks. `MarinerMux` accepts clients, enforces `MaxMariners`, makes sockets non-blocking, and constructs `mariner`. `MarinerLog`, `MarinerReport`, and `MarinerReportVolState` broadcast to clients that enabled fetch logging, path reports, or volume-state reports. Each `mariner` starts a writer LWP, reads command lines with `AwaitRequest`, detects Plan 9 protocol magic and transfers control to `plan9server`, parses commands in `main`, and supports debug toggles, RPC2 tracing, COP mode changes, report subscriptions, fd/path/fid/rpc2 stats, and `VenusPrint`. Non-blocking writes are queued with a fixed queue; overflow drops messages and later reports the drop count.

State and persistence: Mariner state is transient per connection: fd, flags, uid filter, output queue, writer process, command buffer, and optional 9P server. It does not write recoverable metadata.

Dependencies and integration: depends on sockets, IOMGR/LWP, RPC2/SFTP stats, `vproc` path/fid lookup, FSDB/VDB/REALMDB, `VenusPrint`, volume-state reporting, and 9PFS integration.

Risks and test signals: risks include unsynchronized `nmariners`/queue updates, socket permissions, queue overflow semantics, command parsing truncation, TCP exposure, cleanup of writer LWP on disconnect, and 9P magic detection inside line-oriented reads. Tests should connect over Unix/TCP, toggle each subscription, verify dropped-message reporting, run `pathstat`/`fidstat`, exercise disconnect while queued writes exist, and validate 9P handoff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/mariner.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/mariner.h -->
# sources/distributed-fs/coda/coda-src/venus/mariner.h

Purpose: declares the Mariner facility public functions and the `mariner` vproc class used for monitoring/control clients.

Important APIs and types: public functions initialize listeners, accept mux callbacks, broadcast fetch logs/path reports/volume state, and print active mariners. `qentry` stores queued output buffers. `mariner` inherits `vproc`, owns a writer LWP, fixed output queue, state flags for logging/reporting/volume-state subscriptions, uid filter, socket fd, command buffer, optional `plan9server`, and helpers for LWP-aware non-blocking reads/writes, request parsing, resignation, path/fid/rpc2 stats, and queued writing. `mariner_iterator` filters `vproc_iterator` to active Mariner vprocs.

State and persistence: all declared state is transient connection state; no RVM persistence is involved.

Dependencies and integration: depends on `vproc`, Venus fids, volume flags, Plan 9 server forward declaration, and C stdio. Friend declarations expose internals to accept callbacks, broadcast functions, kernel replace handling, and queue writer glue.

Risks and test signals: risks include private ownership/lifetime of queued buffers, friend-heavy access, fixed queue length, and vproc/thread lifecycle coupling. Tests should compile all friend users, iterate active clients, verify subscription flags, and confirm queue writer shutdown through EOF sentinel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/mariner.h -->
