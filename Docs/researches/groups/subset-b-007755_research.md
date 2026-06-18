# Research: subset-b-007755

Grouped research for OpenAFS `src/afs` vnode operation and shared state files. Each section preserves the source path and is bounded by reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_lookup.c -->
## sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_lookup.c

Purpose: Implements the AFS lookup vnode operation plus mountpoint resolution, fakestat substitution, `@sys` expansion, dynroot lookup, and directory-neighbor bulk status prefetch. This file is the main name-to-vcache bridge for the cache manager.

Important APIs, types, and functions: `afs_lookup` is the exported vnode lookup entry. `EvalMountData` parses mountpoint text, cell references, numeric volume IDs, vnode/unique suffixes, readonly/backup preferences, and linked-cell fallback. `EvalMountPoint` resolves mountpoint vcaches into target volume root FIDs. `afs_InitFakeStat`, `afs_EvalFakeStat`, `afs_TryEvalFakeStat`, and `afs_PutFakeStat` implement fakestat lifetime around mountpoint-to-root substitution. `afs_ENameOK`, `Check_AtSys`, `Next_AtSys`, and `afs_AtSys_SetType` implement `@sys` validation and iteration. `afs_DoBulkStat` and `afs_ShouldTryBulkStat` opportunistically create and populate vcaches using `RXAFS_InlineBulkStatus` or `RXAFS_BulkStatus`.

Control flow: `afs_lookup` creates a `vrequest`, enters the disconnected lock, optionally fakestats the parent, verifies parent status, handles `"."`, `".."`, dynroot mount directory names, static dynroot mount redirection, DNLC hits, and directory blob lookup via `afs_dir_LookupOffset`. Misses can retry for dynroot AFSDB discovery or readonly directory cache refresh. If the target is not already statted, lookup may call `afs_DoBulkStat` before falling back to `afs_GetVCache` or `afs_LookupVCache`. Mountpoint targets are evaluated when forced by fakestat settings or cached `CMValid` metadata. Successful lookups enter the DNLC unless the result is an unevaluated mountpoint or a direct cache hit.

State and persistence behavior: The code updates vcache parent hints, `CMValid`, mountpoint target roots, volume `dotdot` and `mtpoint`, `last_looker`, callback state, and DNLC entries. Bulk stat temporarily stores a sequence number in `f.m.Length` while `CBulkFetching` is set, then merges status only if the sequence still matches. It also updates `CBulkStat`, `CTruth`, `CStatd`, `CRO`, `CBackup`, and `CForeign`. No durable on-disk state is written directly, but dcache/vcache metadata and callback queues are mutated.

Dependencies and integration points: Depends on vcache/dcache locking, directory package calls, `afs_GetVolume*`, `afs_GetVCache`, callback queues, RX fileserver RPCs, `afs_Analyze`, DNLC APIs, dynroot APIs, NFS exporter `EXP_SYSNAME`, global sysname state, and platform-specific vnode finalization for Darwin.

Risks and edge cases: Bulk stat is race-sensitive and deliberately conservative; misuse of `f.m.Length` while `CBulkFetching` is set would corrupt file size semantics. Lookup suppresses internal `ENOENT` in many paths to avoid negative-cache poisoning. Mountpoint parsing temporarily edits strings in place. `@sys` expansion allocates large-space buffers and must free only when ownership changed. Lock ordering across vcache, dcache, callback hash, and global vcache locks is complex. Dynroot and fakestat paths return different errors depending on whether network I/O is allowed.

Test signals: Exercise lookup of `.`, `..`, volume roots, mountpoints, dynroot cells, dynroot mount names, `cell:volume` numeric names, cross-cell mountpoints, backup/readonly volume preference, `@sys` and suffix-`@sys` names, DNLC hit/miss paths, bulk stat enabled/disabled/stressed/offline cases, readonly retry after stale directory data, and error translation through `afs_CheckCode`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_open.c -->
## sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_open.c

Purpose: Implements `afs_open`, the vnode open path for files, directories, symlinks, and mountpoint fakestat targets.

Important APIs, types, and functions: `afs_open` creates a `vrequest`, resolves fakestat mountpoints with `afs_EvalFakeStat`, verifies status with `afs_VerifyVCache`, checks directory and NFS-translator access with `afs_AccessOK`, flushes text/pages for non-directories, updates open and writer counters, and optionally queues background prefetch with `afs_BQueue(BOP_FETCH)`.

Control flow: The function gets the current vcache from platform-specific arguments, enters the disconnected lock, evaluates fakestat, verifies cache status, rejects disconnected opens when chunks are missing, classifies write intent using `FWRITE` and `FTRUNC`, and applies directory-specific rules. Directories cannot be opened for write and require lookup or read access depending on `CForeign`. Regular files and symlinks have text and pages flushed before use. Truncating opens update the cached mtime and mark `CDirty`. Finally it increments `opens` and, for write opens, `execsOrWriters`; read opens can trigger a first-chunk asynchronous prefetch.

State and persistence behavior: Mutates `tvc->opens`, `tvc->execsOrWriters`, `tvc->f.m.Date`, `CDirty`, and platform credential fields such as `tvc->cred` or `tvc->credp`. It may set `DFFetchReq` on a dcache entry and enqueue a background fetch. It does not persist file data to the server; later write, close, and fsync paths handle that.

Dependencies and integration points: Integrates with fakestat helpers from lookup, disconnected-mode checks, dcache chunk presence checks, access cache logic, page/text flushing OS hooks, background daemon request queues, dcache locks, and platform vnode wrappers for SGI/Linux/FreeBSD/AIX behavior.

Risks and edge cases: The function relies on other vnode paths for permission checks before open, except for directory and NFS translator cases. Missing chunks during disconnected mode fail even for otherwise valid status. Open-truncate marks metadata dirty but does not itself store data. Background prefetch must correctly transfer the dcache reference to the daemon only when queued. Counter and credential updates are protected by vcache locks and are sensitive to platform-specific open/close semantics.

Test signals: Open directories read-only and write, regular files for read/write/truncate, mountpoints under fakestat, disconnected files with complete and missing chunks, NFS translator read access, first-chunk prefetch when daemons are idle, busy background queue fallback, and matching close counter decrements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_read.c -->
## sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_read.c

Purpose: Implements cached file reads, read-ahead prefetch, and low-level reads from the configured UFS/memory cache backend.

Important APIs, types, and functions: `afs_read` is the main read path, selected by `afs_rdwr` and platform vnode wrappers. `afs_PrefetchChunk` queues asynchronous fetches for the next chunk. `afs_UFSReadUIO` opens a cache file with `osi_UFSOpen` and dispatches to platform-specific `VOP_READ`, `VNOP_READ`, `VNOP_RDWR`, or `osi_rdwr`.

Control flow: `afs_read` creates a request, verifies the vcache unless `noLock` is set, checks NFS translator read access, then iterates from the uio offset across chunks. For each chunk it obtains or finds a dcache entry, waits for current fetches when needed, starts a background fetch when useful, falls back to synchronous `afs_GetDCache` if background fetch cannot start, and copies data from the cache backend into a partial uio. Short or sparse chunk regions are zero-filled using `afs_zeros`. After the loop, it releases the final dcache, may call `afs_PrefetchChunk`, checks the final error with `afs_CheckCode`, and destroys the request.

State and persistence behavior: Reads do not modify server state. They update uio offsets/residuals, may wait on `tdc->validPos`, may set `DFFetchReq` or `DFNextStarted`, and use `DFFetching` plus dcache `versionNo` to decide whether cached bytes are current. They also respect `avc->vc_error` as a sticky writeback/read failure.

Dependencies and integration points: Depends on chunk macros, dcache freshness checks, background daemon queues, dcache locks and mflags, cache backend `afs_cacheType->vreadUIO`, OS-specific cache-file VOPs, NFS translator credential checks, disconnected locks, and uio helper routines such as `afsio_partialcopy`, `afsio_skip`, and `afsio_free`.

Risks and edge cases: The EOF zero-fill pre-loop is effectively disabled by setting `len` to zero, so correctness depends on the chunk loop handling partial EOF. Waiting on `DFFetching` and `DFFetchReq` requires precise lock release and reacquire ordering. Reads with `noLock` bypass verification and use `afs_FindDCache`, so callers must already have coherence guarantees. Background daemon saturation changes behavior to synchronous fetch. Cache backend errors are surfaced as `EIO` or translated errors.

Test signals: Read fully cached chunks, uncached chunks, concurrent fetch-in-progress chunks, EOF and partial EOF reads, sparse/zero-fill regions, background prefetch success and queue-full fallback, disconnected reads with unavailable dcache, NFS translator access denial, `noLock` VM reads, and platform cache backend read failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_readdir.c -->
## sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_readdir.c

Purpose: Implements directory iteration over AFS/Vice directory blobs and translates AFS directory entries into each platform's `dirent` representation.

Important APIs, types, and functions: `BlobScan` skips page headers and free blobs using the directory page allocation bitmap. `afs_readdir_type` infers BSD/Darwin `d_type` from vnode parity or cached vcache status. `afs_readdir_move` serializes one `DirEntry` into the caller's uio with correct inode number, record length, name length, type, offset, and padding. `afs_readdir` and `afs_readdir2` drive the directory read.

Control flow: `afs_readdir` creates a request, evaluates fakestat, verifies the directory vcache, fetches the full directory dcache at chunk zero, waits for current data, and then iterates from the opaque uio offset. The loop uses `BlobScan` and `afs_dir_GetVerifiedBlob` to look ahead one entry, so it can size the previous entry to fill the user buffer exactly when the next entry will not fit. On EOF it returns any held previous entry, releases dcache/vcache locks, and sets `eofp` where the platform API expects it.

State and persistence behavior: Readdir is read-only for server data, but it depends on fresh dcache state and `CStatd`. It consumes and updates uio offset/residual as an opaque blob cursor. It may consult volume `mtpoint` and vcache `mvid.parent` to report stable inode numbers for `.` and `..` across volume roots and mountpoints. The broader system tracks in-progress readdir with `CReadDir`, `readdir_pid`, and `dcreaddir`, which lookup and bulk stat use to avoid deadlocks.

Dependencies and integration points: Integrates with the AFS directory package, dcache freshness and lock rules, fakestat helpers, volume lookup, `afs_calc_inum`, platform `dirent` layouts, `AFS_UIOMOVE`, and vnode type information cached by lookup/bulk stat. Linux has a separate implementation, so changes that affect shared semantics must be mirrored there.

Risks and edge cases: The code carries many platform-specific layout assumptions. Small user buffers can return `EINVAL` when no entry fits. Correct `.` and `..` inode reporting across root volumes and mountpoints is subtle and depends on cached parent and volume state. Directory offsets are AFS blob indices, not byte offsets. If dcache data becomes stale while locks are reacquired, the function retries from verification.

Test signals: Readdir root volumes, mountpoint targets, dynroot-style directories, buffers that hold zero/one/many entries, EOF offset handling, long names, platform `d_type` reporting, stale dcache retry, concurrent directory fetch, `.` and `..` inode stability, and HPUX/SGI/Sun/BSD layout-specific record sizing where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_readdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_remove.c -->
## sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_remove.c

Purpose: Implements file removal, local directory cache updates, disconnected remove logging, and final deletion of silly-renamed open files.

Important APIs, types, and functions: `afs_remove` is the vnode remove entry. `afsremove` performs the connected `RXAFS_RemoveFile` call or disconnected local removal and updates the parent dcache. `afs_newname` creates a hidden `.__afs` silly-rename target for open unlinked files. `afs_remunlink` removes that silly name after the last reference is gone. `FetchWholeEnchilada` fetches all chunks before unlinking an active file, and `DemoteSmushedVCache` moves flushed vcaches to the VLRU tail.

Control flow: `afs_remove` creates a request, fakestats the parent, rejects dynroot mount writes and readonly/offline-without-disconnected-RW cases, verifies the parent, gets the directory dcache, locks the parent and dcache, ensures freshness, and finds the target vcache through DNLC or directory lookup. In disconnected RW mode it shadows the parent directory and records `VDisconRemove`, unless the target was locally created. Active open files are fetched whole, then either silly-renamed with `afsrename` or removed with `afsremove`. `afsremove` removes DNLC entries, performs the fileserver RPC when connected, applies `afs_LocalHero` or local disconnected directory deletion, decrements link counts, smushes inactive last-link files, and demotes smushed vcaches.

State and persistence behavior: Connected removes synchronously persist via fileserver RPC. Local dcache directory entries are deleted when server status proves the cached directory version advanced as expected. Disconnected removes mutate shadow directories and dirty flags for later replay. Open unlinked files store `mvid.silly_name`, `uncred`, `CUnlinked`, and sometimes `CUnlinkedDel` until `afs_remunlink` performs final removal.

Dependencies and integration points: Depends on `afsrename` from rename handling, directory package deletion, DNLC removal, dcache/vcache locks, fileserver `RXAFS_RemoveFile`, `afs_Analyze`, disconnected dirty queues, shadow directory helpers, credential refcounting, active-vnode checks, and cache smushing.

Risks and edge cases: Lock ordering is delicate, especially disconnected mode where target vcache locks are obtained while parent locks are held. If a fileserver RPC returns a negative/network error, the parent is marked stale because server state may be ambiguous. `afs_newname` uses a 16-bit random suffix, so rare collisions rely on rename failure handling. Silly-rename cleanup may be called with an unheld vcache and uses nonblocking locks, so cleanup is best effort in some paths.

Test signals: Remove ordinary files, active open files, inactive last-link files, DNLC hit and miss targets, readonly directories, disconnected non-RW and RW modes, locally-created disconnected files, silly rename collision/failure, final `afs_remunlink`, NFS translator behavior, and server/network errors that should stale parent cache state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_remove.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_rename.c -->
## sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_rename.c

Purpose: Implements rename across one or two AFS directories, including connected fileserver RPCs, disconnected replay logging, local directory cache surgery, target unlink accounting, and moved-directory parent handling.

Important APIs, types, and functions: `afs_rename` is the vnode wrapper that creates the request and resolves fakestat for old and new parent directories. `afsrename` contains the main implementation. It uses `RXAFS_Rename`, `afs_dir_Lookup`, `afs_dir_Delete`, `afs_dir_Create`, `afs_LocalHero`, `afs_DisconAddDirty`, `afs_MakeShadowDir`, and `afs_dir_ChangeFid`.

Control flow: `afsrename` allocates output status buffers, validates name lengths, verifies old and new parents, rejects cross-volume renames, handles same-directory same-name as a no-op, locks parents in vnode-number order to reduce deadlock risk, obtains old and new directory dcaches, removes DNLC entries, and verifies dcache freshness. Connected mode performs `RXAFS_Rename` through `afs_Analyze`. Disconnected RW mode finds the moved file vcache, creates a parent shadow if needed, saves the old parent, and records `VDisconRename` plus `VDisconRenameSameDir` when applicable. After a successful operation, it locally deletes the source entry, deletes any existing target entry, creates the destination entry, updates link counts, handles overwritten target link-count/smush behavior, and invalidates or rewrites `..` for moved directories.

State and persistence behavior: Connected renames are synchronously persisted by the fileserver. Directory dcache updates are kept only when server status and data-version expectations match; otherwise dcache entries are zapped. Disconnected renames persist intent in dirty flags and shadow metadata for later replay. Parent hints in `f.parent` and moved-directory cached `..` entries are updated or invalidated.

Dependencies and integration points: Integrates with fakestat, vcache/dcache locking, DNLC, fileserver rename RPC, directory package operations, disconnected dirty replay infrastructure, callback invalidation, volume status bits, and remove semantics for overwritten targets.

Risks and edge cases: The code intentionally calls its local update block "loathsome" because success does not guarantee cached directories are current enough to edit safely. Cross-directory locking and dcache acquisition order are complex. Disconnected mode locks moved vcaches while holding directory locks. Same-directory target replacement must preserve correct link counts. If an RPC fails after partially executing on the server, both directories are marked stale.

Test signals: Same-name no-op, same-directory rename, cross-directory rename, cross-volume `EXDEV`, readonly parents, disconnected non-RW and RW rename, target overwrite, moved directories with `..`, cache-local update accepted/rejected by `afs_LocalHero`, missing target dcache, RPC retry/failure, and DNLC invalidation for both old and new names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_rename.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_strategy.c -->
## sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_strategy.c

Purpose: Provides a legacy buffer strategy entry point for platforms that route VM/page I/O through buffer objects instead of directly through read/write vnode calls.

Important APIs, types, and functions: `afs_ustrategy` converts a `struct buf` into a one-element `uio` and dispatches to `afs_rdwr` or `afs_nlrdwr` for reads and writes. It handles platform-specific buffer fields such as `b_un.b_addr`, `b_data`, `b_saveaddr`, `b_blkno`, `b_lblkno`, `b_iocmd`, `b_flags`, and completion callbacks.

Control flow: The function extracts the vcache from `abp->b_vp`, chooses credentials from the caller or platform current user area, builds a kernel-space uio at the block offset, and branches on read versus write. Reads call `afs_rdwr(..., UIO_READ, ...)`, zero-fill any residual bytes in the buffer, and perform AIX page-protection handling beyond EOF. Writes compute the write length, sometimes trimming to current file length on AIX, and call `afs_rdwr(..., UIO_WRITE, ...)`. It records buffer errors on BSD-like platforms and calls the appropriate `iodone`, `biodone`, or `b_iodone`.

State and persistence behavior: This file does not maintain independent state. It drives normal read/write paths, so persistence is delegated to `afs_write`, close, fsync, and background store behavior. Buffer residuals and error fields are updated according to platform requirements.

Dependencies and integration points: Compiled only when not using HPUX, SGI, Linux, or Darwin80-specific alternatives. Depends on `afs_rdwr` wrappers in `afs.h`, platform buffer layouts, uio setup macros, credential APIs, and kernel I/O completion functions.

Risks and edge cases: Correct block offset calculation is platform-specific and differs for `b_blkno` versus `b_lblkno`. Credential selection from global user state is noted as questionable in comments. Residual zero-fill must use the correct buffer address field. Some platforms need explicit buffer error flags while others rely on completion callbacks. This path can mask errors if callers ignore `b_error`.

Test signals: Platform build coverage, buffer reads before/after EOF, residual zero-fill, buffer writes at block offsets, error propagation to `b_error` and `B_ERROR`, completion callback invocation, AIX credential and page-protection paths, and consistency with direct `afs_read`/`afs_write`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_strategy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_symlink.c -->
## sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_symlink.c

Purpose: Implements symlink creation, symlink target caching, mountpoint text handling, and readlink.

Important APIs, types, and functions: `afs_symlink` creates new symlinks or mountpoints. `afs_DisconCreateSymlink` writes disconnected symlink contents to a cache chunk. `afs_MemHandleLink` and `afs_UFSHandleLink` load symlink or mountpoint text into `vcache->linkData` from memory or UFS cache backends. `afs_readlink` verifies and returns cached link text through `AFS_UIOMOVE`.

Control flow: `afs_symlink` creates a request, fakestats the parent, checks name and target lengths, handles dynroot symlinks or readonly dynroot mount failures, verifies parent status, rejects readonly/offline-without-RW cases, prepares store status mode bits, and gets the parent directory dcache. Connected mode calls `RXAFS_Symlink` or `RXAFS_DFSSymlink` for foreign cells. Disconnected RW mode generates a fake FID. If the directory can be updated locally, it inserts the new name in the parent dcache. It then creates a new vcache under `afs_xvcache`, sets callback/status state, processes server status or generates disconnected status, stores `linkData`, and returns or releases the new vcache. `afs_readlink` verifies/fakestats the vnode, requires `VLNK`, calls `afs_HandleLink`, and copies the string to the caller.

State and persistence behavior: Connected symlink creation is persisted synchronously by the fileserver. Disconnected creation writes the target into the local dcache chunk, marks the vcache dirty with `VDisconCreate`, and relies on replay. `linkData` caches a null-terminated target string. Mountpoint-style targets starting with `#` or `%` and ending in `.` are stored with mode `0644`; ordinary symlinks use `0755` and include a terminating null.

Dependencies and integration points: Depends on fileserver symlink RPCs, directory dcache updates, `afs_LocalHero`, callback queues, volume references, cache backends, dynroot hooks, disconnected status generation, fakestat, and `afs_HandleLink`, which selects memory or UFS link loading through cache type integration.

Risks and edge cases: Link target loading rejects cached link data longer than 1024 bytes. The creation path holds global vcache state while initializing the new vcache, so callback and vcache lock ordering matters. In disconnected mode, failure after parent directory insertion is called out as needing cleanup. Mountpoint text conventions depend on mode bits and trailing dot handling. Foreign symlink creation has callback expiration behavior that ordinary symlinks do not.

Test signals: Create ordinary symlinks, mountpoint-style symlinks, long names/targets, dynroot symlink creation, readonly and disconnected failures, disconnected RW creation and replay flags, local directory cache update success/failure, readlink cache hit/miss for UFS and memory cache, non-link readlink `EINVAL`, and foreign/DFS callback handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_write.c -->
## sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_write.c

Purpose: Implements cached writes, cache-backend write I/O, partial stores under dirty-cache pressure, close-time storeback, and fsync.

Important APIs, types, and functions: `afs_write` is the main write path. `afs_UFSWriteUIO` writes to the configured disk cache file through OS VOPs or `osi_rdwr`. `afs_StoreOnLastReference` stores all dirty segments on last writer close or records disconnected write-close state. `afs_DoPartialWrite` calls `afs_StoreAllSegments` when dirty chunks exceed the configured limit. `afs_close` handles writer/read close accounting, background stores, error reporting, lock cleanup, and text flushes. `afs_fsync` synchronously stores data or records disconnected write-flush intent.

Control flow: `afs_write` rejects sticky vnode errors and disconnected non-RW writes, creates a request, locks the vcache unless `noLock`, handles append mode, updates mtime, fake-opens the file for write-token semantics, and loops across chunks. Each iteration obtains a writeable dcache, bounds the transfer to the chunk, writes through `afs_cacheType->vwriteUIO`, updates chunk size/valid position/file length, releases the dcache, and may trigger partial storeback. On backend write failure it zaps and truncates the dcache chunk and clears dirty index flags. `afs_close` evaluates fakestat, releases file locks, and for write closes either stores immediately or queues `BOP_STORE`; it then reports deferred write errors and decrements counters. `afs_fsync` stores all segments under `AFS_SYNC` or records `VDisconWriteFlush`.

State and persistence behavior: Writes first persist to the local cache, marking `CDirty`, `IFDataMod`, chunk sizes, valid positions, file length, and mtime. Connected persistence to the fileserver occurs during partial write, fsync, close, background store, or last-reference store. Disconnected RW writes record dirty flags such as `VDisconWriteClose` and `VDisconWriteFlush`. Sticky `vc_error` carries writeback failures to later close/fsync/read callers.

Dependencies and integration points: Depends on dcache allocation for writing, cache backend ops, `afs_StoreAllSegments`, background daemon `BOP_STORE`, fake-open/close macros from `afs.h`, VM/page flushing hooks, disconnected dirty queues, credential refcounting, and platform-specific VOP write APIs.

Risks and edge cases: Fake-close stores credentials in `linkData` while `CCore` is set, so symlink/linkData use must not overlap. Close-time background store transfers errors through `brequest` fields and must wake sleepers correctly. Dirty-cache pressure can force storeback during a write. Backend write errors must clean dcache and dirty accounting consistently. `afs_close` must return deferred quota/ENOSPC errors even if another thread performed the actual store.

Test signals: Write within one chunk, across chunks, append writes, extending file length, disconnected non-RW and RW writes, backend write failure cleanup, dirty-cache partial store, close with synchronous and background store, close after deferred write error, fsync with writers, quota/ENOSPC reporting, sticky `vc_error`, and platform-specific sync flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs.h -->
## sources/distributed-fs/openafs/src/afs/afs.h

Purpose: Defines core OpenAFS cache-manager constants, state bits, structures, queues, cache metadata, vnode/dcache contracts, background operation opcodes, and helper macros shared by the VNOPS implementation.

Important APIs, types, and functions: Key types include `struct VenusFid`, `struct vrequest`, `struct cell`, `struct unixuser`, `struct afs_conn`, `struct server`, `struct volume`, `struct fvcache`, `struct vcache`, `struct fcache`, `struct dcache`, `struct brequest`, `struct afs_fakestat_state`, `struct storeOps`, and `struct fetchOps`. Important macros include queue operations `QAdd`, `QRemove`, `QTOV`; fid comparisons `FidCmp` and `FidMatches`; store flags `AFS_SYNC`, `AFS_LASTSTORE`, `AFS_NOVMSYNC`; background opcodes `BOP_FETCH`, `BOP_STORE`, `BOP_PARTIAL_STORE`; vcache state bits such as `CStatd`, `CDirty`, `CMValid`, `CUnlinked`, `CBulkStat`, `CBulkFetching`; disconnected flags such as `VDisconRemove`, `VDisconCreate`, `VDisconRename`, `VDisconWriteClose`; dcache flags `DFFetching`, `DFFetchReq`, `DFNextStarted`; and read/write wrappers `afs_rdwr` and `afs_nlrdwr`.

Control flow: This header has no standalone runtime flow, but its macros define how vnode paths select read versus write functions, how fake-open/fake-close increments writer counters and defers last-writer storeback with `CCore`, how vcache verification fast-paths `CStatd`, how queue entries are converted to containing structures, and how cache-full thresholds are computed.

State and persistence behavior: `struct fvcache` captures persistent vnode metadata such as FID, length, data version, owner, mode, link count, parent, truncation position, state bits, disconnected dirty flags, shadow vnode, and old parent. `struct vcache` layers runtime locks, callback state, access cache, open/writer counts, mountpoint/root/silly-name union, link data, readdir hints, dirty queues, and platform vnode state on top. `struct fcache` is stored in dcache entries and records chunk identity, data version, cache inode, chunk size, and flags. `struct dcache` tracks locks, valid bytes, refcounts, data flags, and meta flags.

Dependencies and integration points: Includes AFS syscall constants and parameter headers, depends heavily on platform compile-time environment macros, and is included by cache, callback, vnode, pioctl, daemon, fetch/store, and OS integration code. It exposes global tables such as `afs_indexTable`, `afs_indexUnique`, `afs_vhashT`, `afs_brs`, cache sizing counters, root FID, and callback statistics.

Risks and edge cases: Many macros mutate state without type or lock enforcement; callers must already hold the documented locks. `QRemove` assumes queue membership. `afs_FakeClose` stores credentials in `linkData` while `CCore` is active, creating implicit ownership coupling. `struct vcache` uses a union for silly unlink names, mountpoint target roots, and root parent FIDs, so `mvstat` and state bits must match the active field. Platform conditionals change structure layout and vnode reference semantics. Persistent cache header versioning must stay compatible with cache file formats.

Test signals: Build all supported platform configurations, validate vcache/dcache lock invariants, exercise fake-open/fake-close with last and non-last writer, cache-full threshold behavior, queue add/remove consistency, disconnected dirty flag replay, dcache fetch/write flags, bulk stat state bits, FID matching with zero unique/CUnique, and cache header migration or invalidation when persistent formats change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs.h -->
