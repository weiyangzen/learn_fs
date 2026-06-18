# Research Group subset-b-007020

This grouped research report covers Coda volume-layer and volume-utility files. Each section is bounded by reconciliation markers so the guard can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/cvnode.h -->
# sources/distributed-fs/coda/coda-src/vol/cvnode.h

Purpose: defines the core vnode in-memory and RVM-persistent layout used by the Coda volume package. It separates vnode type (`vFile`, `vDirectory`, `vSymlink`) from vnode class (`vLarge` for directories and `vSmall` for files/symlinks) and provides the arithmetic that maps Coda vnode ids to class-local bit positions.

Important APIs/types/functions: `VnodeDiskObject` is the recoverable representation, including type, copy-on-write flag, mode bits, link count, data length, uniquifier, container inode or directory RVM pointer, version vector, parent fid, advisory `ViceLock`, server modify time, recoverable list link, and optional resolution log. `Vnode` wraps that disk object with VM hash/LRU links, cache state, lock ownership, directory-cache handle, SHA cache, and dirty/delete flags. Exported APIs include `VGetVnode`, `VPutVnode`, `VFlushVnode`, `VAllocFid`, `VAllocVnode`, `ObjectExists`, directory handle helpers, copy-on-write support, fid conversion helpers, and debug printing.

Control flow/state: most implementation lives in companion `.cc` files. Callers allocate or fetch vnodes through the volume package, mutate the in-memory `Vnode::disk` payload, and write it back through RVM-aware routines declared here. Directory ACL storage is modeled as data appended beyond the small vnode disk object, which makes size constants and class checks critical.

Persistence/dependencies/integration: depends on LWP locks, RPC errors, `codadir`, ACL and protection server types, version-vector and inconsistency structures, recoverable small/double lists, `vicelock.h`, and lock-keeper state. Risks are ABI/layout drift (`SIZEOF_SMALLDISKVNODE`, `SIZEOF_LARGEDISKVNODE`), misuse of large-vnode ACL macros on small vnodes, stale directory handles, and invalid class/id conversions. Test signals include vnode create/delete, directory ACL round trips, copy-on-write directories, fid allocation stride cases, and salvage after dirty or deleted vnodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/cvnode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/dirvnode.cc -->
# sources/distributed-fs/coda/coda-src/vol/dirvnode.cc

Purpose: manages directory vnode interaction with the directory cache and recoverable directory inode pages. It keeps VM directory handles synchronized with RVM-backed `PDirInode` state and supports directory copy-on-write.

Important APIs: `VN_DCommit` commits dirty directory cache pages into RVM and updates `vnp->disk.node.dirNode`; for deleted directories it nulls the pointer and decrements the previous directory inode. `VN_DAbort` frees VM directory data and drops new uncommitted handles. `VN_SetDirHandle`, `VN_PutDirHandle`, and `VN_DropDirHandle` bridge a vnode to the directory cache. `VN_CopyOnWrite` detaches a cloned directory from its old RVM inode, either marking the existing cache entry copy-on-write or cloning VM pages when other users still reference the old entry.

Control flow/state: callers set a handle before operating on directory contents. On transaction commit, dirty VM pages are copied into RVM with `DI_DhToDi`, rehashed, and installed into the vnode disk object. On abort or vnode eviction, the code frees or drops cache entries depending on whether the directory ever acquired an RVM inode.

Dependencies/integration: integrates `codadir` directory cache primitives with `Vnode` dirty/delete state and RVM transactions from the vnode/volume layer. Risks include reference-count mismatches because comments explicitly say `VN_SetDirHandle` calls are not perfectly paired with puts, and copy-on-write correctness depends on `DC_Count - dh_refc`. Test signals: create/abort directory, modify/commit directory, clone a directory with and without shared cache users, delete cloned directories, and assert no leaked or double-dropped `PDCEntry` references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/dirvnode.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/dumpcamstorage.cc -->
# sources/distributed-fs/coda/coda-src/vol/dumpcamstorage.cc

Purpose: debugging/introspection code for dumping Coda recoverable storage (`SRV_RVM`) volume and vnode structures to stdout. It is not a mutation path; it exposes internal RVM state for diagnostics.

Important APIs: `dump_storage(level, tag)` prints global initialization, first volume slots, small/large vnode free-list entries, vnode free-list indexes, and `MaxVolId` when `VolDebugLevel` allows it. `print_VolHead`, `print_VolData`, `print_VnodeDiskObject`, and `print_VolumeDiskData` recursively render volume headers, `VolumeData`, recoverable vnode list contents, and `VolumeDiskData` fields. `PrintCamVnode`, `PrintCamDiskData`, and `PrintCamVolume` are level-gated wrappers used by recovery/volume code.

Control flow/state: the dump traverses `SRV_RVM(VolumeList[i])` and each recoverable `rec_smolist`, recovering containing `VnodeDiskObject` values with `strbase`. It calls `ExtractVnode` for targeted vnode display, so it exercises the same lookup path as index/recovery code.

Dependencies/integration: depends on `cvnode.h`, `volume.h`, VLDB/partition/vutil/fssync/index/recovery/cam globals, recoverable lists, and version-vector printing. Risks include hard-coded volume/free-list traversal limits in `dump_storage`, direct stdout output, and dereferencing corrupt RVM pointers during failure diagnosis. Test signals: enable high `VolDebugLevel`, create volumes with small/large vnodes, verify printed fields match RVM state, and run after salvage failures to ensure diagnostics do not crash on missing lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/dumpcamstorage.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/fssync.cc -->
# sources/distributed-fs/coda/coda-src/vol/fssync.cc

Purpose: coordinates volume utilities with the running file server. In this version it is an in-process LWP/timer and shared table mechanism, not an external socket listener.

Important APIs: `FSYNC_fsInit` starts the `FSYNC_sync` LWP, which waits for volume initialization and periodically expires relocation entries. `FSYNC_clientInit` and `FSYNC_clientFinis` register/unregister utility LWPs. `FSYNC_askfs(volume, command, reason)` handles `FSYNC_ON`, `FSYNC_OFF`, `FSYNC_NEEDVOLUME`, and `FSYNC_MOVEVOLUME`. `FSYNC_CheckRelocationSite` returns a temporary moved-to server address.

Control flow/state: registered utilities get a row in `OfflineVolumes[MAXUTILITIES][MAXOFFLINEVOLUMES]`. `FSYNC_NEEDVOLUME` may offline a volume, leave read-only/dump/clone cases online, or set `VBUSY`; `FSYNC_ON` removes it from the offline list and reattaches it for update. Move commands add relocation entries and mark attached volumes `VMOVED`. Relocations age out after `REDIRECT_TIME`.

Dependencies/integration: uses LWP, IOMGR timers, volume attach/update/offline operations, and volume status fields. It is called from `VAttachVolumeById`, `VOffline`, `VDetachVolume`, and lookup/location paths. Risks include fixed utility/offline/relocation table sizes, assertion on unknown utility id, limited locking around global arrays, and semantic overload of the `reason` field for move target. Test signals: utility attach/detach while file server serves a volume, clone/dump leave-online cases, relocation expiry, MAXUTILITIES exhaustion, and failed attach cleanup path returning a volume online.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/fssync.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/fssync.h -->
# sources/distributed-fs/coda/coda-src/vol/fssync.h

Purpose: public command and API definitions for file-server/volume-utility synchronization.

Important definitions: commands are `FSYNC_ON`, `FSYNC_OFF`, `FSYNC_NEEDVOLUME`, and `FSYNC_MOVEVOLUME`. Reasons include salvage, move, and operator action. Replies are byte-sized `FSYNC_DENIED` or `FSYNC_OK`. Exported APIs initialize the file-server side, register utility clients, finalize clients, issue synchronization requests, and check temporary relocation information.

Control flow/state: the header constrains the protocol surface used by volume utilities and the volume package. `FSYNC_NEEDVOLUME` is intentionally mode-sensitive: callers pass volume attachment mode in the `reason` position. `FSYNC_CheckRelocationSite` is marked with `WARN_SINGLE_HOMING`, signaling that single-server assumptions may be relevant.

Dependencies/integration: depends on Coda transaction annotations and deprecation helpers; uses `VolumeId` from included volume/common headers. Risks are protocol ambiguity from integer commands/reasons and compatibility dependence on exact numeric constants. Test signals are compile-time coverage in utilities and runtime tests for every command/reason pair.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/fssync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/index.cc -->
# sources/distributed-fs/coda/coda-src/vol/index.cc

Purpose: wraps RVM-backed vnode lists as an index-like C++ abstraction for callers that expect volume/vnode index operations.

Important APIs: `vindex` stores volume id, recoverable volume index, vnode class, device, and object-size metadata. `elts()` returns active slot count, `vnodes()` returns allocated vnode count, `IsEmpty()` checks whether a class-local slot's recoverable list is empty, `get`/`oget` call `ExtractVnode`, and `put`/`oput` call `ReplaceVnode`. `vindex_iterator` iterates through all non-null vnodes in a class by traversing `rec_smolist` arrays.

Control flow/state: constructor either accepts a supplied recoverable volume index or looks one up with `HashLookup`. Iteration selects small or large vnode-list arrays, then advances list-by-list, skipping `vNull` entries and copying the class-appropriate disk-object size.

Dependencies/integration: integrates recovery routines (`ExtractVnode`, `ReplaceVnode`, `ActiveVnodes`, `AllocatedVnodes`) with volume bitmap construction, dump/backup tooling, and vnode cache initialization. Risks include unchecked constructor failure state after a failed `HashLookup`, array bounds assumptions inherited from recovery functions, and needing large-vnode buffers for directory entries. Test signals: iterate sparse small/large lists, confirm `IsEmpty` for multi-uniquifier slots, replace/delete through `put`, and build a volume bitmap from iterator output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/index.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/index.h -->
# sources/distributed-fs/coda/coda-src/vol/index.h

Purpose: declares the recoverable vnode index abstraction used by the volume layer.

Important types/APIs: `vindex` exposes slot counts, allocated counts, empty checks, id-based and offset-based get/put operations. `vindex_iterator` exposes `operator()(VnodeDiskObject *)`, returning the current recoverable vnode index or `-1` at end. Write operations are annotated as requiring a transaction.

Control flow/state: `vindex` is a lightweight handle over a `VolumeId` and vnode class rather than owning storage. `vindex_iterator` owns a `rec_smolist_iterator` and walks one recoverable slot list at a time.

Dependencies/integration: depends on `VolumeId`, `Device`, `VnodeId`, `Unique_t`, `VnodeDiskObject`, `bit32`, and recoverable-list classes from the volume headers. Risks include public declaration of `operator=` without implementation, implicit default constructor values of `-1`, and caller responsibility for buffer size. Test signals: compile users in volume/dump/salvage paths and verify transaction enforcement around `put`/`oput`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/index.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/lockqueue.cc -->
# sources/distributed-fs/coda/coda-src/vol/lockqueue.cc

Purpose: implements a volume lock queue manager that times out stale exclusive volume locks and forces unlocks.

Important APIs/classes: global `LockQueueMan`, `InitLockQueue`, `ForceUnlockVol`, `lqman`, `lq_iterator`, and `lqent`. `lqman::func` runs as an LWP, initializes RVM thread data, tags itself as a volume utility, scans queued lock entries every `LQINTERVAL`, and unlocks entries older than `LQTIMEOUT` unless they are being dequeued.

Control flow/state: exclusive locks obtained through `GetVolObj` can enqueue an `lqent`. On timeout, the manager removes the entry, calls `ForceUnlockVol`, which gets the volume without a lock and then calls `PutVolObj` as an exclusive unlock. `findanddeq` marks an entry `deqing` so the manager will not race normal unlock cleanup.

Dependencies/integration: depends on LWP, RPC2 types, RVM per-thread setup, `GetVolObj`/`PutVolObj`, `VolumeId`, and `dlist`. Risks include global manager lifetime, fixed timeout policy, forced unlock assumptions, use of write locks around list mutation, and possible stale `lqent` if callers forget `Dequeue`. Test signals: acquire/release exclusive lock with queue entry, timeout unlock, deq race, manager startup/shutdown, and lock contention with shared locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/lockqueue.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/lockqueue.h -->
# sources/distributed-fs/coda/coda-src/vol/lockqueue.h

Purpose: declares the volume lock queue facility and maps volume lock constants onto Coda/LWP lock levels.

Important APIs/classes: `VOL_NO_LOCK`, `VOL_SHARED_LOCK`, and `VOL_EXCL_LOCK`; `ForceUnlockVol`; `lqman` queue manager; `lq_iterator`; and private `lqent` queue entries. `lqent` grants friendship to volume object helpers and RPC lock/unlock entry points, allowing those paths to manipulate its private volume id, timestamp, and dequeue flag.

Control flow/state: consumers create an `lqman`, add `lqent` objects for lock holders, search or mark entries during unlock, and print queue contents. `lqman::func` is private and invoked through `LQman_init`.

Dependencies/integration: depends on LWP locks, RPC2, `vice.h`, and `dlist`. The lock queue is an integration point between file-server RPC lock APIs and lower-level volume object locking. Risks are friend-heavy encapsulation, global `LockQueueMan`, and reliance on C-style lock constants. Test signals: compile RPC lock/unlock users, queue print output, timeout manager behavior, and lock-level mapping in `GetVolObj`/`PutVolObj`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/lockqueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/objlist.c -->
# sources/distributed-fs/coda/coda-src/vol/objlist.c

Purpose: appears intended as a C-style object list parallel to `vlist`, tracking per-fid objects and reintegration side state. As checked in, the file contains obvious type and identifier inconsistencies and likely does not compile in normal builds.

Important APIs: intended functions are `OBJ_Cmp`, `OBJ_NewList`, `OBJ_FreeList`, `OBJ_Find`, `OBJ_GetFree`, `OBJ_Free`, and `OBJ_Add`. They allocate list heads, search by `ViceFid`, allocate per-object state, and initialize file or directory side fields.

Control flow/state: expected flow is create list, find or add a `fsobj`, attach a vnode pointer/log lists/inode cleanup fields, and free only once the object is detached from any list and has no vnode pointer. However the implementation references `fsobj`, `obj`, `fsobjlist`, `fsobject`, `Fid`, `l`, and malformed `&b - fid` names inconsistently.

Dependencies/integration: includes `codadir`, `srv`, `dllist`, and `objlist.h`; intended to mirror `vlist.cc`. Risks are high: typoed variables, wrong list field names, missing return from `OBJ_GetFree`, and invalid free variable make this a maintenance/build hazard. Test signals are primarily build-system inclusion checks, compiler errors if enabled, and comparison with `vlist.cc` as the working implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/objlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/objlist.h -->
# sources/distributed-fs/coda/coda-src/vol/objlist.h

Purpose: declares a C-style object-list structure for per-fid server objects, but it appears stale or incomplete relative to the rest of the C++ volume code.

Important types: `objlist` should contain a list head; `obj` stores a `ViceFid`, `Vnode *`, spool/log lists, and a union of file cleanup state or directory reintegration state. Macros mirror `vlist.h` field aliases (`f_sid`, `d_needsres`, etc.).

Control flow/state: objects are intended to track temporary resources during operations: file store ids and inodes to decrement/truncate on success/failure, or directory cloned inode/log-resolution flags during reintegration. That mirrors `vle` in `vlist.h`.

Dependencies/integration: depends on Coda server, directory, vnode, and list headers. Risks are very high because the header has malformed `extern "C"` closing comments, a missing semicolon after `struct objlist`, type/name mismatch with `objlist.c`, use of `olist` without visible include, and union field named `obj_u` while macros expect `u`. Test signals: whether this header is included in any build target, direct compilation, and migration/removal decisions against the working `vlist` implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/objlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/purge.cc -->
# sources/distributed-fs/coda/coda-src/vol/purge.cc

Purpose: provides `VPurgeVolume`, the high-level path to remove a volume from file-server memory and recoverable storage.

Important API: `VPurgeVolume(Volume *vp)` asserts that `DeleteVolume(vp)` succeeds, deletes the volume from the in-memory hash table, marks the volume shutting down, and calls `VPutVolume` so last-reference cleanup frees it.

Control flow/state: this intentionally bypasses `VDetachVolume` because the historical comment says FSYNC behavior was not understood. It first removes persistent state via recovery deletion, then removes VM traces and lets reference-counted volume cleanup complete.

Dependencies/integration: integrates `volume.h`, `recov.h`, `vutil.h`, vnode indexes, partition/inode code, and the recoverable volume deletion path. Risks include the comment "NEED TO REVIEW THIS CODE", hard assertion on delete failure, potential double deletion from hash because `DeleteVolume` itself hashes/frees in current code, and lack of FSYNC notification. Test signals: purge a volume while offline, purge failure injection, hash table state after purge, absence of leaked vnodes/inodes, and utility/file-server coordination regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/purge.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/recov.h -->
# sources/distributed-fs/coda/coda-src/vol/recov.h

Purpose: public interface for Coda recoverable storage volume operations.

Important APIs: initialization (`coda_init`), volume header creation/deletion/extraction (`NewVolHeader`, `DeleteVolume`, `DeleteRvmVolume`, `ExtractVolHeader`, `VolHeaderByIndex`), integrity checks, vnode extraction/replacement/growth, volume disk info read/write, vnode lookup/existence/count helpers, volume type/partition lookup, volume-cache setup, and max volume id allocation/get/set.

Control flow/state: callers operate over the RVM global volume list and class-local recoverable vnode lists. Mutators that change persistent structures are annotated as requiring transactions or excluding transactions when they manage their own transaction boundaries.

Dependencies/integration: depends on `volume.h` and Coda transaction annotations. It is consumed by volume attach/create/delete, salvage, dump tools, and vnode index wrappers. Risks include broad mutable API surface, mixed transaction ownership, and index/id confusion because many functions accept integer volume indexes and class-local vnode indexes. Test signals: first-time RVM init, new volume creation, vnode create/delete/replace, volume deletion, array growth, invalid index handling, and salvage recovery after interrupted transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/recov.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/recova.cc -->
# sources/distributed-fs/coda/coda-src/vol/recova.cc

Purpose: implements recoverable volume-header creation and whole-volume deletion from RVM.

Important APIs/functions: `NewVolHeader` finds a free `VolumeList` slot, initializes `VolumeHeader`, allocates `VolumeDiskData`, small and large recoverable vnode-list arrays, writes them into RVM, and inserts the volume id into the volume hash. `DeleteVolume` removes a live `Volume` from the hash/VM, marks its disk info destroyed/unblessed, then deletes small vnodes, large vnodes, volume data, and header. `DeleteRvmVolume` performs deletion by recoverable index for salvager use. Private `DeleteVnodes`, `DeleteVolData`, and `DeleteVolHeader` perform staged cleanup.

Control flow/state: vnode deletion is deliberately split into transactions of `MaxVnodesPerTransaction` to avoid long RVM transactions. File inode decrements are delayed until after commit; directory inodes are decremented in-transaction. After all vnode lists are empty, the list arrays and `VolumeDiskData` are freed and the header slot zeroed.

Dependencies/integration: depends on `rvmlib`, inode operations, recoverable lists, Coda volume/vnode definitions, cam debug helpers, and `volhash`. Risks include loss of atomicity across multi-transaction volume deletion, assumptions about backup volume inode ownership, hard assertions on vnode magic and transaction success, and `MAXVOLS`/`MaxVolId` boundary handling. Test signals: create/delete volume with mixed files/directories, interrupted deletion followed by salvage, inode reference accounting, and hash-table consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/recova.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/recovb.cc -->
# sources/distributed-fs/coda/coda-src/vol/recovb.cc

Purpose: implements vnode and volume-disk-info accessors over recoverable storage.

Important APIs: `ExtractVnode`, `ObjectExists`, `GetParentFid`, `ReplaceVnode`, `NewVolDiskInfo`, `VolDiskInfoById`, `ReplaceVolDiskInfo`, and `FindVnode`. Private `DeleteVnode` removes a single recoverable vnode. `ReplaceVnode` allocates a new `VnodeDiskObject` when a uniquifier is not present, appends it to the class-local `rec_smolist`, increments small/large vnode counts, and writes the disk object. A `vNull` object triggers deletion.

Control flow/state: all lookups validate volume index and class-local slot bounds, select small or large vnode lists, then find entries by uniquifier. Parent fid derivation special-cases root large vnodes whose parent uniquifier is zero. Disk info writes validate version stamps and copy the full `VolumeDiskData` into RVM.

Dependencies/integration: used by vnode cache writeback, index wrappers, dump/debug, resolution, and volume creation. Risks include direct memcpy of fixed vnode sizes, reliance on unique `uniquifier` within each slot list, off-by-one style checks using `> MAXVOLS`, hard assertions on disk-info stamps, and missing concurrency protection outside transaction discipline. Test signals: replace existing vnode, allocate first vnode in a slot, delete vnode with `vNull`, root parent lookup, stale uniquifier lookup, and volume disk-info stamp corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/recovb.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/recovc.cc -->
# sources/distributed-fs/coda/coda-src/vol/recovc.cc

Purpose: handles first-time RVM initialization, recoverable volume/vnode metadata checks, volume id allocation, vnode-list growth, and volume-disk-info extraction.

Important APIs: `coda_init`, `CheckVolData`, `ActiveVnodes`, `AllocatedVnodes`, `GetVolPartition`, `VAllocateVolumeId`, `VGetMaxVolumeId`, `VSetMaxVolumeId`, `GrowVnodes`, `ExtractVolDiskInfo`, and `AvailVnode`. `coda_init` initializes `MaxVolId` from `ThisServerId << 24`, old-compatible vnode free-list metadata, and a VM counter used by resolution store ids.

Control flow/state: `GrowVnodes` allocates a larger `rec_smolist` array, zeros the new tail, copies old entries, frees the old array, and updates the RVM pointer and count. `ExtractVolDiskInfo` copies disk info and validates stamp magic/version. `AvailVnode` distinguishes whole-slot emptiness from absence of a particular uniquifier.

Dependencies/integration: depends on `rvmlib`, Coda globals, volume/vnode types, and the volume-id hash. It is called during volume package init, bitmap growth, volume attach, and fid allocation. Risks include fatal exit when `ThisServerId` is unset, grow-by-copy transaction correctness, assumptions about `MaxVolId & 0x00FFFFFF`, and old free-list compatibility fields. Test signals: fresh RVM initialization, max-id overflow, grow small/large vnode arrays, invalid volume index checks, and `AvailVnode` for multi-uniquifier slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/recovc.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/struct.h -->
# sources/distributed-fs/coda/coda-src/vol/struct.h

Purpose: provides small structure-layout helper macros.

Important APIs: `fldsiz(type, member)` returns the size of a field, and `strbase(type, p, member)` computes the containing structure pointer from a member pointer using `coda_offsetof`.

Control flow/state: no runtime state; these macros are used while traversing embedded link nodes, especially recoverable list links inside `VnodeDiskObject` and hash/list links inside VRDB entries.

Dependencies/integration: depends on `coda_offsetof.h`. Integration is broad because Coda uses intrusive list structures. Risks include incorrect member pointer type or object lifetime causing invalid containing-object recovery. Test signals are compile-time use in `recovb`, `dumpcamstorage`, and `vrdb`, plus sanitizer-style checks when traversing lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/struct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/testvrdb.cc -->
# sources/distributed-fs/coda/coda-src/vol/testvrdb.cc

Purpose: standalone interactive test utility for building and querying the replicated volume database.

Important APIs/functions: `ReadConfigFile` loads server configuration and initializes the vice directory. `BuildVRDB` reads `db/VRList`, parses fixed fields into `vrent`, converts entries to network order, and writes `db/VRDB`. `CheckVRDB` loads the database into `VRDB`. `PrintVRDB` iterates the name hash and prints entries. `main` presents an interactive loop for lookup by replicated volume number, name, or rebuild.

Control flow/state: startup initializes config, builds the on-disk VRDB, and populates in-memory `VRDB`. Each loop command reads from stdin and invokes `VRDB.find`.

Dependencies/integration: uses `vrdb.h`, `codaconf`, `vice_file`, Unix file IO, and intrusive hash iteration. Risks include unsafe `gets`, hard parse width assumptions, abrupt `exit` on malformed input/write failure, and path mismatch in one status message (`vol/VRList` vs `db/VRList`). Test signals: compile as a test tool, parse valid and malformed VRList, query by name/id, rebuild in-place, and replace unsafe input before any production use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/testvrdb.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/treeremove.h -->
# sources/distributed-fs/coda/coda-src/vol/treeremove.h

Purpose: declares the parameter block for recursive tree removal and the directory traversal callback entry point.

Important APIs/types: `TreeRmBlk` stores client, replicated/group volume id, `Volume *`, output status, store id, vnode list, resolution flag, optional hierarchical volume log, server id, and block count pointer. `init` populates those fields and resets `*blocks`. `PerformTreeRemoval(PDirEntry, void *)` is the exported callback.

Control flow/state: callers initialize a `TreeRmBlk` before walking a directory tree. In resolution mode it carries the log tree and server id; otherwise those fields are nulled.

Dependencies/integration: depends on server, object-list, and dlist types and integrates directory traversal with volume mutation and resolution logging. Risks include raw pointer lifetime, unchecked `blocks` pointer, and all state being public mutable fields. Test signals: recursive remove with/without resolution, block accounting, callback use through directory walker, and null-pointer misuse in setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/treeremove.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/vicelock.h -->
# sources/distributed-fs/coda/coda-src/vol/vicelock.h

Purpose: defines the persistent advisory lock record embedded in vnode disk objects.

Important APIs/types: `ViceLock` contains `lockCount` and `lockTime`. `VICELOCKWAIT` is 30 minutes. `ViceLockCheckLocked` and `ViceLockClear` are simple macros for checking/clearing lock fields.

Control flow/state: the lock is part of `VnodeDiskObject`, so advisory lock state can be persisted or copied with vnodes. The "locked" check tests `lockTime == 0`, which is counterintuitive and should be verified against callers.

Dependencies/integration: included by `cvnode.h` and therefore by all vnode users. Risks include macro semantics, absence of owner identity in this structure, and stale persistent lock data. Test signals: vnode lock/unlock paths, timeout behavior against `VICELOCKWAIT`, and salvage/restore clearing behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/vicelock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/vldb.cc -->
# sources/distributed-fs/coda/coda-src/vol/vldb.cc

Purpose: reads and queries the legacy volume location database (`db/VLDB`) stored as fixed-size records in a hashed file.

Important APIs: `VCheckVLDB` opens the VLDB, validates the header magic, and records hash size. `VLDBLookup(key)` hashes a volume key with `HashString`, seeks to the bucket, reads groups of eight records, follows `hashNext` offsets, and returns a static matching record. `VLDBPrint` logs all non-zero records.

Control flow/state: global `VLDB_fd` and `VLDB_size` cache database state. Lookup lazily initializes with `VCheckVLDB` when needed. Records store ids in network byte order, so callers convert selected fields.

Dependencies/integration: used by `VGetVolumeInfo`, `VGetVolumeLocation`, and `VOL_Locate`; depends on `vldb.h`, partition/vutil/volume code, and file paths from `vice_file.h`. Risks include static result buffer, fixed record-size shift (`LOG_VLDBSIZE`), stale file descriptor after database replacement, partial-read handling, and hash-chain corruption causing misses. Test signals: missing/bad VLDB, lookup by name and numeric key, hash collision chains, print full database, and concurrent rebuild/lookup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/vldb.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/vldb.h -->
# sources/distributed-fs/coda/coda-src/vol/vldb.h

Purpose: defines the on-disk VLDB fixed-record format and paths.

Important types/definitions: `struct vldb` is 64 bytes, with a 33-byte key, hash-chain skip, volume type, server count, network-order volume ids for up to `MAXVOLTYPES`, and server numbers for `VSG_MEMBERS`. `struct vldbHeader` stores magic and hash size in network byte order. `VLDB_PATH`, `VLDB_TEMP`, and `BACKUPLIST_PATH` locate database files.

Control flow/state: callers interpret records by hashing text keys, seeking `index << LOG_VLDBSIZE`, and following `hashNext`. Header entry zero is reserved.

Dependencies/integration: includes `vice_file.h` for config paths and Coda/vice types for `byte`, `VSG_MEMBERS`, and volume type constants. Risks include ABI dependence on the 64-byte layout, network-byte-order fields, and truncating keys above 32 characters. Test signals: compile-time size assumptions, generated VLDB compatibility, lookup after byte-order conversion, and backup list path consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/vldb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/vlist.cc -->
# sources/distributed-fs/coda/coda-src/vol/vlist.cc

Purpose: implements the working C++ vnode-list entry helpers used to track per-fid operation state.

Important APIs: `VLECmp` compares two `vle` entries by fid after asserting same volume. `FindVLE` linearly searches a `dlist` for a matching `ViceFid`. `AddVLE` returns an existing entry or inserts a new `vle`.

Control flow/state: callers maintain a `dlist` of `vle` entries for an operation. `AddVLE` centralizes uniqueness by fid and initializes entry side state through the `vle` constructor.

Dependencies/integration: depends on Coda `dlist`, fid comparison macros, server types, and `vlist.h`. Risks include linear lookup cost, comparison assertions if misused across volumes, and caller responsibility for deletion after vnode pointers are released. Test signals: add duplicate fids, find missing/present fids, sort/compare same-volume entries, and clean destruction with `vptr == 0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/vlist.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/vlist.h -->
# sources/distributed-fs/coda/coda-src/vol/vlist.h

Purpose: defines `vle`, the C++ per-fid operation state object used during server mutations, reintegration, and resolution.

Important types/APIs: `vle` inherits `dlink`, stores a `ViceFid`, optional `Vnode *`, VM/RVM spooled log lists, and a union for file or directory side effects. File state tracks last store id and inodes to decrement/truncate. Directory state tracks cloned RVM inode and reintegration/resolution flags. Constructor initializes fields based on whether the fid is a directory; destructor asserts no vnode pointer remains.

Control flow/state: entries are added to dlist-based operation sets with `AddVLE`, mutated while the operation proceeds, then cleaned up once vnode references and pending inodes/logs are settled.

Dependencies/integration: depends on server, object-list, directory, vice, vnode, and list abstractions. Risks include public mutable fields, bitfields for reintegration flags, and raw resource handles whose cleanup policy is external. Test signals: file and directory constructor defaults, reintegration update/stale flags, inode cleanup after success/failure, and destructor assertion coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/vlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/vol-debug.cc -->
# sources/distributed-fs/coda/coda-src/vol/vol-debug.cc

Purpose: standalone debug printers for `VolumeDiskData` and `VnodeDiskObject`, separated from `volume.cc` to avoid linking heavy volume-package dependencies into dump tools.

Important APIs: `PrintVolumeDiskData(FILE *, VolumeDiskData *)` prints core volume identity, state flags, ids, quota/accounting, and disk usage. `PrintVnodeDiskObject(FILE *, VnodeDiskObject *, VnodeId)` prints vnode identity, data version, clone flag, length, inode/dir pointer, link count, type, volume index, parent fid, version vector, and directory ACL entries.

Control flow/state: purely read-only formatting, with directory-specific ACL interpretation through `VVnodeDiskACL`.

Dependencies/integration: used by utilities such as dump-to-tar paths that need layout printers without all of `volume.cc`. Depends on `cvnode.h`, `volume.h`, and ACL definitions. Risks include interpreting the vnode union as `dirNode` in generic output, ACL offset assumptions, and stale field coverage as structures evolve. Test signals: compile/link dump utilities, print directory and non-directory vnodes, and compare with `dumpcamstorage` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/vol-debug.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/voldefs.h -->
# sources/distributed-fs/coda/coda-src/vol/voldefs.h

Purpose: centralizes volume type aliases, volume-name formatting, key configuration paths, and file-server connection flags.

Important definitions: aliases map `readwriteVolume`, `readonlyVolume`, `backupVolume`, `replicatedVolume`, and `nonReplicatedVolume` onto numeric `RWVOL`, `ROVOL`, `BACKVOL`, `REPVOL`, and `NONREPVOL`. `VFORMAT` formats volume header/external names as `V%010u`. Paths include `MAXVOLIDPATH` and `SERVERLISTPATH`. `CONNECT_FS` and `DONT_CONNECT_FS` control volume package init behavior.

Control flow/state: no runtime state; these constants are consumed by `volume.h`, `volhash.cc`, `volume.cc`, utilities, and lookup code.

Dependencies/integration: uses `vice_config_path` through path macros. Risks include adding a volume type without updating `VolumeWriteable`, VLDB/VRDB assumptions, or external format compatibility. Test signals: volume type handling in attach/list/lookup, server-list path resolution, and volume external-name formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/voldefs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/volhash.cc -->
# sources/distributed-fs/coda/coda-src/vol/volhash.cc

Purpose: implements the in-memory mapping from `VolumeId` to recoverable `VolumeList` index.

Important APIs/classes: `InitVolTable`, `vhashtab`, `vhash_iterator`, `hashent`, `HashLookup`, `HashInsert`, and `HashDelete`. `VolIdHash` hashes a formatted volume id string in reverse to avoid adjacent volume ids mapping to adjacent buckets.

Control flow/state: global `VolTable` owns `hashent` records. Insert rejects duplicates, lookup returns the stored RVM index or `-1`, and delete removes and frees entries. `vhashtab` also tracks a volume count and debug name.

Dependencies/integration: used by recovery code (`NewVolHeader`, `ExtractVolHeader`, `GrowVnodes`), volume attach, and index constructors. Depends on `ohash`, `olist`, volume id/type definitions, and `VFORMAT`. Risks include no internal synchronization despite vestigial `Lock`/`Unlock` fields, hard failure on null remove, and global initialization ordering. Test signals: init before recovery operations, duplicate insert, delete missing entry, many adjacent volume ids, and lookup consistency after purge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/volhash.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/volhash.h -->
# sources/distributed-fs/coda/coda-src/vol/volhash.h

Purpose: declares the volume-id hash table abstraction used as the RVM volume index cache.

Important types/APIs: `vhashtab` extends `ohashtab` with a name, count, simple lock marker, add/remove/find/print methods. `vhash_iterator` wraps `ohashtab_iterator`. `hashent` stores `VolumeId` and recoverable storage index. Public C-style functions are `HashInsert`, `HashLookup`, and `HashDelete`.

Control flow/state: callers do not own the table directly; `InitVolTable` is a friend that allocates the global implementation. Hash entries are intrusive `olink` nodes.

Dependencies/integration: depends on Unix headers, `stdint`, `ohash`, `olist`, and Coda inconsistency/volume types. Risks include no exported `InitVolTable` declaration in this header, friend declaration typo for `vhashtab_iterator`, and lock methods that do not enforce mutual exclusion. Test signals: compile users, table initialization path in `VInitVolumePackage`, and hash operations around volume creation/deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/volhash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/vollocate.cc -->
# sources/distributed-fs/coda/coda-src/vol/vollocate.cc

Purpose: resolves a user-supplied volume key to a local replica/non-replicated volume id.

Important APIs: `VOL_Locate(char *volkey)` tries replicated volume name via `VRDB.find(char *)`, replicated volume id via hex parse and `VRDB.find(VolumeId)`, replica/non-replicated volume name via `VLDBLookup`, and finally returns the parsed numeric id if available. Helper `VREtoVolRepId` selects this server's replica from a `vrent`.

Control flow/state: resolution prioritizes VRDB group names/ids, then VLDB replica names, then raw numeric fallback. `vrent::index()` uses `ThisServerId`, so results are server-local.

Dependencies/integration: depends on server globals, VRDB, VLDB, volume hash types, and `vcrcommon`. Risks include accepting partial `strtoul` parses, returning zero for missing local replica, and ambiguity between hex numeric strings and names. Test signals: locate replicated name, replicated id, replica name, non-replicated numeric id, unknown key, and server without group membership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/vollocate.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/vollocate.h -->
# sources/distributed-fs/coda/coda-src/vol/vollocate.h

Purpose: declares the volume key resolution API.

Important API: `VolumeId VOL_Locate(char *volkey)` resolves names or ids through VRDB/VLDB logic. It includes `vcrcommon.h` for volume id/common replication types.

Control flow/state: no state in the header; the implementation consults global VRDB/VLDB/server state.

Dependencies/integration: used by volume utilities that accept flexible volume names or ids. Risks are a mutable `char *` signature for a read-only key and lack of error-code distinction because zero/missing can be ambiguous. Test signals: compile utility consumers and test all lookup fallbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/vollocate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/volres.h -->
# sources/distributed-fs/coda/coda-src/vol/volres.h

Purpose: declares resolution-log helper functions used by the volume/vnode layer.

Important APIs: `InitVolLog(int)`, `AllocateResLog(int, VnodeId, Unique_t)`, and `DeAllocateVMResLogListHeader(int, VnodeId, Unique_t)`.

Control flow/state: implementations are elsewhere, but declarations indicate volume resolution state can be initialized, allocated per vnode, and deallocated for VM log headers.

Dependencies/integration: included by `recovb.cc`, where vnode replacement may interact with resolution log allocation. Risks are minimal in this header but include weak type specificity (`int` volume/index arguments) and no transaction annotations. Test signals: build resolution-enabled paths, vnode writeback with `AllowResolution && V_RVMResOn`, and deallocation on vnode deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/volres.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/volume.cc -->
# sources/distributed-fs/coda/coda-src/vol/volume.cc

Purpose: central implementation of Coda's volume package: server/utility initialization, volume attach/detach/offline lifecycle, in-memory volume cache, bitmap allocation, volume statistics, update-list salvage safety, volume-level locks, and client-facing volume info lookup.

Important APIs/functions: `VInitVolUtil` arbitrates utility/salvager lock files and FSYNC connection. `VInitVolumePackage` initializes LRU header cache, volume id hash, vnode caches, VLDB, runs salvage, starts FSYNC, hashes and attaches valid RVM volumes, and initializes resolution-log transients. `VInitServerList` reads `db/servers`, resolves hostnames, and sets `ThisServerId`. `VGetVolumeInfo` and `VGetVolumeLocation` consult VLDB/FSYNC relocation data. `VAttachVolumeById`, `VAttachVolume`, and private `attach2` load headers/disk info, set online state, add the active volume hash entry, and build bitmaps. `VGetVolume`/`VPutVolume` implement reference-counted access, status errors, offline transition completion, and freeing on shutdown. `VOffline`, `VForceOffline`, `VDetachVolume`, `VShutdown`, `VUpdateVolume`, `GetVolObj`, and `PutVolObj` drive lifecycle and locking.

Control flow/state: persistent state lives in RVM `VolumeDiskData` and recoverable vnode lists; VM state includes `VolumeHashTable`, `volHeader` LRU entries, `vnIndex` bitmaps, `nUsers`, `goingOffline`, `shuttingDown`, `specialStatus`, and `VolLock`. Writable volume attach builds bitmaps by iterating recoverable vnodes and checks vnode magic/uniquifier consistency. `VPutVolume` is where an offline request actually persists `inUse = 0` once the last reference drops.

Dependencies/integration: integrates nearly every volume subsystem: partitions, RVM, vnode cache, recovery, FSYNC, VLDB, lock queue, salvage, volutil RPCs, and resolution logs. Risks include complex global initialization ordering, many fatal assertions/exits, raw LWP "rock" program-type switching, fixed hash/cache sizes, stale relocation semantics, bitmap growth not directly synchronized with RVM list growth except through `GrowVnodes`, and subtle reference-count/offline waits. Test signals: full server startup with salvage, attach/offline/detach as file server and utility, clone/dump/update modes, update-list `DONT_SALVAGE` cycling, bitmap allocation/free/grow, quota checks, lock queue timeout, and shutdown with/without outstanding transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/volume.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/volume.h -->
# sources/distributed-fs/coda/coda-src/vol/volume.h

Purpose: primary public contract for Coda volumes, volume disk data, memory-resident volume state, lifecycle APIs, and lock/disk-usage helpers.

Important types/definitions: `ProgramType` identifies file server, volume utility, salvager, or fs utility. `VolumeHeader` is the recoverable header. `VolumeDiskData` is the persistent administrative record with flags, ids, version vector, quotas, usage counters, dates, resolution log pointer, and messages. `vnodeIndex` is the VM allocation bitmap. `VolLock` is the volume-level mutation lock. `Volume` is the VM object tying hash links, cached header, partition, RVM index, vnode bitmaps, online/offline flags, refcount, special status, locks, and reintegrator state. `volHeader` is the LRU-cached copy of disk data.

Control flow/state: macros expose fields of cached `VolumeDiskData`, so most code mutates `V_inUse`, `V_destroyMe`, `V_diskused`, etc. through macro lvalues. Attach modes (`V_READONLY`, `V_CLONE`, `V_UPDATE`, `V_DUMP`, `V_SECRETLY`) define how utilities coordinate with the file server.

Dependencies/integration: includes recovery volume logs, vice types, partition lists, and `voldefs.h`; exposes initialization, lookup, attach, update, purge, shutdown, stats, disk usage, and volume-object lock APIs. Risks include macro-heavy mutable state, persistent layout ABI, raw pointers in persistent/VM structures, and transaction annotations that callers must honor. Test signals: ABI/layout compatibility, attach mode matrix, field macro mutation, disk usage enforcement, and lock helper behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/volume.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/vrdb.cc -->
# sources/distributed-fs/coda/coda-src/vol/vrdb.cc

Purpose: implements the in-memory replicated volume database and conversion helpers between replicated volume ids and per-server replica ids.

Important APIs/classes: global `VRDB`; `vrtab` maintains two hash tables, by replicated volume id and by name. `CheckVRDB` reads `db/VRList`, parses entries, and populates `VRDB`. `DumpVRDB` writes current entries. `XlateVid` maps replicated ids to this server's replica id and returns count/position/type; non-replicated or replica ids are handled as pass-through with metadata. `ReverseXlateVid` maps replica id back to replicated id. `vrent` supplies host/index lookup, check-version-vector construction, `VolumeInfo` filling, network byte-order conversion, print, and dump.

Control flow/state: `VRDB.clear` removes both hash-table links before reload. `vrent::index` selects the local replica by `ThisServerId`, while `ReverseFind` scans all entries. Replicated ids are identified by high-byte pattern `0x7f`.

Dependencies/integration: used by volume location, client volume info, resolution, and test/build tools. Depends on intrusive hash/list helpers, `volume.h`, `srv.h`, server id globals, and Coda volume id encoding macros. Risks include line parse assertions killing process on malformed VRList, name hash as simple byte sum, reverse lookup O(n), and assumptions about replicated id encoding. Test signals: load valid/malformed VRList, lookup by name/id, local replica selection for each server id, reverse translation, dump/reload round trip, and `GetVolumeInfo` with missing host address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/vrdb.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/vrdb.h -->
# sources/distributed-fs/coda/coda-src/vol/vrdb.h

Purpose: declares the replicated volume database types, file paths, and translation APIs.

Important types/APIs: `vrtab` extends `ohashtab` and owns a secondary `namehtb`; it can add/remove/find/clear/print/dump `vrent` entries. `vrent` stores name key, replicated volume id, name hash link, server count, per-server replica volume numbers, and helpers for host/index lookup, check VV generation, `VolumeInfo` population, byte-order conversion, printing, and dumping. Public functions are `CheckVRDB`, `DumpVRDB`, `XlateVid`, and `ReverseXlateVid`.

Control flow/state: `VRDB_PATH`, `VRDB_TEMP`, and `VRLIST_PATH` locate database inputs/outputs. `VRTABHASHSIZE` fixes hash-table sizing.

Dependencies/integration: includes `vcrcommon`, `vice`, `ohash`, inconsistency utilities, `vice_file`, and deprecation warnings. Risks include unusual `public :` formatting, public data fields, raw char key buffer, and unsupported assignment operator that aborts. Test signals: compile users, reload/dump, field size compatibility with `testvrdb`, and single-homing warnings for host helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/vrdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/vutil.cc -->
# sources/distributed-fs/coda/coda-src/vol/vutil.cc

Purpose: volume utility helper implementations for creating and copying volume metadata.

Important APIs: `VCreateVolume` creates a new RVM volume record, optionally allocates a recoverable resolution log, writes a header and disk info through recovery APIs, and attaches it secretly. `AssignVolumeName` normalizes names and optional suffixes. `CopyVolumeHeader` copies administrative disk data from one volume to another while preserving immutable ids/group/copy date and resetting destroy/log/resolution fields. `ClearVolumeStats` zeros daily/weekly usage counters.

Control flow/state: new volumes are created with `destroyMe = DESTROY_ME`, meaning the file server should not attach them until utility code finishes and clears the flag. `VCreateVolume` locks the partition, allocates `VolumeDiskData`, calls `NewVolHeader`, then `NewVolDiskInfo`, and returns an attached `Volume *` in `V_SECRETLY` mode.

Dependencies/integration: depends on partitions, vice inode support, `volume.h`, `recov.h`, recoverable volume logs, and `AllowResolution`. Risks include `sprintf(vol.partition, partition, strlen(partition)+1)` misuse where `strncpy`/`snprintf` would be expected, leaving destroy flag uncleared by caller, partial creation cleanup after `NewVolDiskInfo` failure, and transaction ownership by caller. Test signals: create RW/RO/backup/replicated volumes, long partition names, optional RVM logs, interrupted restore cleanup, header copy preserving immutable ids, and name suffix stripping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/vutil.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/vutil.h -->
# sources/distributed-fs/coda/coda-src/vol/vutil.h

Purpose: declares utility routines used by offline volume programs and dump/salvage tooling.

Important APIs: `VCreateVolume`, `MakeBackupVolume`, `AssignVolumeName`, `CopyVolumeHeader`, `ClearVolumeStats`, `ListViceInodes`, `ListCodaInodes`, `HashString`, and `CloneVolume`. `VCreateVolume` is annotated as transaction-required and has default type/log-size arguments.

Control flow/state: the header exposes creation/clone/list helpers but implementations are split across several utility files. Inode listing callbacks accept `ViceInodeInfo` and a volume id parameter to judge ownership.

Dependencies/integration: includes transaction annotations and `voldefs.h`; depends on `Volume`, `Error`, `VolumeDiskData`, and inode info types from surrounding includes. Risks include broad prototypes with raw `char *` and function-pointer callbacks, and default arguments coupling C++ callers to volume type constants. Test signals: compile volutil programs, create/clone/backup workflows, inode listing callbacks, and hash compatibility with VLDB generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vol/vutil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/Makefile.am -->
# sources/distributed-fs/coda/coda-src/volutil/Makefile.am

Purpose: automake definition for Coda volume utility libraries and programs.

Important targets: under `BUILD_SERVER`, builds noinst libraries `libvolutil.la`, `libvolserv.la`, and `libdumpstuff.la`; installs/defines `volutil`, `codareaddump`, `codamergedump`, and `codadump2tar`; and distributes man pages. `libvolutil_la_SOURCES` aggregates many volume subcommands plus dump helpers. `libvolserv_la_SOURCES` provides server-side volutil RPC implementation. Program source lists define specific dump/read/merge/tar frontends.

Control flow/state: `AM_CPPFLAGS` wires include paths across base, kernel dependency, util, vicedep, dir, ACL, partition, auth, vv, lka, vol, and resolution trees with large-file flags. `*_LDADD` expresses library dependencies for each frontend, including RPC2/RVM/readline/termcap as needed.

Dependencies/integration: this is the build integration point connecting volutil commands to auth, vicedep, util, kerndep, base, vv, dir, ACL, rwcdb, and RPC/RVM libraries. Risks include duplicate dump sources in `libvolutil_la_SOURCES`, conditional server-only build coverage, and fragile dependency order. Test signals: `make` with `BUILD_SERVER`, link every program, distcheck/manpage inclusion, and targeted rebuild after changing volume/dump libraries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/Makefile.am -->
