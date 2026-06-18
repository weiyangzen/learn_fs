# subset-b-007761 Research Report

Grouped research report for the requested OpenAFS source files. Each section preserves the source path in its title and is wrapped in the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_vcache.c -->
# sources/distributed-fs/openafs/src/afs/afs_vcache.c

Purpose: implements cache-manager vnode/stat-cache lifecycle for `struct vcache`: allocation, lookup, callback state, status fetching, LRU pressure eviction, disconnected-mode dirty tracking hooks, and shutdown cleanup. It is the main bridge between AFS FIDs and platform vnodes.

Important APIs and state: global locks include `afs_xvcache`, `afs_xvcb`, `afs_xvreclaim`, and `afs_xvcdirty`. Global queues/tables include `VLRU`, `afs_vhashT`, `afs_vhashTV`, callback-return hash `afs_cbrHashT`, and disk slot allocation state `afs_nextVcacheSlot`/`afs_freeSlotList`. Core entry points are `afs_GetVCache`, `afs_LookupVCache`, `afs_GetRootVCache`, `afs_FindVCache`, `afs_NFSFindVCache`, `afs_FetchStatus`, `afs_UpdateStatus`, `afs_WriteVCache`, `afs_WriteVCacheDiscon`, `afs_ResetVCache`, `afs_FlushVCache`, `afs_ShakeLooseVCaches`, `afs_FlushVCBs`, `afs_DisconGiveUpCallbacks`, and `shutdown_vcache`.

Control flow: lookup first probes `afs_vhashT` under `afs_xvcache`, optionally moves a live entry to the head of `VLRU`, then fetches status over RX if `CStatd` is absent. New vcaches are pre-populated, inserted into both hash tables and LRU, attached to a platform vnode, then post-populated and woken from `CVInit`. Status RPCs run through `afs_Conn`/`RXAFS_FetchStatus` or `RXAFS_Lookup`, validated by `afs_CheckFetchStatus`, then merged via `afs_ProcessFS` and callback queuing under `afs_xcbhash`. Eviction removes entries from VLRU/hash queues, clears DNLC/link/mountpoint/access state, queues callback returns, and either places the vcache on a non-Linux free list or drops Linux vnode references.

State and persistence: this file persists no standalone file, but `diskSlot` binds vcaches to cache metadata slots and is preserved across reinitialization of the struct. State flags such as `CVInit`, `CVFlushed`, `CStatd`, `CUnique`, `CRO`, `CBackup`, `CForeign`, `CBulkFetching`, `CUnlinked`, `CUnlinkedDel`, and `CCore` determine status validity, callback truth, data writeback, and deferred unlink handling. Disconnected writes use `VDisconSetTime`, `VDisconSetMode`, and `VDisconTrunc` through `afs_DisconAddDirty`.

Dependencies and integration points: depends heavily on `afs.h` data structures, `afs_volume.c` volume lookup, RXAFS file-server RPCs, VL/cell/server connection machinery, DNLC helpers, cache segment invalidation, platform vnode functions in `osi_*`, callback queueing, and stats/tracing macros. It also integrates with NFS translation by supporting partial FID matching in `afs_NFSFindVCache`.

Risks: lock ordering is delicate, especially when `afs_QueueVCB` may drop and reacquire `afs_xvcache` while holding callback state, and when `afs_FindVCache` upgrades shared locks for LRU movement. Fetch-status validation intentionally treats malformed server data as `VBUSY`; changes here can become data-corruption risks. Platform branches for Darwin, Linux, Solaris, SGI, and BSD have distinct vnode reference semantics. LRU corruption checks panic or warn, so queue invariants are critical. Disconnected-mode status suppression under `AFS_IN_SYNC` can hide stale metadata if flags are mishandled.

Test signals: exercise cold lookup, hot lookup, root volume lookup, callback expiry, RO callback fallback, malformed fetch-status response, NFS translator duplicate FID handling, stat-cache pressure trimming, last-reference store/unlink cleanup, disconnected metadata updates, shutdown cleanup, and platform vnode reference failure paths. Instrument hits/misses, `vcachegen`, `afs_vcount`, callback-return counts, and warnings from `afs_ShakeLooseVCaches`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_vcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_volume.c -->
# sources/distributed-fs/openafs/src/afs/afs_volume.c

Purpose: implements cache-manager volume lookup and volume-entry caching. It maps volume IDs/names to `struct volume`, populates server site lists from VLDB entries, handles dynroot volumes, invalidates expired volume information, and persists volume metadata for UFS cache mode.

Important APIs and state: globals include `afs_xvolume`, `afs_volumes[NVOLS]`, `afs_freeVolList`, `volumeInode`, `fvTable[NFENTRIES]`, `afs_volCounter`, `afs_volume_ttl`, and `afs_siteless_volume_ttl`. Key functions are `afs_UFSGetVolSlot`, `afs_MemGetVolSlot`, `afs_SetupVolSlot`, `afs_FindVolume`, `afs_GetVolume`, `afs_GetVolumeByName`, `afs_NewVolumeByName`, `afs_SetupVolume`, `afs_NewDynrootVolume`, `LockAndInstallVolumeEntry`, `LockAndInstallNVolumeEntry`, `LockAndInstallUVolumeEntry`, `afs_CheckVolumeNames`, `afs_ResetVolumes`, and `afs_ResetVolumeInfo`.

Control flow: callers find a valid cached volume by ID or name; on misses the code queries VLDB using old, new, or UUID-capable RPCs depending on server capability. `afs_SetupVolume` chooses RW/RO/BK ID by suffix or numeric name, allocates/reuses a slot, installs server sites, stores volume type flags, and optionally caches the name. `afs_CheckVolumeNames` scans all volumes for expiration, resets stale state, clears busy flags, and then invalidates affected mountpoints and RO callbacks in the vcache table.

State and persistence: UFS mode stores `struct fvolume` records in `VolumeItems` via `volumeInode`, using `fvTable` as an on-disk hash-chain index and `staticFVolume`/`afs_FVIndex` as a one-record cache. Memory mode allocates volume slots dynamically. Volume state includes `VRO`, `VBackup`, `VForeign`, `VRecheck`, and `VHardMount`; server status slots are reset to `not_busy` during setup and invalidation.

Dependencies and integration points: integrates with cells, VLDB RPCs (`VL_GetEntryByNameO/N/U`, `VL_GetAddrsU`), server cache management (`afs_GetServer`, `afs_FindServer`, `afs_SortServers`), dynroot helpers, vcache invalidation, DNLC purge, and request/error propagation through `afs_Analyze` and `afs_CopyError`. `afs_vcache.c` consumes volume flags to mark vcaches as RO/backup/foreign/root and to copy mountpoint parent FIDs.

Risks: `afs_UFSGetVolSlot` mutates disk-backed slot state and must roll back carefully on read/write errors; stale `staticFVolume` state can corrupt hash chains if not invalidated. UUID VLDB handling performs nested address discovery and can leave `areq->volumeError = VOLMISSING` without installing a lock if lookup fails. Expiration and force invalidation walk both volume and vcache tables, so lock ordering and vnode holds are sensitive. `afs_FindVolume` ignores the `locktype` argument in this implementation and returns with only a refcount increment, so callers must follow local conventions.

Test signals: test numeric volume names, `.readonly` and `.backup` suffix resolution, dynroot FIDs, old/new/UUID VLDB capability fallback, site-less volume TTL expiry, forced mountpoint invalidation, UFS volumeinfo read/write failures, missing UUID address records, and reset of hard-mount/busy state after server movement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_volume.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_warn.c -->
# sources/distributed-fs/openafs/src/afs/afs_warn.c

Purpose: central warning output helpers for the cache manager. It gates console and user-visible warnings through `afs_showflags`, abstracts platform print APIs, and emits a specific cache-partition-full warning.

Important APIs: `afs_warn`, `afs_warnuser`, `afs_warnall`, and `afs_WarnENOSPC`. Platform-specific internals include `afs_vprintf`, `afs_vwarn`, and `afs_vwarnuser`; AIX uses old-style varargs and explicit `/dev/console` writes via `fp_open`/`fp_write`.

Control flow: `afs_warn` emits only when `GAGCONSOLE` is set. `afs_warnuser` emits only when `GAGUSER` is set and may drop/reacquire the AFS global lock around user printf paths. `afs_warnall` avoids duplicate Linux output because console and user paths converge there. The Mariner variant logs a `warn$` record before printing.

State and persistence: no persistent state. Runtime behavior depends on `afs_showflags`, `afs_mariner`, and global lock state. `AFS_STATCNT` records call counts.

Dependencies and integration points: used across cache/volume/vcache code for operational warnings. It depends on platform kernel printf facilities, `afsincludes.h`, and stats macros. `afs_WarnENOSPC` is a higher-level signal for cache partition exhaustion.

Risks: format-string handling is kernel-side; callers must pass trusted format strings and matching arguments. Lock transitions around user output are platform-sensitive. The Darwin 8 inline path calls `printf(buf)`, so any accidental `%` generated into `buf` would be unsafe if the buffer content were not purely formatted from a trusted format string.

Test signals: verify console-only, user-only, both, and neither flag combinations; Linux duplicate suppression; AIX console path failure tolerance; Mariner logging; global-lock drop/reacquire balance; and that ENOSPC warning is user-visible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_warn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afsincludes.h -->
# sources/distributed-fs/openafs/src/afs/afsincludes.h

Purpose: aggregate AFS kernel/cache-manager headers in a consistent order, with a UKERNEL redirect. It is the project-local counterpart to `sysincludes.h`.

Important APIs/types: defines only the include guard `AFS_INCLUDES_H`; it exports no functions. It includes AFS core headers such as `afs/stds.h`, `roken.h`, `afs/opr.h`, `rx/rx.h`, `afs/afs_osi.h`, `afs/lock.h`, `volerrors.h`, `voldefs.h`, `afsint.h`, `exporter.h`, `vldbint.h`, `afs.h`, `afs_chunkops.h`, `rxkad.h`, `prs_fs.h`, `dir.h`, `afs_axscache.h`, `icl.h`, `afs_stats.h`, `afs_prototypes.h`, and `discon.h`.

Control flow: compile-time only. For `UKERNEL`, it delegates to `UKERNEL/afsincludes.h`; otherwise it selects OS-specific `osi_vfs.h` and `osi_machdep.h` includes and normalizes Linux macro conflicts by undefining `TRUE`, `FALSE`, `__NFDBITS`, and `__FDMASK` before protocol headers.

State and persistence: none.

Dependencies and integration points: included by major cache-manager C files after `sysincludes.h`, making it the common dependency surface for OpenAFS structs, RPC interfaces, locking, errors, stats, and prototypes.

Risks: include order changes can break kernel builds because OS headers and AFS protocol headers define overlapping names. Linux macro undefines are compatibility-sensitive. Adding new headers here increases rebuild scope and can introduce platform-only compile errors.

Test signals: build matrix across Linux, Darwin, BSD, AIX/HPUX/Solaris/SGI where supported; verify no duplicate macro/type conflicts and that UKERNEL builds continue to use the alternate include set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afsincludes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/discon.h -->
# sources/distributed-fs/openafs/src/afs/discon.h

Purpose: public interface and inline queue helpers for disconnected and disconnected-readwrite cache-manager operation.

Important APIs/types: declares global mode flags `afs_is_disconnected`, `afs_is_discon_rw`, `afs_in_sync`, locks `afs_discon_lock` and `afs_disconDirtyLock`, queues `afs_disconDirty` and `afs_disconShadow`, conflict policy, and `afs_DisconVnode`. Prototypes cover resync, connection removal, fake/shadow FID generation, shadow directories, dcache lookup by FID, status update, discard-all, and `afs_WriteVCacheDiscon`. Macros `AFS_IS_DISCONNECTED`, `AFS_IS_DISCON_RW`, and `AFS_IN_SYNC` are used by vcache/volume code.

Control flow: `afs_DisconAddDirty` appends a vcache to `afs_disconDirty` only on the first dirty operation, optionally taking `afs_xvcache`, then takes a vcache reference so queue membership pins it. `afs_DisconRemoveDirty` removes the queue entry, clears dirty flags, and releases that reference.

State and persistence: tracks in-memory dirty and shadow queues; persistence is indirect through later resync and dcache/shadow directory machinery. `avc->f.ddirty_flags` accumulates operations such as metadata update or truncation.

Dependencies and integration points: consumed by `afs_vcache.c` for disconnected status writes and callback behavior; relies on `struct vcache`, `struct dcache`, `struct vrequest`, AFS queue primitives, and vcache refcount helpers.

Risks: dirty queue membership and vcache references must stay paired, or disconnected vcaches can leak or be freed while queued. `afs_DisconVnode` is explicitly not protected. The inline helpers assume the vcache lock is already held; misuse can race dirty flags.

Test signals: dirty add/remove idempotence, refcount balance, resync after metadata-only changes, truncation dirty flags, concurrent disconnected writes, discard-all, and reconnect while `AFS_IN_SYNC` suppresses normal status updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/discon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/exporter.h -->
# sources/distributed-fs/openafs/src/afs/exporter.h

Purpose: defines the cache-manager exporter abstraction, primarily for the NFS/AFS translator and remote-user request handling.

Important APIs/types: `struct exporterops` contains callbacks for request handling, hold/release, sysname lookup, garbage collection, stats, host validation, and host retrieval. `struct afs_exporter` stores linked-list state, ops, flags, type, stats, and private data. `struct exporterstats`, `struct afs3_fid`, and `struct Sfid` define accounting and exported file-handle layouts. Macros dispatch operation calls and define `EXP_NFS`, `EXP_EXPORTED`, `EXP_UNIXMODE`, `EXP_PWSYNC`, `EXP_SUBMOUNTS`, `EXP_CLIPAGS`, `EXP_CALLBACK`, `AFS_NFSFULLFID`, and `AFS_XLATOR_MAGIC`.

Control flow: compile-time data/dispatch layer. Runtime exporter implementations supply `exporterops`; callers use `EXP_*` macros to invoke them.

State and persistence: exporter instances hold in-memory reference and statistics state. File handle structs encode Cell/Volume/Vnode/Unique for cross-protocol identity but are not persistent storage by themselves.

Dependencies and integration points: ties into `nfsclient.h`, vcache NFS lookup, credential/PAG handling, `@sys` expansion, and platform NFS file-handle limits. `AFS_NFSXLATORREQ` detects translator credentials except on Darwin/XBSD where it is disabled.

Risks: `AFS_XLATOR_MAGIC` size differs on 64-bit kernels to fit NFS handle limits; changing layout can break file-handle compatibility. The first fields of `nfsclientpag` intentionally overlay `afs_exporter`, so struct layout is an ABI-like contract. Credential detection depends on group ID conventions.

Test signals: NFS translator mount/export operations, file-handle decode on 32-bit and 64-bit kernels, PAG/sysname handling, exporter refcount and GC paths, rejected remote-user calls, and host validation callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/exporter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/findlocks -->
# sources/distributed-fs/openafs/src/afs/findlocks

Purpose: developer utility script for scanning source trees for OpenAFS lock acquisition source-indicator numbers and reporting duplicates.

Important APIs/types: Perl script using `File::Find` and `IO::File`. Pattern matches `ObtainLock`, `ObtainWriteLock`, `ObtainSharedLock`, `NBObtainLock`, `NBObtainWriteLock`, `NBObtainSharedLock`, and `UpgradeSToWLock` calls with a numeric second argument.

Control flow: optional `-d` restricts output to duplicate lock IDs. The script recursively visits input paths, records `path:line` per numeric lock ID, then prints IDs in numeric order with all locations.

State and persistence: no persistent state; all results are in-memory arrays for one run.

Dependencies and integration points: supports the `lock.h` convention where write/shared/upgrade acquisition records `src_indicator`. It is useful when maintaining `MAX_LOCK_NUMBER` and avoiding duplicate diagnostic IDs.

Risks: regex-based scanning misses multi-line/unusual macro invocations and can produce false positives in comments or strings. It assumes lock ID arguments are literal integers.

Test signals: run against `src/afs` with and without `-d`; verify known duplicate and unique lock IDs; include files with no lock calls and nested directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/findlocks -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/lock.h -->
# sources/distributed-fs/openafs/src/afs/lock.h

Purpose: defines OpenAFS kernel lock structures and fast inline lock operations used throughout the cache manager.

Important APIs/types: `struct afs_lock`/`afs_lock_t`/`afs_rwlock_t`, lock modes `READ_LOCK`, `WRITE_LOCK`, `SHARED_LOCK`, `BOOSTED_LOCK`, `EXCL_LOCKS`, and `MAX_LOCK_NUMBER`. Inline APIs include `ObtainReadLock`, `NBObtainReadLock`, `ObtainWriteLock`, `NBObtainWriteLock`, `ObtainSharedLock`, `NBObtainSharedLock`, `UpgradeSToWLock`, conversions from write/shared to weaker modes, release helpers, `LockWaiters`, `CheckLock`, and `WriteLocked`.

Control flow: fast paths update lock fields directly under the AFS global lock; contended paths call `Afs_Lock_Obtain`, `Afs_Lock_ReleaseR`, or `Afs_Lock_ReleaseW`. Shared locks are exclusive against other shared/write holders but allow readers; boosted locks upgrade shared to write once readers drain. Source indicators are recorded for write/shared/upgrade acquisitions.

State and persistence: lock state is in memory: waiting modes, exclusive mode, reader count, number waiting, timing/stat fields, last reader, writer, and source indicator.

Dependencies and integration points: requires `KERNEL`, platform-specific current-thread/process macros, `AFS_ASSERT_GLOCK`, `osi_Assert`, and optional ICL tracing. It underpins `afs_vcache.c`, `afs_volume.c`, disconnected queues, callback hashes, and most cache-manager shared structures.

Risks: all inline operations assume the AFS global lock is held. Incorrect release mode or missing conversion can violate assertions or deadlock. Duplicate source indicators reduce diagnostic value. Platform `MyPidxx` definitions are central to ownership assertions.

Test signals: contention tests for read/write/shared/upgrade modes, nonblocking failure paths, waiter wakeups, conversion behavior, GLOCK assertion failures in debug builds, and `findlocks -d` duplicate scans after new lock sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/lock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/nfsclient.h -->
# sources/distributed-fs/openafs/src/afs/nfsclient.h

Purpose: defines per-NFS-client PAG/exporter state for the NFS/AFS translator.

Important APIs/types: constants `NNFSCLIENTS`, `NHash(host)`, `NFSCLIENTGC`, and `NFSXLATOR_CRED`. `struct nfsclientpag` overlays its first fields with `struct afs_exporter`, then adds refcount, UID, host, PAG, client UID, per-client `@sys` values, count, and `lastcall`.

Control flow: no functions; hash and timeout constants guide implementation elsewhere. Entries are looked up by host/UID and garbage-collected after `NFSCLIENTGC`.

State and persistence: in-memory translator state only. PAG and sysname values preserve remote client identity between calls.

Dependencies and integration points: depends on `exporter.h` layout and `MAXNUMSYSNAMES` from AFS headers. Used by NFS translator request handling and by vcache partial-FID lookup paths.

Risks: overlay layout with `afs_exporter` must remain stable. Host hash is simple bitmasking and assumes table size is a power of two. Stale PAG/sysname state can leak remote identity behavior until GC.

Test signals: hash distribution, GC after 24 hours, refcount balance, sysname propagation, host/UID distinction, and translator credential detection via `NFSXLATOR_CRED`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/nfsclient.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/sysctl.h -->
# sources/distributed-fs/openafs/src/afs/sysctl.h

Purpose: assigns numeric sysctl namespace IDs for platform-independent and platform-specific OpenAFS cache-manager controls.

Important APIs/types: top-level IDs include `AFS_SC_ALL`, `AFS_SC_DARWIN`, `AFS_SC_AIX`, `AFS_SC_DFBSD`, `AFS_SC_FBSD`, `AFS_SC_LINUX`, `AFS_SC_HPUX`, `AFS_SC_IRIX`, `AFS_SC_NBSD`, `AFS_SC_OBSD`, `AFS_SC_SOLARIS`, and `AFS_SC_UKERNEL`. Subspaces define Darwin releases and feature controls, AIX releases, FreeBSD releases, and Linux kernel generations.

Control flow: compile-time constants only.

State and persistence: none in this header; external sysctl registration code interprets these IDs.

Dependencies and integration points: used by OS-specific sysctl handlers and user/admin tooling that expects stable numeric IDs.

Risks: renumbering breaks compatibility. Adding new platform controls must avoid collisions and preserve existing values.

Test signals: compile sysctl consumers, verify registered OIDs match expected numeric paths, and test platform feature toggles such as Darwin real modes, fsevents, and bulkstat where implemented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/sysctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/sysincludes.h -->
# sources/distributed-fs/openafs/src/afs/sysincludes.h

Purpose: centralizes OS/kernel header inclusion for AFS cache-manager code, with extensive platform conditionals and a UKERNEL redirect.

Important APIs/types: no exported functions. It chooses system headers for OpenBSD, NetBSD, Linux, AIX, SGI, Solaris, HPUX, Darwin, FreeBSD, and generic legacy Unix paths. It also defines guard macros to prevent namespace conflicts with Linux Coda/XFS inode headers and declares FreeBSD `M_AFS`.

Control flow: compile-time only. Linux includes modern kernel headers such as `uaccess`, `list`, `dcache`, `mount`, `fs`, `quota`, `sched`, `mm`, `slab`, `proc_fs`, `completion`, and optional `exportfs`. Non-Linux paths include vnode, UFS, socket, mbuf, proc, ioctl, flock, and platform VM headers as needed.

State and persistence: none.

Dependencies and integration points: included before `afsincludes.h` by C files such as `afs_vcache.c`, `afs_volume.c`, and `afs_warn.c`. It provides the kernel type universe for vnodes, credentials, sockets, uio, buffers, and memory APIs consumed by OpenAFS abstractions.

Risks: include-order and macro-conflict risk is high. Some branches intentionally fake or predefine guard macros to avoid conflicting external filesystems. Platform kernel header evolution can break stale conditionals. Duplicate NetBSD includes are harmless but indicate historical accretion.

Test signals: broad compile matrix, especially Linux kernel-version feature probes, Darwin/FreeBSD vnode builds, Solaris 5.10/5.11 branches, and SGI debug header behavior. Also test that `UKERNEL` redirects without pulling kernel headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/sysincludes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/unified_afs.p.h -->
# sources/distributed-fs/openafs/src/afs/unified_afs.p.h

Purpose: provides fallback errno definitions so generated/unified AFS code can compile on platforms missing specific errno constants.

Important APIs/types: includes NT errno mapping for `AFS_NT40_ENV`, requires `EIO`, maps missing `EDQUOT` to `ENOSPC`, and maps many other missing errno constants to `EIO`.

Control flow: compile-time preprocessor fallback list only. If `EIO` is absent, compilation fails because there is no safe common fallback.

State and persistence: none.

Dependencies and integration points: used by generated prototype/unified code and cross-platform builds where error constants vary. Volume/cache code relies on named errors such as `ENETDOWN`, `VBUSY`, `EDQUOT`, and `EROFS` being defined.

Risks: mapping unknown errors to `EIO` preserves compilation but collapses semantics, potentially hiding distinctions between retryable, permission, quota, network, and stale-handle failures on deficient platforms. Adding a fallback can affect conditional code that uses `#ifdef` to detect platform capabilities.

Test signals: preprocess on minimal/Windows-like environments, verify required errno names compile, and confirm runtime error translation still distinguishes important cases on full POSIX platforms where native constants exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/unified_afs.p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/voldefs.h -->
# sources/distributed-fs/openafs/src/afs/voldefs.h

Purpose: defines common volume type IDs and volume header filename conventions.

Important APIs/types: aliases `readwriteVolume`, `readonlyVolume`, and `backupVolume` map to `RWVOL`, `ROVOL`, and `BACKVOL`. Type IDs are `RWVOL = 0`, `ROVOL = 1`, `BACKVOL = 2`. Header file naming uses `VHDREXT`/`VFORMAT`, with `.vl` on AIX/HPUX and `.vol` elsewhere. `VMAXPATHLEN` caps external volume path length at 64 bytes.

Control flow: compile-time constants; `AFS_VOLID_FMT` from `afs/param.h` must be available before including this file.

State and persistence: affects persistent on-disk volume header filenames on file servers and related tooling.

Dependencies and integration points: consumed by volume and VLDB code, including `afs_volume.c` when choosing RW/RO/BK IDs from entries.

Risks: changing numeric type IDs or file-name formats breaks compatibility. The comments warn against clever token-pasting because historical compilers handled it inconsistently.

Test signals: build with AIX/HPUX and non-AIX/HPUX formats, verify generated names for representative volume IDs, and confirm volume type indexing matches VLDB arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/voldefs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/volerrors.h -->
# sources/distributed-fs/openafs/src/afs/volerrors.h

Purpose: defines volume package error codes and special server-returned conditions.

Important APIs/types: `VREADONLY` maps to `EROFS`; special codes start at `VICE_SPECIAL_ERRORS = 101`. Defined conditions include `VSALVAGE`, `VNOVNODE`, `VNOVOL`, `VVOLEXISTS`, `VNOSERVICE`, `VOFFLINE`, `VONLINE`, `VDISKFULL`, `VOVERQUOTA`, `VBUSY`, `VMOVED`, and negative `VRESTARTING`.

Control flow: constants only. Callers interpret some values specially instead of passing them directly to applications.

State and persistence: none.

Dependencies and integration points: included by `afsincludes.h` and used by vcache/volume/server analysis paths. `afs_CheckFetchStatus` returns `VBUSY` for malformed fetch status, and `afs_FlushActiveVcaches` suppresses some warnings for `VNOVNODE`.

Risks: numeric compatibility is important; old cache managers interpret negative `VRESTARTING` as server-down. Typos or remapping can change retry/offline/quota behavior.

Test signals: server error translation tests for readonly, over quota, disk full, busy, moved, restarting, and salvage/offline cases; verify retry logic handles `VBUSY`/`VRESTARTING` correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/volerrors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsd/Makefile.in -->
# sources/distributed-fs/openafs/src/afsd/Makefile.in

Purpose: automake-style template for building and installing OpenAFS client daemons/utilities: kernel `afsd`, optional FUSE `afsd.fuse`, and `vsys`.

Important APIs/targets: includes `Makefile.config`, `Makefile.pthread`, and `Makefile.version`. Targets include `all`, `afsd`, `afsd.fuse`, `vsys`, object rules, `clean`, `install`, `dest`, and `system`. Library groups are `AFSLIBS`, `UAFSLIBS`, `FUSE_LIBS`, `AFSD_LIBS`, crypto/roken/thread libs, and AIX-only `AFSD_KERNEL_LDFLAGS`.

Control flow: `all` builds `afsd`, `vsys`, and optionally FUSE. `afsd` links `afsd.o` and `afsd_kernel.o` statically with auth/cmd/sys/util/opr libraries. `afsd.fuse` compiles with UKERNEL and FUSE flags and links `libuafs.a`. `install` writes binaries to `${sbindir}`; `dest` writes legacy client tree paths and OS-specific rc scripts/configs based on `${SYS_NAME}`.

State and persistence: build output includes binaries and objects; install/dest persist daemons, `vsys`, and platform startup scripts into package/image directories.

Dependencies and integration points: ties user-space daemon build to libafs syscall export on AIX, UKERNEL/libuafs for FUSE, and platform rc script inventory in `src/afsd`. The daemon configures the cache manager whose kernel code is represented by the `afs` source files in this group.

Risks: platform case patterns must match configured `SYS_NAME`; missing rc script paths break packaging. Static link library order matters. FUSE build depends on substituted `@ENABLE_FUSE_CLIENT@`, `@FUSE_CFLAGS@`, and `@FUSE_LIBS@`. AIX needs `afsl.exp` import for syscall linkage.

Test signals: build default, FUSE-enabled, and AIX variants; run `make install DESTDIR=...` and `make dest DEST=...` staging checks; verify clean removes generated binary/object/version files; check OS rc script selection for Linux, Darwin, FreeBSD, Solaris, HPUX, AIX, and SGI names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsd/Makefile.in -->
