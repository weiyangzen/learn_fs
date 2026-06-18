# Research: subset-b-000540

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsHelper.c -->
# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsHelper.c

## Purpose
`FhgfsOpsHelper.c` implements shared helper paths for BeeGFS client VFS operations: operation logging, directory listing refresh, buffered read/write cache management, append locking, symlink creation, stateless read/write helpers, and sparse-read zero filling. It sits between VFS-facing operation files and `FhgfsOpsRemoting`, translating local inode/file state into metadata/storage RPCs while maintaining BeeGFS client-side cache invariants.

## Important APIs, Types, And Functions
- `FhgfsOpsHelper_logOpMsg()` resolves dentries into paths, reads `EntryInfo` under the inode entry-info lock, and logs operation context with optional formatted detail.
- `FhgfsOpsHelper_refreshDirInfoIncremental()` maintains `FsDirInfo` directory buffers and detects whether the metadata server supports buffer-size based listing (`META_CAP_LISTDIR_BUFSIZE_MODE`) or legacy entry-count mode.
- `FhgfsOpsHelper_writeCached()` and `FhgfsOpsHelper_readCached()` are the public buffered-cache paths used by file operations.
- `__FhgfsOpsHelper_writeCacheFlushed()`, `__FhgfsOpsHelper_readCacheFlushed()`, `__FhgfsOpsHelper_flushCacheUnlocked()`, and `__FhgfsOpsHelper_discardCache()` implement the unlocked cache state transitions; callers must hold the inode file-cache lock.
- `FhgfsOpsHelper_appendfileVecOffset()`, `FhgfsOpsHelper_getAppendLock()`, and `FhgfsOpsHelper_releaseAppendLock()` serialize append writes through metadata append locks.
- `FhgfsOpsHelper_symlink()` creates symlinks as BeeGFS files containing the target path, using create/open/write/close remoting.
- `FhgfsOpsHelper_readStateless()` and `FhgfsOpsHelper_writeStateless()` perform open-read/write-close flows for callers without an existing file handle.

## Control Flow
Logging first checks the configured log level, resolves the path through `__FhgfsOps_pathResolveToStoreBuf()`, locks inode entry info only while reading the entry ID, formats the optional message, and returns any borrowed path buffer to `NoAllocBufferStore`.

Directory refresh decides between three cases: forced refresh, local buffered contents still usable, or remote listing needed. The listing limit is either the configured message buffer size when the server capability is known/supported, or `100` for legacy/probe mode. On remoting error it clears the local directory contents and resets the current position.

Buffered write starts by bypassing the helper cache when coherent-buffer mode sees active mmaps. Otherwise it takes the inode cache exclusive lock, inspects the current `CacheBuffer` type, and either writes through, discards read cache, extends write cache, flushes incompatible write cache, or creates a new write cache. Full write buffers are flushed immediately. Buffered read has a parallel-reader/shared-lock fast path when no cache exists, otherwise it takes the exclusive lock, flushes write cache before reading, handles read-cache overlap, remote-reads gaps before/after the cache, and discards cache when the requested range extends beyond the cached region.

The stateless paths build `RemotingIOInfo` with a temporary `AtomicInt` and `PathInfo`, initialize `firstWriteDone` bitsets based on the stripe pattern target count, perform the remote operation, close with async retry, and free remoting state. Append writes first acquire a metadata append lock, stat the current size, add any caller-supplied end offset, write at that computed offset, and release the append lock even on error.

## State And Persistence Behavior
Persistent server state changes occur through BeeGFS remoting calls: file writes, symlink file creation, close, unlink-on-error cleanup, append locks, and metadata refresh/listing RPCs. Local state includes per-inode `CacheBuffer` fields (`buf`, `bufType`, `bufUsageLen`, `bufUsageMaxLen`, `fileOffset`), `FsFileInfo` cache hit counters and last offsets, `FsDirInfo` listing capability and contents state, `RemotingIOInfo` cleanup flags, and `InodeRefStore` membership for cached inodes. Cache buffers are borrowed from and returned to `NoAllocBufferStore`; cached inodes are reference-tracked for async flush.

## Dependencies And Integration Points
This file depends heavily on `FhgfsInode` locking/state helpers, `FsFileInfo`, `FsDirInfo`, `NoAllocBufferStore`, `InodeRefStore`, `StripePattern`, `RemotingIOInfo`, `FhgfsOpsRemoting`, `InternodeSyncer`, and kernel `iov_iter` copy helpers. It is called by file, inode, symlink, readlink, writeback, and truncate paths. The async retry integration is in the header inline wrappers, but this implementation provides the stateless write and symlink flows that feed those wrappers.

## Risks
- The cache functions rely on strict external locking for unlocked helpers; misuse can leak buffers, corrupt cache state, or race with read/write paths.
- `copy_from_iter()` and `copy_to_iter()` short-copy handling maps to BeeGFS address-fault errors; callers must preserve negative BeeGFS error conventions.
- Append locking sets cleanup flags on failure, so release failures need delayed cleanup elsewhere.
- Directory capability detection is stateful per handle; bad capability transitions could reduce listing correctness or performance.
- Stateless write uses a referenced inode handle when possible, but has to release it reliably after all errors.
- Symlink creation does multi-step remote mutation and must unlink partially created files if open/write fails.

## Test Signals
Useful signals include append-write serialization tests, buffered read/write cache hit/miss and flush tests, mmap coherent-buffer bypass tests, short user-copy fault injection, directory listing against old and new metadata server capabilities, symlink create/read failure cleanup, sparse reads with EOF zero fill, and close/unlock communication-error async retry queue coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsHelper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsHelper.h -->
# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsHelper.h

## Purpose
`FhgfsOpsHelper.h` declares the BeeGFS helper API used by file, inode, directory, page-cache, and symlink code. It also provides inline wrappers for hot logging, readlink, close retry, and lock-unlock retry behavior.

## Important APIs, Types, And Functions
- Public cache APIs: `FhgfsOpsHelper_flushCache()`, `FhgfsOpsHelper_flushCacheNoWait()`, `FhgfsOpsHelper_writeCached()`, and `FhgfsOpsHelper_readCached()`.
- Unlocked cache internals: `__FhgfsOpsHelper_flushCacheUnlocked()`, `__FhgfsOpsHelper_writeCacheFlushed()`, `__FhgfsOpsHelper_readCacheFlushed()`, and `__FhgfsOpsHelper_discardCache()`.
- Append and stateless I/O: `FhgfsOpsHelper_appendfileVecOffset()`, `FhgfsOpsHelper_getAppendLock()`, `FhgfsOpsHelper_releaseAppendLock()`, `FhgfsOpsHelper_readStateless()`, and `FhgfsOpsHelper_writeStateless()`.
- Directory and symlink helpers: `FhgfsOpsHelper_refreshDirInfoIncremental()`, `FhgfsOpsHelper_getRelativeLinkStr()`, `FhgfsOpsHelper_symlink()`, and `FhgfsOpsHelper_readlink_kernel()`.
- Inline retry wrappers: `FhgfsOpsHelper_closefileWithAsyncRetry()`, `FhgfsOpsHelper_unlockEntryWithAsyncRetry()`, and `FhgfsOpsHelper_unlockRangeWithAsyncRetry()`.

## Control Flow
The `LOG_DEBUG_MESSAGES` macro controls whether `FhgfsOpsHelper_logOpDebug()` emits log calls or compiles away. `FhgfsOpsHelper_logOp()` performs an inline level check before calling the formatted logger. `FhgfsOpsHelper_readlink_kernel()` builds a stack `kvec` iterator and delegates to the stateless read helper.

The close/unlock retry inlines call the matching `FhgfsOpsRemoting_*` operation first. If the result is `FhgfsOpsErr_COMMUNICATION` or `FhgfsOpsErr_INTERRUPTED`, they enqueue delayed cleanup in `InternodeSyncer`. For successful/non-retry close calls, any supplied file event is uninitialized immediately.

## State And Persistence Behavior
The header itself owns no persistent state. It defines contracts for helpers that mutate server file state, per-inode caches, and delayed retry queues. The inline retry wrappers copy enough `EntryInfo`/`RemotingIOInfo` state into `InternodeSyncer` queues to persist cleanup work across transient communication failures.

## Dependencies And Integration Points
The declarations pull in `App`, `StorageErrors`, `MetadataTk`, `InternodeSyncer`, `FsDirInfo`, `FsFileInfo`, and `FhgfsOpsRemoting`. It is a central integration header for VFS operation files and remoting code. Kernel API dependencies include dentries, inodes, and `iov_iter`.

## Risks
- Several non-`static` inline function definitions live in the header; build settings must avoid duplicate symbol issues in this kernel-module style.
- Retry wrappers assume communication/interruption errors are the only cases needing delayed cleanup.
- The unlocked cache declarations make lock ownership a caller responsibility, so misuse is not type-enforced.
- `FhgfsOpsHelper_readlink_kernel()` depends on the stack iterator macro and assumes the target buffer remains valid through the synchronous read.

## Test Signals
Compile coverage across debug/non-debug builds, close/unlock communication fault injection, readlink buffer limit tests, and static analysis for unlocked helper callers are the strongest signals for this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsHelper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsInode.c -->
# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsInode.c

## Purpose
`FhgfsOpsInode.c` implements BeeGFS inode operations for the Linux VFS: lookup, getattr/setattr, xattrs, ACLs, mkdir/create/mknod/symlink/link/unlink/rmdir/rename, symlink following, truncate, inode allocation/destruction, inode instantiation, and remote-stat based cache revalidation. It is the primary bridge between kernel inode/dentry semantics and BeeGFS metadata-server RPCs.

## Important APIs, Types, And Functions
- `maybeRefreshInode()` refreshes inode attributes when the root is not initialized, the BeeGFS inode cache is invalid, or a forced stat is requested.
- `FhgfsOps_lookupIntent()`, `FhgfsOps_createIntent()`, and `FhgfsOps_atomicOpen()` use BeeGFS lookup-intent RPCs to combine lookup/create/stat/open.
- `FhgfsOps_getattr()` fills `kstat` after optional refresh and handles root inode numbering and 32-bit inode overflow mitigation.
- `FhgfsOps_setattr()` handles chmod/chown/utime/truncate, flushes dirty data for regular files, remotes attribute changes, updates ACLs, and performs remote truncation.
- Xattr and ACL APIs include `FhgfsOps_listxattr()`, `FhgfsOps_getxattr()`, `FhgfsOps_setxattr()`, `FhgfsOps_removexattrInode()`, `Fhgfs_get_acl()`, and `FhgfsOps_set_acl()`.
- Namespace mutation APIs include `FhgfsOps_mkdir()`, `FhgfsOps_rmdir()`, `FhgfsOps_mknod()`, `FhgfsOps_symlink()`, `FhgfsOps_link()`, `FhgfsOps_hardlinkAsSymlink()`, `FhgfsOps_unlink()`, and `FhgfsOps_rename()`.
- Inode lifecycle APIs include `FhgfsOps_initInodeCache()`, `FhgfsOps_alloc_inode()`, `FhgfsOps_destroy_inode()`, `__FhgfsOps_newInodeWithParentID()`, and `__FhgfsOps_instantiateInode()`.
- Refresh/cache APIs include `__FhgfsOps_flushInodeFileCache()`, `__FhgfsOps_doRefreshInode()`, and `__FhgfsOps_revalidateMapping()`.

## Control Flow
Lookup initializes dentry validation time, refreshes the parent/root if required, then either handles root specially or performs `FhgfsOpsRemoting_lookupIntent()` under the parent entry-info read lock. Successful lookup converts BeeGFS stat data into a `kstat`, generates a stable inode number from the entry ID, creates or reuses an inode through `iget5_locked()`, and attaches it with directory-specific `d_materialise_unique()` or `d_splice_alias()`.

Create/open paths build `LookupIntentInfoIn` with optional `CreateInfo` and `OpenInfo`. They check name length and type, lock parent entry info during the combined RPC, validate create/stat/open results, instantiate the inode, and when an open handle was returned attach it to the file via `FhgfsOps_openReferenceHandle()`. Error paths close server-side handles that were opened before local setup completed.

Setattr first performs kernel permission checks (`setattr_prepare()` or `inode_change_ok()`), ignores redundant open-time truncation, flushes page cache and buffered file cache for regular files, converts `iattr` into BeeGFS attributes, sends remote setattr with optional event logging, applies local attributes, updates ACLs for chmod, and issues remote truncate plus local `FhgfsOps_vmtruncate()` when size changes.

Namespace operations follow a repeated pattern: build `CreateInfo` or event metadata, lock the relevant parent/file entry infos in a stable order, call the remoting operation, update local dentry/inode timestamps/link counts/entry info on success, drop negative dentries on selected errors, and invalidate BeeGFS inode caches where needed. Rename takes a write lock on the renamed file's entry info to protect concurrent reference/release and then updates entry info after a successful remote rename.

Refresh flushes dirty local content unless `noFlush` is set, stats the metadata server, validates object type, applies stat fields under `i_lock`, and invalidates remote inode page state when mtime/size changed or the page-cache validity timeout expired.

## State And Persistence Behavior
Server-persistent operations include metadata creates, removes, hardlinks, symlink file creation, renames, xattr/ACL changes, setattr, truncation, and lookup/stat state. Local persistent-in-memory state includes inode cache slab objects, `EntryInfo`, `metaVersion`, parent node IDs for export reconnect, idmapped mount/user namespace pointers, generated inode numbers, link counts, timestamps, page-cache mappings, ACL caches, `dataCacheTime`, dirty-page/writeback counters, and `S_NOSEC` xattr/capability cache flags.

The code intentionally prevents some local `i_size` decreases while page writeback may still be racing, using `FhgfsIsizeHints`, writeback counters, and `lastWriteBackOrIsizeWriteTime`. Server timestamps are authoritative for normal inode timestamp state; local timestamps are updated for VFS-visible directory mutations after successful remoting.

## Dependencies And Integration Points
This file integrates with `FhgfsOpsRemoting`, `FhgfsInode`, `FhgfsOpsFile`, `FhgfsOpsFileNative`, `FhgfsOpsDir`, `FhgfsOpsSuper`, `FhgfsXAttrHandlers`, `OsTypeConv`, `CreateInfo`, `LookupIntentInfo`, `OpenInfo`, `FileEvent`, POSIX ACL helpers, Linux dentry/inode/page-cache APIs, idmapped/user namespace APIs, and configuration options controlling cache mode, ACL/xattr revalidation, hardlink-as-symlink behavior, event logging, and EBUSY-to-EXDEV rename mapping.

## Risks
- `FhgfsOps_createIntent()` has an early `return -EINVAL` inside a parent entry-info lock when `createMode` is not regular; that path is worth auditing for lock release in the active build configuration.
- Lock ordering is critical for link and rename paths because multiple directory and file entry-info locks are taken.
- `FhgfsOps_hardlinkAsSymlink()` has error handling around path resolution; wrong `IS_ERR`/`PTR_ERR` handling could report incorrect errors.
- Inode refresh and page-cache invalidation race with writeback; the no-decrease logic is complex and requires regression coverage.
- ACL/xattr caching with `inode_has_no_xattr()` and `forget_all_cached_acls()` depends on configuration and kernel security semantics.
- Atomic-open is conditionally enabled and has non-trivial cleanup paths for successful lookup but failed open/reference setup.

## Test Signals
High-value coverage includes lookup/create/open races, NFS/disconnected dentry aliasing, chmod with ACL updates, truncation while writeback is active, xattr/capability cache modes, SELinux xattr initialization, hardlink and hardlink-as-symlink modes, rename across directories, stale cache invalidation after remote modification, 32-bit stat inode behavior, and fault injection for remoting success with local open-handle setup failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsInode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsInode.h -->
# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsInode.h

## Purpose
`FhgfsOpsInode.h` declares the BeeGFS inode-operation interface and supplies compatibility shims/inlines for changing Linux kernel inode, time, ACL, idmapped mount, and VFS callback APIs. It also defines inline stat-to-inode application helpers used by inode creation and refresh.

## Important APIs, Types, And Functions
- Kernel time compatibility: `inode_timespec`, `inode_get_ctime*()`, `inode_set_ctime*()`, `inode_get_atime*()`, `inode_set_atime*()`, `inode_get_mtime*()`, `inode_set_mtime*()`, and `inode_set_mc_time()`.
- VFS operation declarations cover lookup, getattr, setattr, xattrs, ACLs, mkdir/mknod/create/atomic-open, rmdir/unlink/symlink/link, symlink follow/get-link, rename, and truncate.
- Inode cache/lifecycle declarations include `FhgfsOps_initInodeCache()`, `FhgfsOps_alloc_inode()`, `FhgfsOps_destroy_inode()`, `__FhgfsOps_newInodeWithParentID()`, and `__FhgfsOps_instantiateInode()`.
- Inline helpers include `__FhgfsOps_applyStatDataToInode()`, `__FhgfsOps_applyStatDataToInodeUnlocked()`, `__FhgfsOps_applyStatAttribsToInode()`, `__FhgfsOps_applyStatSizeToInode()`, `__FhgfsOps_newInode()`, `__FhgfsOps_isPagedMode()`, and `__FhgfsOps_refreshInode()`.
- `struct FhgfsInodeComparisonInfo` carries the generated inode hash and entry ID for `iget5_locked()` comparison.

## Control Flow
The header selects function signatures through `#if` blocks for kernel features such as `KERNEL_HAS_STATX`, `KERNEL_HAS_IDMAPPED_MOUNTS`, `KERNEL_HAS_USER_NS_MOUNTS`, `KERNEL_HAS_ATOMIC_OPEN`, `KERNEL_HAS_GET_LINK`, and ACL callback variants. This lets the implementation expose the exact callback prototypes expected by the target kernel.

The stat-application inlines first write mode, ownership, timestamps, link count, and block bits, then update size and block count under `i_lock`. `__FhgfsOps_applyStatSizeToInode()` contains the key paged-writeback protection: when regular files have page-write flags, it avoids decreasing `i_size` if no-decrease is set, writeback is active, or `FhgfsIsizeHints` indicate a concurrent update after the remote stat began. `__FhgfsOps_isPagedMode()` maps BeeGFS cache configuration to paged/native modes that require page-cache address-space operations.

## State And Persistence Behavior
The header modifies local inode fields through inline helpers but does not directly perform remoting. It controls local persistence of cached inode attributes, `i_size`, `i_blocks`, timestamps, and generated inode identity. The `i_size` decrease guard preserves local dirty/writeback data over potentially stale metadata-server sizes.

## Dependencies And Integration Points
The header integrates kernel compatibility macros from `FhgfsOps_versions.h`, BeeGFS `FhgfsInode`, `FsDirInfo`, `FsFileInfo`, remoting declarations, `NoAllocBufferStore`, and Linux VFS headers. It is included by inode, file, page-cache, and superblock operation code to keep callback signatures consistent with the build kernel.

## Risks
- The large compatibility matrix can hide compile-only bugs on kernel versions not covered by regular CI.
- Inline functions update inode state directly and depend on callers holding `i_lock` where required.
- The `i_size` decrease avoidance is intentionally conservative; bugs can cause stale size exposure or data-loss risk if it allows shrink during writeback.
- `__FhgfsOps_isPagedMode()` affects operation table selection and must remain aligned with all cache-type semantics.

## Test Signals
Kernel-version build matrix coverage, sparse/static checks for callback signatures, focused tests for `i_size` updates under writeback, and integration tests for paged/native/buffered cache mode inode creation provide the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsInode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsIoctl.c -->
# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsIoctl.c

## Purpose
`FhgfsOpsIoctl.c` implements BeeGFS client ioctl commands for version queries, mount/config discovery, stripe layout inspection, file creation with hints or explicit metadata, inode/entry information queries, node ping diagnostics, and privileged file-state changes. It is the user-space control/query entry point for operations that do not fit standard POSIX VFS calls.

## Important APIs, Types, And Functions
- Dispatchers: `FhgfsOpsIoctl_ioctl()` and `FhgfsOpsIoctl_compatIoctl()`.
- Config/mount probes: `FhgfsOpsIoctl_getCfgFile()`, `FhgfsOpsIoctl_getRuntimeCfgFile()`, `FhgfsOpsIoctl_testIsFhGFS()`, and `FhgfsOpsIoctl_getMountID()`.
- Stripe queries: `FhgfsOpsIoctl_getStripeInfo()`, `FhgfsOpsIoctl_getStripeTarget()`, `FhgfsOpsIoctl_getStripeTargetV2()`, `getStripePatternImpl()`, and `resolveNodeToString()`.
- Creation helpers: `FhgfsOpsIoctl_mkfileWithStripeHints()` and `FhgfsOpsIoctl_createFile()` for ioctl create versions 1 through 3.
- Metadata/diagnostic helpers: `FhgfsOpsIoctl_getInodeID()`, `FhgfsOpsIoctl_getEntryInfo()`, `FhgfsOpsIoctl_pingNode()`, and `FhgfsOpsIoctl_setFileState()`.

## Control Flow
The main ioctl dispatcher logs the command and switches on BeeGFS ioctl numbers. Old `GETVERSION` commands map to `inode->i_generation`; `TCGETS` is rejected as `-ENOTTY` to satisfy `isatty()` probes; unknown commands return `-ENOIOCTLCMD`. The compat dispatcher only remaps 32-bit get-version commands and forwards them to the main dispatcher through `compat_ptr()`.

Simple getters validate user memory implicitly or explicitly, format mount/config strings, and copy bounded data to user space. Stripe target resolution validates that the file is not a directory, reads the inode stripe pattern, resolves buddy-mirror groups into primary/secondary targets, maps targets to node IDs, resolves node aliases from the storage node store, and copies all requested fields to user space.

Creation ioctls check directory permissions and mount writeability, copy versioned argument structures through `IoctlHelper`, build `CreateInfo`, translate preferred targets and storage pool IDs, optionally override uid/gid for privileged callers, construct parent `EntryInfo`, and perform `mkfile` or symlink helper remoting. Cleanup frees all copied strings and target lists and drops mount write references.

`FhgfsOpsIoctl_pingNode()` copies ping parameters, validates node type/count/interval, references the selected node, acquires or reuses a stream socket, sends heartbeat requests, skips the first sample to avoid connection overhead, records latency and NIC type, invalidates sockets on request failure, releases node/socket resources, and copies results back.

`FhgfsOpsIoctl_setFileState()` copies and validates a filename, requires a directory fd and `CAP_SYS_ADMIN`, takes a mount write reference, looks up the target under the parent entry-info lock, validates regular-file type, sends `SetFileState`, then releases lookup output, entry info, and write reference.

## State And Persistence Behavior
Read-only ioctls expose local mount config, runtime proc path, generated inode IDs, `EntryInfo`, and stripe layout. Mutating ioctls create files/symlinks with server-persistent metadata, optional stripe/storage-pool preferences, and event-log records. `SET_FILE_STATE` changes server-side access/data state. Ping does not persist filesystem data but exercises node connection pools and can invalidate a failed socket.

## Dependencies And Integration Points
This file integrates with the public `uapi/beegfs_client.h` ioctl ABI, `IoctlHelper`, `FhgfsOpsRemoting`, `FhgfsOpsHelper`, `FhgfsOpsInode`, `CreateInfo`, `EntryInfo`, `TargetMapper`, `MirrorBuddyGroupMapper`, `NodeStoreEx`, `NodeConnPool`, heartbeat messages, mount write accounting, Linux user-copy helpers, and capability checks.

## Risks
- User-copy structure versioning must stay ABI-compatible with `uapi/beegfs_client.h`.
- Creation ioctls accept many user-supplied pointers/strings and must free all partial allocations on every error path.
- Stripe target queries depend on open-file stripe pattern state; missing pattern returns errors expected to be unreachable.
- `pingNode` loops from `0` through `count` to skip the first sample, so result arrays must be sized for `count` samples after validation.
- `setFileState` must preserve privilege and filename validation because it changes server-side file state outside normal POSIX permissions.
- Mount write references (`mnt_want_write*`) must always be dropped on all post-acquire paths.

## Test Signals
Ioctl ABI tests for 32-bit and 64-bit callers, fuzzed user-copy failures, create-file v1/v2/v3 argument cleanup, stripe info for buddy-mirrored and non-mirrored files, directory/error cases, ping validation and socket failure injection, and privileged/unprivileged `SET_FILE_STATE` tests are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsIoctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsIoctl.h -->
# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsIoctl.h

## Purpose
`FhgfsOpsIoctl.h` declares the BeeGFS ioctl entry points and defines compatibility ioctl command numbers for old kernel `FS_IOC_GETVERSION` variants. It is the narrow header that connects BeeGFS file operation tables to the ioctl implementation.

## Important APIs, Types, And Functions
- `BEEGFS_IOC_GETVERSION_OLD` maps to `FS_IOC_GETVERSION` when present or defines the old `_IOR('v', ...)` command manually.
- `BEEGFS_IOC32_GETVERSION_OLD` does the same for 32-bit compat mode when `CONFIG_COMPAT` is enabled.
- `FhgfsOpsIoctl_ioctl()` is the main unlocked ioctl callback.
- `FhgfsOpsIoctl_compatIoctl()` is the compat callback for 32-bit user space on 64-bit kernels.

## Control Flow
The header uses preprocessor feature checks to select existing kernel ioctl constants when available and local definitions otherwise. The implementation receives all other BeeGFS ioctl numbers from `uapi/beegfs_client.h`.

## State And Persistence Behavior
The header has no runtime state. Its constants preserve ABI behavior for older userspace and older kernels.

## Dependencies And Integration Points
It includes `asm/ioctl.h`, Linux kernel headers, BeeGFS `NumNodeID`, and the public BeeGFS client uapi header. It is consumed by file operation table setup and `FhgfsOpsIoctl.c`.

## Risks
Incorrect ioctl-number compatibility would break old tools, NFS/user-space filesystem generation checks, or 32-bit compat callers. Since only get-version compat is forwarded in `FhgfsOpsIoctl_compatIoctl()`, adding new compat-sensitive ioctls requires explicit updates.

## Test Signals
Builds on kernels with and without `FS_IOC_GETVERSION`, 32-bit compat ioctl smoke tests, and user-space `ioctl(GETVERSION)` regression tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsIoctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsPages.c -->
# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsPages.c

## Purpose
`FhgfsOpsPages.c` implements BeeGFS address-space page-cache operations for paged/native cache modes: readpage/read_folio, readahead/readpages, writepage/writepages, page-vector batching, writeback completion, short-read handling, and page-backed inode size correction. It bridges Linux MM/VFS page callbacks to asynchronous BeeGFS page-vector remoting work.

## Important APIs, Types, And Functions
- Page-vector cache lifecycle: `FhgfsOpsPages_initPageListVecCache()` and `FhgfsOpsPages_destroyPageListVecCache()`.
- Internal batching: `struct FhgfsPageData`, `_FhgfsOpsPages_allocNewPageVec()`, and `_FhgfsOpsPages_sendPageVec()`.
- File-handle referencing: `_FhgfsOpsPages_referenceReadFileHandle()`, `_FhgfsOpsPages_referenceWriteFileHandle()`, and `_FhgfsOpsPages_referenceFileHandle()`.
- Write path: `FhgfsOpsPages_writePageCallBack()`, `_FhgfsOpsPages_writepages()`, `FhgfsOpsPages_writepage()`, `FhgfsOpsPages_writepages()`, and `FhgfsOpsPages_endWritePage()`.
- Read path: `FhgfsOpsPages_readPageCallBack()`, `FhgfsOpsPages_readpageSync()`, `FhgfsOps_read_folio()` or `FhgfsOpsPages_readpage()`, `_FhgfsOpsPages_readahead()` or `_FhgfsOpsPages_readpages()`, and `FhgfsOpsPages_readahead()` or `FhgfsOpsPages_readpages()`.
- Size/short-read handling: `__FhgfsOpsPages_incInodeFileSizeOnPagedRead()`, `FhgfsOpsPages_isShortRead()`, `FhgfsOpsPages_endReadPage()`, and `FhgfsOpsPages_writeBackPage()`.

## Control Flow
Initialization creates a slab cache for `FhgfsPageListVec` objects and a small mempool reserve; teardown destroys the mempool before the slab cache. Page-vector sending checks for null/empty vectors, queues non-empty vectors through `RWPagesWork_createQueue()`, and optionally allocates the next vector for continued batching.

Writeback begins from `write_cache_pages()` or a single-page writepage call. The callback references a write handle on first use, allocates a chunk page vector, clips the final page to `i_size`, ignores pages beyond truncation while clearing writeback state, pushes pages into the vector, sends full vectors asynchronously, sets page writeback, and leaves completion to worker callbacks. The final `_writepages` flush sends any remaining vector and releases the referenced file handle.

Readpage clears `PageUptodate`, writes back the target page first to avoid reading stale dirty data, and delegates to readahead/readpages. The read batching path references a read-capable handle, holds the inode while async work owns pages, pushes pages into chunk vectors, sends vectors to read workers, releases the handle, and drops the inode reference. Read completion zero-fills partial pages, flushes dcache, marks pages uptodate, records errors, adjusts inode size when reads extend past local `i_size`, and unmaps/unlocks/releases pages.

`__FhgfsOpsPages_incInodeFileSizeOnPagedRead()` handles metadata size lag: it refreshes the inode without flushing because locked pages could deadlock, asks the metadata server to refresh the entry if needed, refreshes again, and only increases local `i_size` under `i_lock` if the read still extends beyond known size.

## State And Persistence Behavior
Local state includes slab/mempool allocations, `FhgfsPageData` handle references and `RemotingIOInfo`, `FhgfsChunkPageVec` batches, page dirty/writeback/uptodate/error flags, inode dirty-page counters, inode size, and inode hold counts while async work is queued. Server-persistent behavior is indirect: queued `RWPagesWork` performs storage-node reads/writes, and size correction can request metadata refresh via `FhgfsOpsRemoting_refreshEntry()`.

## Dependencies And Integration Points
This file integrates with Linux MM helpers (`write_cache_pages`, `read_cache_pages`, folio/readahead APIs, writeback controls, page locking), BeeGFS `FhgfsChunkPageVec`, `FhgfsPage`, `RWPagesWork`, `FhgfsInode` handle/reference/counter APIs, `FhgfsOpsInode` refresh, `FhgfsOpsHelper` logging, `RemotingIOInfo`, and cache-mode address-space operation tables selected during inode creation.

## Risks
- Page lock and inode flush ordering is delicate; refresh paths explicitly avoid flushing while pages are locked to prevent deadlocks.
- Async queued page vectors must own page references correctly until completion; missing `get_page()`/release behavior can race page reuse.
- Writeback error handling must set mapping/page errors and decrement dirty counters exactly once.
- Clipping writes against `i_size` races with truncate and can either drop beyond-size pages or re-dirty them for retry.
- Kernel API variants for folios/readpages/writepage callbacks increase build-matrix risk.
- Mempool exhaustion paths must not leak page vectors or leave pages locked.

## Test Signals
Stress tests for mmap/page-cache writes, truncation during writeback, readahead across chunk boundaries, sparse and short reads, metadata size lag, injected `RWPagesWork_createQueue()` allocation failure, writeback error propagation, folio and pre-folio kernel builds, and dirty-page counter accounting are the most valuable signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsPages.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsPages.h -->
# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsPages.h

## Purpose
`FhgfsOpsPages.h` declares BeeGFS page-cache/address-space operations and provides the fast inline inode-size correction wrapper used after paged reads. It defines the maximum page-vector list size shared with the page batching implementation.

## Important APIs, Types, And Functions
- `BEEGFS_MAX_PAGE_LIST_SIZE` caps chunk page-vector sizes and must remain larger than the implementation's initial search size.
- Cache lifecycle: `FhgfsOpsPages_initPageListVecCache()` and `FhgfsOpsPages_destroyPageListVecCache()`.
- Read callbacks: `FhgfsOps_readpagesVec()`, `FhgfsOpsPages_readpageSync()`, `FhgfsOps_read_folio()` or `FhgfsOpsPages_readpage()`, and `FhgfsOpsPages_readahead()` or `FhgfsOpsPages_readpages()`.
- Write callbacks: `FhgfsOpsPages_writepage()`, `FhgfsOpsPages_writepages()`, and `FhgfsOpsPages_writeBackPage()`.
- Completion and size helpers: `FhgfsOpsPages_incInodeFileSizeOnPagedRead()`, `__FhgfsOpsPages_incInodeFileSizeOnPagedRead()`, `FhgfsOpsPages_isShortRead()`, `FhgfsOpsPages_endReadPage()`, and `FhgfsOpsPages_endWritePage()`.

## Control Flow
The header selects folio-aware or page-based callback declarations depending on kernel feature macros. The inline `FhgfsOpsPages_incInodeFileSizeOnPagedRead()` reads current `i_size`, returns immediately for non-positive reads, and calls the slower non-inline helper only when `offset + readRes` exceeds local size.

## State And Persistence Behavior
The header itself holds no state. The inline helper can trigger local inode-size correction through the implementation function, which may refresh metadata and increase local `i_size`.

## Dependencies And Integration Points
The header depends on `toolkit/FhgfsPage.h` and Linux page-cache types. It is included by BeeGFS page-cache implementation and address-space operation table declarations used by inode setup.

## Risks
- The documented maximum page-list size comment appears to state `65536` pages and `262144 MiB` for 4K pages, while the macro is `65535`; consumers should rely on the macro and implementation assertions.
- If the inline size check is removed or bypassed, reads beyond stale local `i_size` can be discarded incorrectly by callers.
- Kernel feature macro mismatches can produce incorrect address-space operation signatures.

## Test Signals
Compile coverage for folio and non-folio kernels, read-completion tests where remote reads extend beyond local `i_size`, and static checks that `BEEGFS_MAX_PAGE_LIST_SIZE` remains above implementation thresholds validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsPages.h -->
