# Research: subset-b-000539

Grouped research for BeeGFS client module filesystem inode, directory, export, file, and native file operation sources. Each section preserves the source path and is wrapped for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsInode.c -->
## sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsInode.c

**Purpose:** Implements the BeeGFS-specific state machine attached to each Linux `struct inode`: inode-cache lifecycle hooks, shared remote file-handle reference counting, stripe-pattern ownership, lock-PID tracking, cache locks, reproducible inode-number generation, and short-lived subentry cache validity checks. This is the central implementation backing the inline state declared in `FhgfsInode.h` and used by VFS open/read/write/lock/export paths.

**Important APIs/types/functions:** `FhgfsInode_initOnce`, `FhgfsInode_allocInit`, and `FhgfsInode_destroyUninit` manage slab-cache lifetime for locks, maps, file handle slots, `EntryInfo`, `PathInfo`, stripe patterns, and per-handle `BitStore`s. `FhgfsInode_referenceHandle` maps BeeGFS open flags to `FileHandleType`, reuses matching/RW handles, handles lookup-intent pre-opened handles, opens remote files through `FhgfsOpsRemoting_openfile`, updates path info and stripe patterns, initializes `firstWriteDone`, emits open/truncate file events, and optionally fetches a file version. `FhgfsInode_releaseHandle` drops a reference, sends async-retry close on the last reference, emits close-write events, frees the remote handle ID, resets append-lock cleanup state, max-used target index, and per-stripe write bits. Supporting functions include `FhgfsInode_hasWriteHandle`, `FhgfsInode_addRangeLockPID`, `FhgfsInode_removeRangeLockPID`, `__FhgfsInode_openFlagsToHandleType`, `__FhgfsInode_referenceTrunc`, `__FhgfsInode_initOpenIOInfo`, `FhgfsInode_getRefIOInfo`, file-cache lock wrappers, `Fhgfsinode_getFileCacheBuffer`, `FhgfsInode_generateInodeID`, and `FhgfsInode_isCacheValid`.

**Control flow:** New inode objects are initialized in two phases: one-time lock/map setup and per-allocation reset of entry/path/file-handle/cache/writeback fields. Open flows enter with `fileHandlesMutex`, select a desired handle type, either increment an existing refcount after optional truncate/version operations or prepare `RemotingIOInfo`, possibly ignore a stale stripe pattern, take an `entryInfo` read lock, send an open RPC, and install returned handle/pattern state. Release is symmetric: under `fileHandlesMutex`, decrement the chosen handle refcount; on transition to zero, build close `RemotingIOInfo`, take `entryInfo` read lock, send close with async retry, then free handle-local resources. Range-lock PID helpers serialize map updates with `rangeLockPIDsMutex`. Cache validity compares `dataCacheTime` against configured dir/file subentry cache windows.

**State and persistence behavior:** The file does not persist durable data itself, but it controls in-memory consistency for remote BeeGFS objects. Persistent identity is represented by `EntryInfo` and remote file handles; VFS inode numbers are reproducible hashes of BeeGFS entry IDs using the configured hash style. `pattern` is owned by the inode after open and freed on destroy or stale replacement. `fileHandles[]` share remote handles across multiple VFS file instances and keep append-cleanup, target-write, and first-write-per-stripe hints. `rangeLockPIDs` records TGIDs that used range locking so close can clean up remote locks. `fileCacheBuffer` is protected by the inode file-cache RW lock.

**Dependencies and integration points:** Depends on `App`, `Config`, `Logger`, `EntryInfo`, `PathInfo`, `StripePattern`, `RemotingIOInfo`, `FhgfsOpsRemoting`, `FhgfsOpsHelper`, `BitStore`, `IntMap`, BeeGFS event logging, and Linux inode/superblock APIs. It is called by `FhgfsOpsFile.c`, `FhgfsOpsFileNative.c`, `FhgfsOpsPages.c`, NFS export reconstruction, inode refresh logic, and worker writeback code.

**Risks:** Handle refcounting and stripe-pattern replacement are protected by `fileHandlesMutex`; callers that use returned `RemotingIOInfo` after releasing a handle risk stale handle IDs or pattern pointers. `FhgfsInode_getStripeCount` assumes `pattern` is non-NULL. Close errors still consume the last local reference, so recovery relies on async retry and higher-level flush/error propagation. The inode-number hash is reproducible but not collision-free. Open event selection sends at most one open event, with truncate overriding the earlier open event when both masks apply. `FhgfsInode_isCacheValid` is time-based and intentionally may serve stale metadata within configured windows.

**Test signals:** Exercise open/reuse/release for read/write/RW handles, lookup-intent opens, truncating an already-open handle, stale stripe-pattern replacement, close-write event emission, version fetch, range-lock PID add/remove idempotence, inode hash reproducibility and reserved-ID avoidance, cache-validity timing for dir/file/disabled settings, and failure paths for remote open/close/truncate. Kernel tests should include concurrent opens/releases and page/writeback paths using `FhgfsInode_getRefIOInfo`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsInode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsInode.h -->
## sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsInode.h

**Purpose:** Declares and largely inlines the BeeGFS inode extension that embeds Linux `struct inode`, exposes handle/cache/lock helpers, defines inode flags and small cache structures, and centralizes UID/GID and attribute conversion across multiple kernel ID-mapping eras. It is the public contract used by inode, file, page-cache, export, remoting, and helper code in the client module.

**Important APIs/types/functions:** Constants include root inode number `BEEGFS_INODE_ROOT_INO`, handle-slot count, and inode flags for write errors, paged writes, and stale stripe patterns. `FileHandleType` indexes read/RW/write remote handles; `FileBufferType` classifies internal file cache buffers; `CacheBuffer` tracks buffer pointer, used/max length, file offset, and type; `FhgfsIsizeHints` carries remote-stat i_size suppression hints. `FhgfsInodeFileHandle` stores remote handle ID, refcount, append-lock cleanup flag, max-used target index, and `firstWriteDone` bitset. `FhgfsInode` embeds `struct inode` and adds `EntryInfo`, `PathInfo`, parent node ID for NFS export, data-cache time, handle/lock maps, append mutex/counter, file cache lock/buffer, dirty-page and writeback counters, no-i_size-decrease state, flags, file/meta versions, modified/coherent-RW atomics, and optional idmapped mount context. Inline APIs cover entry-info locking/update, open-state queries, dirty-page counters, writeback/i_size hints, stale-pattern flags, append lock, parent node ID, UID/GID mapping, `kstat` conversion, and `iattr` conversion.

**Control flow:** Callers usually cast `struct inode*` with `BEEGFS_INODE`, take `entryInfo` locks before reading mutable parent/name/owner fields, and use file-handle APIs from `FhgfsInode.c` for remote I/O. Root `EntryInfo` initialization is lazy: `FhgfsInode_entryInfoReadLock` and write lock call `_FhgfsInode_initRootEntryInfo`, which obtains root metadata once and marks the superblock as initialized. Rename/update helpers assume the caller already holds the write lock. i_size hint helpers inspect writeback counters, dirty/writeback tags, and writable mmap state to decide whether remote stat results may shrink `i_size`. ID-mapping helpers select `mnt_idmap`, `mnt_userns`, or init-userns paths according to compile-time kernel capabilities and `BEEGFS_DISABLE_IDMAPPING`.

**State and persistence behavior:** The header defines in-memory state only. Durable metadata comes from BeeGFS `EntryInfo`, `fhgfs_stat`, and remote RPCs. `fileVersion` and `metaVersion` are local consistency tokens protected by `entryInfoLock`; native cache uses `fileVersion` to decide when to invalidate cached data, and lookup revalidation uses `metaVersion` to detect internal metadata changes such as stripe-pattern updates. `noRemoteIsizeDecrease`, `writeBackCounter`, dirty-page counters, and last-writeback time prevent stale server sizes from shrinking local file size while writes or mmap dirties may still be outstanding.

**Dependencies and integration points:** Includes BeeGFS common storage, threading, hashing, metadata, remoting, bitset, and Linux VFS headers. `OsTypeConv_kstatFhgfsToOs` and `OsTypeConv_iattrOsToFhgfs` are called by inode refresh/create and setattr paths. File ops, native ops, page ops, NFS export, and remoting worker code rely on these inline helpers, so ABI changes to `FhgfsInode` affect most of the client module.

**Risks:** Many inline helpers document locking assumptions but cannot enforce them. `FhgfsInode_getIsFileOpenByMultipleReaders` intentionally reads refcounts without locking and is only a hint. Root entry-info lazy initialization can briefly upgrade to a write lock from read/write lock entry points. ID-mapping code is highly kernel-version-sensitive; fallback mappings can silently use identity/init namespace behavior when newer helper macros are absent or idmapping is disabled. The non-ASCII comments in this file indicate prior manual edits; future kernel API changes around folios/idmapped mounts are likely regression points.

**Test signals:** Compile against the supported kernel matrix, especially 5.15-6.2 userns mounts and >=6.3 idmapped mounts. Test root entry-info lazy initialization, rename owner/mirroring updates, page-write/write-error/stale-pattern flag transitions, i_size hint suppression during dirty/writeback/mmap states, UID/GID conversion for idmapped and non-idmapped mounts, `kstat` conversion, and `iattr` conversion for mode/uid/gid/mtime/atime combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsInode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsDir.c -->
## sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsDir.c

**Purpose:** Implements BeeGFS dentry operations and path-buffer resolution. Its main job is dcache revalidation: decide whether cached dentries/inodes remain valid by using local cache windows, remote lookup-intent/stat RPCs, SELinux invalidation, and metadata-version cache-invalidation signals.

**Important APIs/types/functions:** `fhgfs_dentry_ops` installs `FhgfsOps_revalidateIntent` and `FhgfsOps_deleteDentry`. `FhgfsOps_revalidateIntent` is compiled with different signatures for stable-reference, atomic-open, and old `nameidata` kernels. `__FhgfsOps_revalidateIntent` performs the remote revalidation work. `FhgfsOps_deleteDentry` drops bad-inode dentries. `__FhgfsOps_pathResolveToStoreBuf` gets a fixed buffer from `NoAllocBufferStore` and calls `dentry_path_raw`.

**Control flow:** Revalidation rejects RCU-walk mode with `-ECHILD` because BeeGFS may sleep and needs parent access. Negative or bad dentries are dropped unless negative-entry caching is enabled and `dentry->d_time` is still within `tuneENOENTCacheValidityMS`; bad directory dentries also shrink child dcache unless submounts exist. Positive dentries pass to `__FhgfsOps_revalidateIntent`. That function first honors `FhgfsInode_isCacheValid` unless SELinux mode forces validation. It invalidates SELinux secctx when configured, then for non-root entries prepares `LookupIntentInfoIn` with parent entry info, current entry info, and inode `metaVersion`, calls `FhgfsOpsRemoting_lookupIntent`, updates entry feature flags on success, handles path-not-exists by dropping the dentry, maps successful stat data into `fhgfsStatPtr`, and calls `__FhgfsOps_refreshInode`. A metadata-version mismatch with cache invalidation enabled marks the stripe pattern stale if no file handle is open; if a handle is unexpectedly open, it marks the inode bad and invalidates cached pages as a defensive block.

**State and persistence behavior:** Dentry validity is controlled by Linux dcache state, `dentry->d_time` for negative caching, inode `dataCacheTime`, entry feature flags, inode `metaVersion`, and stripe-pattern stale flag. No durable state is written here, but remote lookup/stat results refresh local inode attributes and may invalidate local dcache/page-cache state.

**Dependencies and integration points:** Depends on `FhgfsOpsRemoting_lookupIntent`, `FhgfsOpsHelper_refreshDirInfoIncremental` indirectly through path consumers, `__FhgfsOps_refreshInode`, `FhgfsInode` entry locks and cache helpers, SELinux `security_inode_invalidate_secctx`, Linux dcache helpers, and `NoAllocBufferStore`. The exported `fhgfs_dentry_ops` is attached to BeeGFS dentries by superblock/inode/export paths.

**Risks:** Revalidation is a correctness boundary for stale metadata. Time-based positive/negative cache windows can intentionally serve stale entries. Lock ordering matters: parent entry read lock and child entry write lock are taken together during lookup-intent revalidation. The metadata-version mismatch path assumes stale stripe patterns can be safely handled only when no handle is open; the open-handle fallback makes the inode bad and can disrupt applications. `__FhgfsOps_pathResolveToStoreBuf` can deadlock if called twice by the same thread before returning buffers, as documented.

**Test signals:** Test positive dentry revalidation success, path-not-exists drop, remote/stat errors, negative dentry cache expiry and non-expiry, bad directory dentry pruning with/without submounts, RCU-walk fallback, SELinux secctx invalidation, cache-valid fast path, metadata-version mismatch with open and closed files, and path buffer acquisition/release behavior for long paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsDir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsDir.h -->
## sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsDir.h

**Purpose:** Provides the small public interface for BeeGFS dentry operations and dentry-to-path buffer resolution. It lets other filesystem components attach BeeGFS revalidation/delete behavior to dentries and resolve raw paths using the mount's no-allocation buffer store.

**Important APIs/types/functions:** Exports `fhgfs_dentry_ops`, a `struct dentry_operations` defined in `FhgfsOpsDir.c`, and `__FhgfsOps_pathResolveToStoreBuf(NoAllocBufferStore*, struct dentry*, char**)`, which returns either a path pointer inside the acquired store buffer or an `ERR_PTR` while setting `*outStoreBuf` to NULL on failure.

**Control flow:** Callers include this header when they need to set `d_op` on dentries obtained from lookup/NFS export paths or when they need a temporary path string without dynamic allocation. The path helper's contract requires callers to return the buffer to `NoAllocBufferStore` after successful use.

**State and persistence behavior:** The header owns no state. It exposes operations that manipulate Linux dcache state and borrow buffers from `NoAllocBufferStore`.

**Dependencies and integration points:** Depends on Linux `dcache.h` and BeeGFS `NoAllocBufferStore`. Included by export and other filesystem operation files that need `fhgfs_dentry_ops`.

**Risks:** The path helper uses a borrowed fixed-size buffer and can return `-ENAMETOOLONG`. Its implementation warns against taking two buffers in the same thread because the store can deadlock under pressure.

**Test signals:** Compile users across kernel versions, verify dentries receive BeeGFS ops when needed, and test path helper success, long-path failure, and buffer-return discipline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsDir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsExport.c -->
## sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsExport.c

**Purpose:** Implements Linux `export_operations` for BeeGFS NFS export and `open_by_handle` support on kernels >=2.6.29. It encodes BeeGFS entry identity into compact NFS file handles, decodes old and current handle formats, reconstructs dentries/inodes from local cache or metadata RPCs, finds parent dentries, and implements slow name lookup by scanning directory entries.

**Important APIs/types/functions:** `fhgfs_export_ops` wires `encode_fh`, `fh_to_dentry`, `fh_to_parent`, `get_parent`, and `get_name`. `FhgfsNfsHandleType` distinguishes V1, V2, V3, invalid, and buffer-too-small handles. `__FhgfsOpsExport_encodeNfsFileHandleV3` serializes parent entry ID, entry ID, owner node/group, parent owner, entry type, and buddy-mirroring into `FhgfsNfsFileHandleV3`. `FhgfsOpsExport_nfsFileHandleToDentry` and `FhgfsOpsExport_nfsFileHandleToParent` validate/upgrade handle formats and call `__FhgfsOpsExport_lookupDentryFromNfsHandle`. Helpers parse and rebuild BeeGFS entry IDs, get parent dentries, get child names, and scan directories for matching entry IDs.

**Control flow:** Encoding obtains the inode `EntryInfo` under read lock, parses parent and child entry IDs into counter/timestamp/node components, fills the packed V3 handle, stores parent owner if a connectable parent was supplied, records buddy mirroring, and zero-pads unused caller buffer space. Decoding validates handle type/length, converts V1/V2 into V3 shape, enables refresh-on-getattr on first NFS use, reconstructs entry ID strings, computes the reproducible inode hash, and tries `ilookup5`. On cache miss, it builds synthetic `EntryInfo`, calls `FhgfsOpsRemoting_statAndGetParentInfo`, retries with toggled mirroring for parent lookups that may cross mirrored/unmirrored boundaries, creates an inode with mapped `kstat`, records parent node/entry IDs, obtains an alias dentry, and attaches BeeGFS dentry ops where needed. `get_parent` similarly uses cached parent ID or remote stat-and-parent-info. `get_name` scans the parent directory incrementally until a matching child entry ID is found.

**State and persistence behavior:** NFS handles persist BeeGFS identity, owner node/group, entry type, and mirroring in packed on-wire structures independent of current dcache state. The decode path may populate local inode cache, update `parentNodeID`, and update `EntryInfo.parentEntryID` from server-provided parent info. It does not change server metadata.

**Dependencies and integration points:** Depends on Linux exportfs, dcache/inode aliasing, BeeGFS `EntryInfo`, `Metadata`, `FhgfsInode`, inode creation helpers, remoting stat/parent RPCs, ID conversion, directory incremental refresh, and `fhgfs_dentry_ops`. NFS export behavior forces `tuneRefreshOnGetAttr` because NFS can bypass lookup-intent assumptions.

**Risks:** Handles depend on parseable BeeGFS entry ID format except for root. V1/V2 compatibility paths lack newer information and infer missing fields. Parent reconstruction may fail with `-ESTALE` if owner node is unknown and not the child's owner. Mirroring retry is heuristic. `get_name` is intentionally slow because it scans client-side readdir results. The decode error path must free generated entry strings and uninit synthetic `EntryInfo`; leaks or stale pointers here would affect long-running NFS servers.

**Test signals:** Test handle buffer-too-small sizing, V3 encode/decode round-trip, V1/V2 decode compatibility, root handle handling, mirrored/unmirrored parent retries, cache-hit `ilookup5` and cache-miss inode creation, parent dentry reconstruction, `get_name` success/failure over incremental readdir, refresh-on-getattr side effect on first NFS access, and stale/error mappings to `ERR_PTR(-ESTALE)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsExport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsExport.h -->
## sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsExport.h

**Purpose:** Declares BeeGFS NFS export support and the packed handle formats used by `FhgfsOpsExport.c`. The header is compiled only for kernels new enough to support exportfs operations.

**Important APIs/types/functions:** Exports `fhgfs_export_ops`, `FhgfsOpsExport_encodeNfsFileHandle` with kernel-version-dependent signature, `FhgfsOpsExport_nfsFileHandleToDentry`, `FhgfsOpsExport_nfsFileHandleToParent`, `FhgfsOpsExport_getName`, `FhgfsOpsExport_getParentDentry`, and internal helpers for handle lookup and entry-ID parse/rebuild. It defines packed `FhgfsNfsFileHandleV1`, `FhgfsNfsFileHandleV2`, and `FhgfsNfsFileHandleV3`. V1 stores parent/entry ID components, owner node, and entry type. V2 adds parent owner node. V3 changes owner fields to `NumNodeID` and adds `isBuddyMirrored`.

**Control flow:** NFS/exportfs callers receive function pointers through `fhgfs_export_ops`; encode/decode paths exchange one of the packed handle structures through Linux `fid` buffers. The V3 structure is the current full-fidelity format; V1/V2 remain decode-compatible.

**State and persistence behavior:** These packed structures are persistent file-handle ABI for NFS clients. Field layout and handle type values must remain backward-compatible. The header does not own runtime state, but its structs determine what identity survives across NFS handle encode/decode cycles.

**Dependencies and integration points:** Depends on `common/Common.h` for kernel version macros and `linux/exportfs.h`. It is included by export implementation and any code needing export operation declarations.

**Risks:** Packed ABI changes can invalidate existing NFS file handles. V1/V2 contain 16-bit owner/node fields while V3 uses `NumNodeID`; conversion must preserve legacy semantics. The header exposes internal helper declarations, so accidental external use could couple code to handle internals.

**Test signals:** Compile with kernels before/after `KERNEL_HAS_ENCODE_FH_INODE`, verify struct sizes and packed layout expectations, and run NFS export handle compatibility tests for V1, V2, and V3 buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsExport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsFile.c -->
## sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsFile.c

**Purpose:** Implements the non-native BeeGFS VFS file, directory, and address-space operations for buffered/no-cache and paged-cache modes. It bridges Linux file operations to BeeGFS remote I/O, directory listing, open/close handle sharing, flock/fcntl global locks, flush/fsync, mmap cache coherence, page-cache write hooks, and direct I/O.

**Important APIs/types/functions:** Exports `fhgfs_file_buffered_ops`, `fhgfs_file_pagecache_ops`, `fhgfs_dir_ops`, `fhgfs_address_ops`, and `fhgfs_address_pagecache_ops`. Public functions include `FhgfsOps_llseekdir`, `FhgfsOps_llseek`, `FhgfsOps_readlink`, `FhgfsOps_opendirIncremental`, `FhgfsOps_iterateIncremental`/`FhgfsOps_readdirIncremental`, `FhgfsOps_releasedir`, `FhgfsOps_openReferenceHandle`, `FhgfsOps_open`, `FhgfsOps_release`, `FhgfsOps_releaseCancelLocks`, `FhgfsOps_flock`, `FhgfsOps_lock`, `FhgfsOps_read_iter`, `FhgfsOps_write_iter`, `FhgfsOps_fsync`, `__FhgfsOps_flush`, `FhgfsOps_mmap`, and `FhgfsOps_directIO`. Static helpers include buffered `read_common`, `write_common`, `FhgfsOps_buffered_read_iter`, `FhgfsOps_buffered_write_iter`, page-cache `FhgfsOps_write_begin/end`, and `__FhgfsOps_directIO_common`.

**Control flow:** File open converts OS flags to BeeGFS open flags, references a remote handle through `FhgfsInode_referenceHandle`, constructs `FsFileInfo`, tracks append mode, and disables local caching for O_DIRECT, unbuffered append, or no-cache config. Release cancels leaked global locks, releases the remote handle, and destroys `FsFileInfo`. Directory iteration refreshes `FsDirInfo` incrementally under entry-info read lock, emits entries with generated inode numbers, advances server offsets, and resets cached contents on directory seek. Buffered read/write use BeeGFS helper caches and remote I/O; sparse reads fill gaps after short remote reads. Paged read/write delegate to generic filemap operations after revalidation/write checks and use address-space write hooks. Global flock/range locks flush before unlock, send remote lock RPCs when configured, then apply local Linux locks to preserve kernel semantics. Flush writes dirty pages, waits for filemap, flushes BeeGFS buffer cache, optionally sends remote fsync/session checks/sync-on-close, and bumps file version for flush event logging.

**State and persistence behavior:** Per-open state lives in `FsFileInfo` at `file->private_data`; directory state uses `FsDirInfo`. Inode state tracks shared handles, dirty pages, writeback hints, cache buffers, append locks, and file-size suppression. Durable BeeGFS state changes occur through remote open/close/read/write/truncate/fsync/lock/version-bump RPCs. Local page-cache and buffer-cache state are invalidated or flushed according to cache mode and coherent-buffer settings.

**Dependencies and integration points:** Depends on `FhgfsInode`, `FsFileInfo`, `FsDirInfo`, `FhgfsOpsHelper`, `FhgfsOpsRemoting`, `FhgfsOpsPages`, ioctl ops, OS compatibility wrappers, Linux filemap/writeback/locking/mmap APIs, and BeeGFS config. The operation tables are selected by superblock/inode setup according to configured cache type.

**Risks:** Correctness depends on careful ordering between remote/global locks and local locks, append mutex/global append locks, cache flushes, and i_size updates. Flush errors on release may not reach user space except through `flush`. Coherent-buffer mode uses invalidate operations that can return `-EBUSY` and are intentionally ignored in some paths. `write_common` and page-cache write hooks update local i_size optimistically after remote writes. Sparse read compatibility adds extra refresh/read-or-clear work after short reads. Kernel API shims for folios, fsync signatures, iterate variants, splice, and write_begin flags are broad regression surfaces.

**Test signals:** Test open/close with all access modes, append and O_DIRECT cache disabling, directory seek/iterate offsets, inode-number generation for readdir, global flock and POSIX range lock add/remove/error cases, leaked lock cleanup on close, buffered read/write including sparse gaps, page-cache write_begin/write_end short/full writes, fsync/flush with remote fsync/session/sync-on-close combinations, mmap coherent-buffer retry path, direct I/O read/write, and kernel-version build coverage for operation signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsFile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsFile.h -->
## sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsFile.h

**Purpose:** Declares the public VFS file/directory/address-space operation tables and function entry points implemented in `FhgfsOpsFile.c`, plus small inline accessors for `file->private_data`, lock-owner identity, and page-versus-folio write_begin compatibility.

**Important APIs/types/functions:** Exports operation tables for buffered/pagecache file ops, directory ops, and buffered/pagecache address-space ops. Declares llseek, open/release, directory open/read/release, fsync, flush helper, flock/range lock, readlink, read/write iterators, mmap, direct I/O, close-time lock cancellation, and sparse-read helper. Inline helpers cast `file->private_data` to `FsObjectInfo`, `FsDirInfo`, or `FsFileInfo`; set those pointers; return current lock PID as `current->tgid`; return virtual lock FD as the `struct file*` address; and adapt `struct page*` to `beegfs_pgfol_t` for folio-aware kernels.

**Control flow:** Other modules include this header to invoke shared file-operation helpers or install operation tables. `__FhgfsOps_getObjectInfo` is used when code needs to distinguish file and directory private data polymorphically. The folio/page helpers are used by write_begin/write_end implementations so the same source can compile across kernels that expect either `struct page*` or `struct folio*`, and across kernels whose `grab_cache_page_write_begin` accepts flags or not.

**State and persistence behavior:** The header itself owns no durable state. Its private-data helpers define how per-open `FsFileInfo` and `FsDirInfo` are stored in Linux `struct file`. Lock identity helpers define the remote owner identifiers used for BeeGFS entry/range locks.

**Dependencies and integration points:** Depends on BeeGFS app/config/threading/remoting, `FsDirInfo`, `FsFileInfo`, `FhgfsOps_versions`, `FhgfsOpsInode`, and Linux fs/vfs/pagemap/uio APIs. It is included by native file ops, export code, inode helpers, and compatibility wrappers.

**Risks:** `file->private_data` is untyped, so using a file helper on a directory or vice versa can corrupt assumptions. Remote lock FD uses pointer identity rather than user-space fd by design; that must match server-side unlock expectations. Kernel compatibility macros must be accurate for folio and write_begin signatures or builds will fail.

**Test signals:** Compile across old/new kernels, verify file and directory private-data setup/destruction, exercise lock cleanup using TGID and file pointer identities, and test page/folio write_begin wrappers on kernels with and without flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsFile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsFileNative.c -->
## sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsFileNative.c

**Purpose:** Implements BeeGFS "native" page-cache file operations and address-space operations. Unlike the older buffered/pagecache path, this mode tracks per-page valid ranges, batches asynchronous remote writeback/read-ahead through a workqueue, uses file versions for cache invalidation, and switches between cached and direct I/O based on request size, append locking, and fault injection.

**Important APIs/types/functions:** Exports `fhgfs_file_native_ops`, `fhgfs_addrspace_native_ops`, `beegfs_native_init`, and `beegfs_native_release`. Key helpers include PVR accessors (`pvr_init/present/clear/get/set/merge`), cache range helpers (`beegfs_release_range`, `beegfs_acquire_range`, `beegfs_drop_all_caches`), open/flush/release/read/write/fsync/lock/mmap wrappers, writepages context/state/mempool/workqueue functions, readpages context/state/kref/workqueue functions, page/folio read, readahead/readpages, native write_begin/write_end, release/invalidate/launder page or folio hooks, dirty marking, and direct I/O helpers.

**Control flow:** Initialization creates a writepages mempool, sets readpages block size, and allocates a reclaim-capable workqueue. Native open references a remote handle, validates stripe chunk size alignment to `PAGE_SIZE`, compares local and remote file versions with wraparound-aware logic, updates local version, tracks append FDs, and invalidates/refreshes cache if the remote version changed. Writes mark the inode modified; large writes or fault injection bypass cache through direct I/O, while smaller writes use generic file writeback. Global append writes take BeeGFS append lock under the inode append mutex, refresh i_size, then force direct write. Flush/release write dirty ranges, bump file version, optionally drop all caches on release flush failure, and delegate final handle release to the shared file path. Writeback batches contiguous pages/PVRs into `kvec` arrays, sends vector write RPCs on the workqueue, clears/redirties/errors pages, and waits on a synchronized barrier. Readahead batches contiguous pages into vector reads and completes page endio asynchronously.

**State and persistence behavior:** Page private state stores PVR first/last byte ranges using `PagePrivate` and `PageChecked` discrimination. Inode `modified` controls whether flush/version bump is needed; `fileVersion` tracks server cache coherence; append FD count and append mutex coordinate append locking; writeback counters and no-i_size-decrease protect local size during dirty/writeback activity. Durable changes are remote writes, remote fsync, append locks, and file-version bumps.

**Dependencies and integration points:** Depends on shared `FhgfsOpsFile` open/release/llseek/lock helpers, `FhgfsInode`, `FsFileInfo`, `FhgfsOpsRemoting`, ioctl ops, fault injection, `SynchronizedCounter`, Linux pagecache/writeback/readahead/folio APIs, mempools, krefs, workqueues, and OS compatibility wrappers. The native operation tables are selected by cache-mode setup outside this file.

**Risks:** PVR metadata uses scarce page bits and `page->private`; incorrect interaction with kernel folio/private semantics can corrupt cache state. Several paths contain `BUG()` for unexpected "ARDs were deleted" cases, so malformed private state can crash the kernel. Workqueue writeback must preserve page locking/writeback ordering and correctly handle partial writes. `beegfs_dIO_read` appears to pass `offset + result` to sparse read after already incrementing `offset`, which deserves scrutiny for double-advancing in sparse tails. Flush/fsync error paths set `modified` back to `0` in some branches, which may be intentional but should be reviewed. Native cache correctness relies on file-version bump success and remote version comparison.

**Test signals:** Test native init/release, chunk-size alignment rejection, version-change cache invalidation, modified flag and version bumps on flush/fsync, append direct-write locking, large-request direct bypass, PVR merge/flush/invalidate/release/launder paths, writepages batching for contiguous/non-contiguous pages and partial failures, readahead batching and partial reads, sparse direct reads, lock/mmap acquire/release range behavior, fault-injection paths, and folio versus page kernel builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsFileNative.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsFileNative.h -->
## sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsFileNative.h

**Purpose:** Declares the native BeeGFS file and address-space operation tables and lifecycle functions. This is the public hook used by filesystem setup code to enable the native cache implementation from `FhgfsOpsFileNative.c`.

**Important APIs/types/functions:** Exports `fhgfs_file_native_ops`, `fhgfs_addrspace_native_ops`, `beegfs_native_init(void)`, and `beegfs_native_release(void)`. The operation tables provide VFS and page-cache callbacks; the lifecycle functions allocate/free native writeback/read-ahead resources and the remoting workqueue.

**Control flow:** Initialization code calls `beegfs_native_init` before using the native operation tables and calls `beegfs_native_release` on module teardown. Inodes configured for native cache mode can point their file/address-space operations at the exported tables.

**State and persistence behavior:** The header owns no state. It exposes global operation tables and lifecycle hooks for state managed inside the `.c` file: mempool, workqueue, and cached page-private metadata.

**Dependencies and integration points:** Depends only on Linux `fs.h` for operation-table types. Included by native implementation and cache-mode selection code.

**Risks:** Callers must respect lifecycle ordering; using native ops before successful init or after release would dereference uninitialized global infrastructure. The include guard uses a generated mixed-case identifier rather than the project’s usual filename style, but it is unique.

**Test signals:** Build native-cache configurations, verify init failure unwinds resources, verify release destroys resources once, and mount/open files with native ops enabled after initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsFileNative.h -->
