# subset-b-000541 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsSuper.c -->
# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsSuper.c

## Purpose
Implements BeeGFS client VFS superblock registration, per-mount `App` lifecycle, root inode construction, procfs attachment, xattr handler selection, and unmount cleanup. It is the mount/unmount spine connecting Linux VFS objects to the BeeGFS runtime.

## Important APIs and Functions
`FhgfsOps_registerFilesystem()` and `FhgfsOps_unregisterFilesystem()` register the `file_system_type`. `FhgfsOps_fillSuper()` builds a mounted superblock and root dentry. `FhgfsOps_putSuper()` and `FhgfsOps_killSB()` tear down mount state. Private helpers `__FhgfsOps_constructFsInfo()`, `__FhgfsOps_destructFsInfo()`, `__FhgfsOps_initApp()`, and `__FhgfsOps_uninitApp()` allocate `FhgfsSuperBlockInfo`, run/stop `App`, create/remove procfs entries, and manage backing-device information.

## Control Flow
Mount registration points either `.get_sb` or `.mount` at the compatibility wrappers in `FhgfsOps_versions.c`, with `.kill_sb` bound to `FhgfsOps_killSB()`. `FhgfsOps_fillSuper()` calls `__FhgfsOps_constructFsInfo()`, which allocates `sb->s_fs_info`, parses raw mount options into `MountConfig`, initializes/runs `App`, creates per-mount procfs entries, and initializes BDI state where required. The fill path then configures VFS limits, flags, super operations, xattr handlers, export ops, root `kstat`, dummy `EntryInfo`, root inode, root dentry, and optional default dentry ops. Unmount disables connection retries, flushes page work, unregisters older BDI state, and lets `kill_anon_super()` drive `put_super`.

## State and Persistence
State is per mount and lives in `sb->s_fs_info`: embedded `App`, optional `backing_dev_info`, `haveRootEntryInfo`, and `isRootInited`. Procfs entries persist for the mount session and are removed after `App_stop()`. Root inode state is initially dummy and refreshed later by lookup/revalidation paths. No durable storage is written here; persistent effects are remote cluster/session side effects owned by `App`.

## Dependencies and Integration Points
Depends on VFS superblock APIs, `App`, `MountConfig`, `Config`, `ProcFs`, inode/file/dir/page/export operations, xattr handler arrays, `RWPagesWork`, and remoting helpers. It integrates with Linux BDI APIs across kernel versions and with NFS export support for supported kernels.

## Risks
Failure unwinding must keep `sb->s_fs_info`, `App`, BDI registration, root inode/dentry, and procfs entries balanced. `FhgfsOps_getApp()` assumes initialized `s_fs_info`, so callers during failed mounts must guard. Xattr handler selection depends on config combinations; wrong selection can silently disable ACL/SELinux paths. Unmount latency depends on connection retry state and page-work flushing.

## Test Signals
Useful tests include mount with valid/invalid options, BDI setup failure injection, procfs entry presence/removal, ACL/SELinux/xattr option combinations, root inode creation failure, repeated mount/unmount, unmount during communication failure, and stat/export smoke tests after mount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsSuper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsSuper.h -->
# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsSuper.h

## Purpose
Defines the public superblock interface and the per-superblock BeeGFS mount state for the client module.

## Important APIs and Types
`FhgfsSuperBlockInfo` stores the embedded `App`, optional `backing_dev_info`, and root initialization flags. Constants include `BEEGFS_MAGIC` and reported statfs block size values. Public declarations expose filesystem registration, superblock fill/kill/put, and mount option display. Inline accessors expose `App`, BDI, root `EntryInfo` readiness, and root attribute initialization state.

## Control Flow
Most functions in this header are inline accessors used by VFS operations throughout the client. `FhgfsOps_getApp()` and `FhgfsOps_getBdi()` retrieve per-mount state from `sb->s_fs_info`; root flags are read/set by mount and inode lookup/revalidation paths.

## State and Persistence
The header defines in-memory mount state only. `haveRootEntryInfo` and `isRootInited` are process-lifetime flags tied to root inode metadata refresh behavior, not durable state. Comments specify lock expectations for root entry info: callers should coordinate with `fhgfsInode->entryInfoLock` except during mount.

## Dependencies and Integration Points
Includes `App`, common definitions, kernel VFS/BDI/seq APIs, and `FhgfsOps_versions.h` for cross-kernel signatures. The structure layout is consumed by `FhgfsOpsSuper.c` and all VFS paths that need the `App`.

## Risks
Inline getters intentionally skip null checks for performance. Any caller using them before successful superblock initialization or after partial teardown can dereference null state. Locking guidance around root flags is advisory, so misuse can produce stale root entry information.

## Test Signals
Compile across kernel feature combinations, mount failure paths that leave `s_fs_info` null, and root lookup/revalidation tests that check flag transitions under lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsSuper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOps_versions.c -->
# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOps_versions.c

## Purpose
Provides Linux-kernel-version compatibility implementations for permission, statfs, mount entry points, file flush, inode-cache construction, and older kernel helper emulation.

## Important APIs and Functions
`FhgfsOps_permission()` disables RCU path walking where necessary and delegates permission checks to the appropriate generic permission API. `FhgfsOps_statfs()` fills `kstatfs` from `StatFsCache`. `FhgfsOps_getSB()`/`FhgfsOps_mount()` adapt to old/new mount APIs. `FhgfsOps_flush()` invokes BeeGFS close-time flushing. `FhgfsOps_initInodeOnce()` initializes cached BeeGFS inode objects. Older kernels may get emulated `generic_file_llseek_unlocked()`.

## Control Flow
Permission checks return `-ECHILD` for RCU walk flags so VFS retries in ref-walk mode, then use idmapped/userns/generic permission paths. Statfs initializes fields, queries cached total/free space, converts BeeGFS error codes to Linux errors, and rounds byte totals into `BEEGFS_STATFS_BLOCKSIZE` units. Flush logs the operation and calls `__FhgfsOps_flush()` with asynchronous cleanup allowances.

## State and Persistence
This file does not own durable state. It reads `App`, `Config`, `StatFsCache`, file/dentry/inode state, and initializes slab-created inode objects. Statfs reports cached distributed storage values rather than local disk values.

## Dependencies and Integration Points
Integrates with `FhgfsOpsSuper`, inode/file/dir helpers, remoting, `NoAllocBufferStore`, `StatFsCache`, and `OsCompat`. It is a compatibility layer for many `KERNEL_HAS_*` feature macros.

## Risks
Cross-version signatures are fragile; incorrect macro detection can produce ABI mismatches. Statfs depends on cache freshness and can return remote I/O errors. Flush errors do not imply data is permanently lost because flusher references may remain, but caller-visible close behavior depends on `__FhgfsOps_flush()` semantics.

## Test Signals
Build matrix across supported kernels, permission RCU-walk regression tests, statfs cache success/failure, close/flush with delayed writeback, and slab constructor tests for inode initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOps_versions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOps_versions.h -->
# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOps_versions.h

## Purpose
Declares version-dependent VFS operation signatures and fallback helper APIs needed by the BeeGFS client module.

## Important APIs and Types
The header declares `FhgfsOps_permission()` variants, mount/get_sb variants, `FhgfsOps_statfs()`, `FhgfsOps_flush()`, and `FhgfsOps_initInodeOnce()` variants. It also defines inline or external compatibility helpers for `generic_file_llseek_unlocked`, `set_nlink`, `dentry_path_raw`, `ihold`, `file_dentry`, and `file_inode` when kernels lack them.

## Control Flow
Preprocessor branches select the signature visible to the rest of the client. Inline fallbacks directly manipulate old-kernel fields, for example `inode->i_nlink` and `inode->i_count`.

## State and Persistence
No owned runtime state. The fallback helpers mutate standard VFS structures in the same way newer kernel helpers would.

## Dependencies and Integration Points
Includes Linux module, fs, vfs, pagevec, pagemap, and page flag headers. It is included by superblock and many filesystem operation implementations to normalize kernel APIs.

## Risks
Because the header provides inline definitions, macro mismatches can create duplicate symbols or wrong calling conventions. Old-kernel fallbacks bypass newer helper abstractions and require exact semantic parity.

## Test Signals
Compile-only coverage against the supported kernel matrix is the strongest signal. Runtime smoke tests should cover inode link-count changes, file inode/dentry retrieval, and llseek behavior on old kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOps_versions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsXAttrHandlers.c -->
# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsXAttrHandlers.c

## Purpose
Implements BeeGFS xattr handler tables and operations for user, security/SELinux, and POSIX ACL extended attributes across kernel xattr API versions.

## Important APIs and Functions
ACL handlers `FhgfsXAttrSetACL()` and `FhgfsXAttrGetACL()` map POSIX ACL xattrs to BeeGFS remote xattr operations and update file mode bits for access ACLs. `FhgfsXAttr_getUser()`/`setUser()` and `FhgfsXAttr_getSecurity()`/`setSecurity()` reapply namespace prefixes before delegating to `FhgfsOps_getxattr`, `FhgfsOps_setxattr`, or removal helpers. `FhgfsXAttr_init_security()` invokes LSM initialization using `security_inode_init_security()`. Handler arrays expose all, ACL-only, SELinux-only, and user-only combinations.

## Control Flow
VFS strips namespace prefixes before handler calls; handlers allocate prefixed names and call BeeGFS inode xattr operations. ACL set validates empty handler names, owner/capability, symlink exclusion, ACL parse/equivalence, and mode update via `FhgfsOps_setattr()` before setting/removing the ACL xattr. Security initialization checks directory security state, then applies each generated LSM xattr in the security namespace.

## State and Persistence
Local state is transient allocations for prefixed names and ACL parsing. Persistent effect is remote metadata mutation through BeeGFS xattr and setattr RPC paths. Handler arrays are static module state selected into `sb->s_xattr` by mount config.

## Dependencies and Integration Points
Depends on Linux xattr, POSIX ACL, LSM hooks, idmapped/user namespace helpers, `FhgfsOpsInode`, `FhgfsOpsHelper`, and superblock config selection in `FhgfsOpsSuper.c`.

## Risks
Name length handling differs between the older dynamic prefix helpers and `beegfs_xattr_set()`, which uses `XATTR_NAME_MAX` and `snprintf`; long names need careful validation. Several paths allocate before remote calls and must free on all exits. ACL mode updates and remote xattr updates are separate operations, so partial failure after chmod-like setattr can leave mode changed without the intended ACL. `FhgfsXAttr_security_xattr_enabled()` checks `i_security` and `s_security`; behavior depends on kernel security structure availability.

## Test Signals
Exercise get/set/remove for `user.*` and `security.*`, ACL access/default set including equivalent-mode ACLs and empty ACL removal, owner/capability denial, symlink ACL denial, SELinux inode creation labels, long names, `XATTR_CREATE`/`XATTR_REPLACE`, and mount configs enabling/disabling ACL and SELinux handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsXAttrHandlers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsXAttrHandlers.h -->
# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsXAttrHandlers.h

## Purpose
Declares BeeGFS xattr handler arrays and the security xattr initialization API used by inode creation and superblock setup.

## Important APIs and Types
`FhgfsXAttr_init_security()` is exported for create paths to initialize LSM-provided security xattrs. Depending on const-handler kernel macros, the header declares `fhgfs_xattr_handlers`, `fhgfs_xattr_handlers_acl`, `fhgfs_xattr_handlers_selinux`, and `fhgfs_xattr_handlers_noacl` with the correct pointer constness. It also declares `FhgfsXAttr_getSecurity()` for kernels using xattr handler callbacks.

## Control Flow
The header itself has no runtime flow. Compile-time branching ensures the same implementation can be assigned to `super_block->s_xattr` across kernels with different handler constness and callback signatures.

## State and Persistence
No owned state. The declared arrays are static module-global handler tables defined in `FhgfsXAttrHandlers.c`.

## Dependencies and Integration Points
Includes Linux xattr APIs and is consumed by `FhgfsOpsSuper.c` during mount and by inode creation/security paths.

## Risks
Constness/signature mismatches across kernel versions can break module builds. Consumers should only reference arrays that exist under the same `KERNEL_HAS_GET_ACL` conditions.

## Test Signals
Compile matrix over handler constness variants, mount with each xattr config combination, and create-path tests that call `FhgfsXAttr_init_security()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsXAttrHandlers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FsDirInfo.h -->
# sources/distributed-fs/beegfs/client_module/source/filesystem/FsDirInfo.h

## Purpose
Defines per-open-directory state used to cache directory listing batches, maintain server offsets, and remember metadata-server capabilities.

## Important APIs and Types
`FsDirInfo` embeds `FsObjectInfo` and owns `StrCpyVec` entry names, `UInt8Vec` entry types, `StrCpyVec` entry IDs, `Int64CpyVec` server offsets, current server/local positions, end-of-directory state, and capability bitmasks. `META_CAP_LISTDIR_BUFSIZE_MODE` indicates support for buffer-size-aware directory listing. Inline constructors/destructors and getters/setters manage this state.

## Control Flow
`FsDirInfo_construct()` allocates and initializes vectors, offsets, end flag, capability masks, and virtual uninit pointer. Readdir/listing code appends server responses to the vectors, advances `currentContentsPos`, updates `serverOffset`, and marks `endOfDir`. Capability helpers mark a capability known and supported/unsupported.

## State and Persistence
All state is per directory handle and in memory. It persists only while the open directory file object exists. Vector contents mirror a fetched listing window and are not durable.

## Dependencies and Integration Points
Depends on BeeGFS vector containers, storage definitions, common types, and `FsObjectInfo`. It is used by directory VFS operations that need file-private directory enumeration state.

## Risks
This header contains inline function definitions, so changes affect every includer. Vector triplets must stay index-aligned; corruption yields wrong names/types/entry IDs/offsets. Capability bitmasks are single-byte and assume future capabilities fit. The virtual destructor assumes `uninit` is set through initialization.

## Test Signals
Directory listing tests should cover empty dirs, multi-batch dirs, telldir/seekdir offsets, end-of-dir transitions, vector cleanup, capability probe known/supported states, and allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FsDirInfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FsFileInfo.c -->
# sources/distributed-fs/beegfs/client_module/source/filesystem/FsFileInfo.c

## Purpose
Implements per-open-file state for BeeGFS client operations: access flags, handle type, append mode, cache hit heuristics, sequential offsets, and entry-lock cleanup markers.

## Important APIs and Functions
`FsFileInfo_init()` and `FsFileInfo_construct()` initialize file-private state. `FsFileInfo_incCacheHits()`/`decCacheHits()` clamp the cache heuristic between configured thresholds. Getters/setters expose append, caching, last read/write offsets, handle type, access flags, and entry-lock usage. `FsFileInfo_getIOInfo()` derives a `RemotingIOInfo` from the associated `FhgfsInode`.

## Control Flow
Open paths allocate and initialize `FsFileInfo`, then file operations update offsets and cache hit counters as reads/writes occur. Remote I/O paths call `FsFileInfo_getIOInfo()` before communicating with storage targets. Cleanup uses the virtual `FsFileInfo_uninit()`, currently a no-op.

## State and Persistence
State is in-memory per file descriptor/open file and disappears on close. `cacheHits`, `allowCaching`, and last offsets are adaptive hints, not persisted. `usedEntryLocking` records whether entry lock methods were used and thus whether close cleanup must unlock remotely.

## Dependencies and Integration Points
Depends on `FsObjectInfo`, `FhgfsInode`, `RemotingIOInfo`, and handle/access flag types. It integrates with file open/close, read/write, cache selection, and lock cleanup paths.

## Risks
The cache heuristic is mutable and likely used without extra locking in file-private contexts; sharing assumptions should remain per-open. `FsFileInfo_getIOInfo()` depends on inode state and remote handle validity. The no-op uninit is correct only while no owned allocations are added.

## Test Signals
Open/close tests for all handle types and access modes, sequential/random read heuristic transitions, append-mode writes, O_DIRECT/cache-disabled behavior, entry-lock cleanup, and remote I/O info population from inodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FsFileInfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FsFileInfo.h -->
# sources/distributed-fs/beegfs/client_module/source/filesystem/FsFileInfo.h

## Purpose
Declares the opaque `FsFileInfo` type and the public API for managing per-open-file BeeGFS state.

## Important APIs and Types
Defines cache heuristic constants: initial hits `3`, upper threshold `5`, lower threshold `-5`, and slow-start read length `64 KiB`. Declares construction, initialization, uninitialization, cache hit adjustment, flag/offset/caching/append accessors, `FsFileInfo_getIOInfo()`, and entry-lock usage accessors.

## Control Flow
The header establishes an opaque type boundary: users manipulate state through declared functions rather than direct field access. Read/write code can call cache and offset accessors while remoting code can derive `RemotingIOInfo`.

## State and Persistence
No state is defined in the header beyond constants and forward declarations. Runtime state is implemented in `FsFileInfo.c` and is per open file.

## Dependencies and Integration Points
Includes common definitions, `FhgfsInode`, and `FsObjectInfo`. Forward declarations avoid pulling in remoting and striping definitions for all includers.

## Risks
Changing constants alters cache behavior globally. Because the struct is opaque, any new direct field usage elsewhere would require exposing layout or adding accessors.

## Test Signals
Compile all file operation users, then validate cache threshold behavior, `RemotingIOInfo` generation, and close cleanup paths that rely on entry-lock state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FsFileInfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FsObjectInfo.h -->
# sources/distributed-fs/beegfs/client_module/source/filesystem/FsObjectInfo.h

## Purpose
Provides a small base "class" for file-private BeeGFS objects, distinguishing directory and file state and supporting virtual cleanup.

## Important APIs and Types
`FsObjectType` enumerates `DIRECTORY` and `FILE`. `FsObjectInfo` stores an `App*`, object type, and `uninit` function pointer. Inline functions initialize the base, dispatch virtual destruction, and return the app/type.

## Control Flow
Derived objects call `FsObjectInfo_init()` then assign `uninit`. Generic cleanup calls `FsObjectInfo_virtualDestruct()`, which invokes the derived uninit and frees the object.

## State and Persistence
State is per open file/directory object and is not durable. It links file-private state back to the per-mount `App`.

## Dependencies and Integration Points
Used by `FsDirInfo` and `FsFileInfo`; indirectly integrated with VFS file private data and close/release paths.

## Risks
`FsObjectInfo_virtualDestruct()` does not check whether `uninit` is null. Any partially initialized object passed to it will crash. The pattern relies on C casts from derived structs whose first member is `FsObjectInfo`.

## Test Signals
Construct/destroy file and directory private objects, allocation failure paths that avoid virtual destruction on uninitialized memory, and type dispatch in release paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/FsObjectInfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/ProcFs.c -->
# sources/distributed-fs/beegfs/client_module/source/filesystem/ProcFs.c

## Purpose
Creates, removes, and dispatches BeeGFS procfs entries under `/proc/fs/<module>/<session>`, exposing configuration, status, node lists, target state, and selected runtime toggles.

## Important APIs and Functions
`ProcFs_createGeneralDir()`/`removeGeneralDir()` manage the global parent. `ProcFs_createEntries()`/`removeEntries()` manage per-mount directories. `__ProcFs_open()` binds a seq-file show callback and mount `App`. Read wrappers call `ProcFsHelper_readV2_*`; write wrappers validate user buffers and call `ProcFsHelper_write_*`. Compatibility helpers access proc entry data across kernel APIs.

## Control Flow
Creation builds a session-specific directory from the local node alias and then iterates static tables for read-only and read-write files. Each proc entry stores its show function as data, while the parent directory stores `App*`. Opening a file uses entry data to choose `single_open()` callback and parent data as private app state. Write handlers recover `App*`, run `access_ok`, and delegate parsing/action.

## State and Persistence
Proc entries are runtime kernel objects tied to a mounted `App`. Writes change in-memory runtime flags such as connection retries, netbench mode, remap-connection-failure status, dropped connections, and log levels. No proc data is durable across mount.

## Dependencies and Integration Points
Depends on Linux procfs and seq_file APIs, `ProcFsHelper`, node alias state, and `App` lifecycle from `FhgfsOpsSuper.c`.

## Risks
Creation failure only logs and falls through to cleanup label without removing already-created entries in this function, so partial proc directories can remain until unmount cleanup attempts explicit removals. Removal is manually enumerated; adding an entry to creation tables requires updating removal. Write permissions are owner/group writable; deployment permissions should be intentional.

## Test Signals
Mount/unmount proc tree creation/removal, partial creation failure injection, open/read all entries, write each mutable entry with valid/invalid userspace buffers, and kernel-version coverage for `proc_ops`, `PDE_DATA`, and parent-data access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/ProcFs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/ProcFs.h -->
# sources/distributed-fs/beegfs/client_module/source/filesystem/ProcFs.h

## Purpose
Declares the BeeGFS procfs management and callback interface.

## Important APIs and Types
Exports global and per-mount create/remove functions, seq-file read callbacks for config/build/status/fs UUID/nodes/client info/target states/toggles/log levels, write callbacks for toggles/drop connections/log levels/remap failure, and proc data compatibility helpers.

## Control Flow
The declarations mirror the static proc entry tables in `ProcFs.c`. Open/write callbacks recover `App*` from proc metadata and delegate behavior to `ProcFsHelper`.

## State and Persistence
No owned state. It declares interfaces that operate on per-mount proc entries and `App` runtime state.

## Dependencies and Integration Points
Includes target state store, common types, `App`, Linux procfs, and seq_file. Used by superblock mount lifecycle and procfs implementation.

## Risks
The public surface includes internal-looking `__ProcFs_*` callbacks; external misuse could bypass expected procfs data setup. Declaration drift against `ProcFs.c` or helper tables can break builds.

## Test Signals
Compile with procfs API variants and run proc entry open/read/write smoke tests through the declared callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/ProcFs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/ProcFsHelper.c -->
# sources/distributed-fs/beegfs/client_module/source/filesystem/ProcFsHelper.c

## Purpose
Formats BeeGFS procfs output and implements procfs write-side runtime controls.

## Important APIs and Functions
Read helpers emit mount config, build config, client status counters, fs UUID, node lists and connections, client NICs, target states, connection retry flag, netbench mode, and log levels. Write helpers parse user buffers to set connection retries, remap-connection-failure status, netbench mode, drop all node connections, and set per-topic log levels. Internal printers annotate root ownership and connection counts.

## Control Flow
Read paths use `seq_printf()` and app getters. Node and target-state readers acquire node references, format alias/ID/state/connection details, and release references. Write paths allocate `count+1`, copy from user, trim, parse bool/int/topic-level syntax, mutate `App`, `Config`, `Logger`, or node connection pools, then return `count` or an error.

## State and Persistence
Reads expose current in-memory state: buffer pools, delayed queues, ack queues, node stores, target states, config, and logger levels. Writes mutate runtime-only state; config file values are not rewritten. Dropping connections affects live connection pools.

## Dependencies and Integration Points
Depends on `Config`, `Logger`, list/vector helpers, `NodesTk`, target state store, `InternodeSyncer`, `AckManager`, `InodeRefStore`, `NoAllocBufferStore`, node stores, and procfs wrappers.

## Risks
The write helpers dereference `kernelBuf` immediately after `os_kmalloc(count+1)` without checking allocation, so allocation failure can crash. Large `count` values can also request large allocations. Parsing accepts broad bool/int conversions, so invalid strings may silently become false/zero depending on `StringTk`. Target-state reading aborts output when a referenced node is missing.

## Test Signals
Read all proc files under realistic mounted state, simulate empty/missing node stores, write toggles with `0/1/true/false/invalid`, huge write sizes and allocation failure, log level syntax errors, drop-connections effects, and target-state formatting for meta/storage targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/ProcFsHelper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/ProcFsHelper.h -->
# sources/distributed-fs/beegfs/client_module/source/filesystem/ProcFsHelper.h

## Purpose
Declares procfs formatting and write-control helpers used by `ProcFs.c`.

## Important APIs and Types
Declares V2 seq-file read helpers for config, build config, status, fs UUID, nodes, client info, target states, connection retries, netbench mode, and log levels. Also declares legacy buffer-style read helpers, write helpers for mutable proc entries, and node/root/connection formatting helpers.

## Control Flow
The header separates procfs wrapper mechanics from the actual read/write behavior. `ProcFs.c` calls these functions after resolving the per-mount `App`.

## State and Persistence
No owned state. Functions operate on live `App`, node, target, config, and logger state.

## Dependencies and Integration Points
Includes `App`, common definitions, `NodeStoreEx`, and seq_file. It is an integration boundary between procfs VFS callbacks and BeeGFS internal state.

## Risks
Several legacy buffer-style declarations appear not implemented in the current `ProcFsHelper.c` excerpt, so callers should prefer V2 seq helpers unless legacy implementation exists elsewhere. Declaration drift can hide dead APIs.

## Test Signals
Compile all procfs users, verify each declared V2 helper has a definition, and run proc read/write smoke tests with representative app state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/ProcFsHelper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/helper/IoctlHelper.c -->
# sources/distributed-fs/beegfs/client_module/source/filesystem/helper/IoctlHelper.c

## Purpose
Copies and validates BeeGFS create-file ioctl arguments from userspace across ABI versions and converts preferred target arrays into internal lists.

## Important APIs and Functions
`IoctlHelper_ioctlCreateFileCopyFromUser()`, `V2()`, and `V3()` normalize older user structs into `BeegfsIoctl_MkFileV3_Arg`. `IoctlHelper_ioctlCreateFileTargetsToList()` converts a zero-terminated target array to a `UInt16List`. The `STRDUP_OR_RETURN` macro copies userspace strings with length validation and `strndup_user()`.

## Control Flow
Each copy function copies the fixed userspace struct, manually assigns scalar fields into the output struct to preserve null pointers for cleanup, duplicates required path/name strings, optionally duplicates symlink targets, validates preferred-target byte length against `numTargets + 1`, copies the raw target array, and checks the terminating zero. V1 and V2 fill newer fields with defaults; V3 preserves `storagePoolId`.

## State and Persistence
State is transient kernel allocations inside `outFileInfo` and `outCreateInfo`. Caller owns cleanup even on partial failure. Persistent effects occur later in create-file ioctl handlers, not here.

## Dependencies and Integration Points
Depends on ioctl ABI structs from `FhgfsOpsIoctl.h`, `CreateInfo`, `UInt16List`, `Logger`, storage pool constants, and user-copy helpers. It feeds file creation logic with validated kernel-owned data.

## Risks
On early error after some strings/arrays were allocated, caller must free partial output exactly as documented. Arithmetic `(numTargets + 1) * sizeof(uint16_t)` uses signed/int fields and should be tested for overflow or negative values from malformed userspace. `prefTargetsLen` can be larger than needed and drives `memdup_user()`. Mid-array zero is rejected during list conversion, after copy succeeds.

## Test Signals
Ioctl ABI tests for V1/V2/V3, missing/zero string lengths, invalid userspace pointers, symlink and non-symlink paths, insufficient/unbounded `prefTargetsLen`, missing terminator, zero target in middle, storage pool ID preservation, and cleanup after every partial failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/helper/IoctlHelper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/helper/IoctlHelper.h -->
# sources/distributed-fs/beegfs/client_module/source/filesystem/helper/IoctlHelper.h

## Purpose
Declares helper functions for BeeGFS ioctl create-file argument import and target-list conversion.

## Important APIs and Types
Exports three create-file copy helpers for ioctl ABI versions and `IoctlHelper_ioctlCreateFileTargetsToList()`. Includes `App`, `Config`, OS compatibility, superblock/helper/ioctl definitions, optional compat support, and Linux mount APIs.

## Control Flow
The header provides the boundary used by ioctl handlers: import userspace arguments into a V3-shaped kernel struct, then convert preferred target arrays into internal create info.

## State and Persistence
No owned state. Declared functions allocate output members whose lifetime is managed by their callers.

## Dependencies and Integration Points
Integrated with `FhgfsOpsIoctl` create paths and user-copy validation. Optional `CONFIG_COMPAT` support brings in compat and inode definitions.

## Risks
Callers must pass zero-initialized output structs and must free partial allocations. Missing that convention can leak or double-free.

## Test Signals
Compile ioctl handlers with and without `CONFIG_COMPAT`; run create-file ioctl tests covering all ABI versions and cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/filesystem/helper/IoctlHelper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsCommKit.c -->
# sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsCommKit.c

## Purpose
Implements the generic multi-target BeeGFS storage communication engine for read, write, fsync, and stat-storage operations, including socket acquisition, message serialization, polling, retries, buddy-mirror fallback, RDMA/NVFS mapping, and cleanup.

## Important APIs and Functions
`FhgfsOpsCommKit_initEmergencyPools()`/`releaseEmergencyPools()` manage a mempool-backed 4 KiB header buffer cache. `FhgfsOpsCommkit_communicate()` is the generic state-machine driver. State initializers create file, fsync, and stat-storage target states. Specialized operation tables provide prepare/send/receive callbacks for readfile, writefile, fsync, and stat-storage. `__commkit_start_retry()` handles retry waiters, target-state checks, and buddy fallback. `__commkit_message_genericResponse()` maps server generic responses to BeeGFS errors.

## Control Flow
For each target state, the driver loops through `PREPARE`, `SENDHEADER`, optional `SENDDATA`, `RECVHEADER`, optional `RECVDATA`, `CLEANUP`, `SOCKETINVALIDATE`, `RETRYWAIT`, and `DONE`. Prepare resolves mirror group to target, validates target state, references a storage node, acquires a socket, serializes the request into a pooled header buffer, and moves to send. Polling is nonblocking when at least one state can progress and blocking only when all unfinished states wait. Cleanup releases sockets/nodes/buffers and either finishes or moves to retry wait. Read receives length-prefixed data fragments; write streams iov data and parses write responses; fsync and stat-storage only send headers and parse responses.

## State and Persistence
Per-call state is `CommKitContext` plus per-target `CommKitTargetInfo`/derived structs. It tracks acquired sockets, poll state, retry counts, bufferless/unconnectable states, selected target IDs, node results, and optional RDMA mappings. Persistent effects are remote reads/writes/fsync/stat requests and live socket pool state. Header buffer pools are module-global runtime resources.

## Dependencies and Integration Points
Depends on storage net messages, `RemotingIOInfo`, node stores, target mappers, target state stores, mirror buddy groups, socket and polling toolkit, `Config`, `Logger`, `MessagingTk`, fault injection, RDMA/NVFS APIs, and error conversion conventions. Public wrappers are called by remoting and file I/O layers.

## Risks
This is a high-risk state machine. Resource balance across socket invalidation, normal cleanup, RDMA unmap, node references, and header mempool buffers is critical. Retry behavior changes based on target reachability/consistency and can sleep/reset counters indefinitely for non-good buddy states. The `msgLength > BEEGFS_COMMKIT_MSGBUF_SIZE` path assigns `info->state = -CommKitState_SOCKETINVALIDATE`, which is suspicious because `state` is an enum of positive values and may hit the default `BUG()` path. NVFS detection casts `FileOpState` to vector state when using read/write ops, so callers must pass compatible state layouts.

## Test Signals
Use fault injection for send/receive/poll timeouts, connection acquisition failures, buffer pool exhaustion, malformed/oversized responses, generic TRYAGAIN/INDIRECTCOMMERR, target offline/needs-resync/bad states, buddy fallback, finite/infinite retries, interrupted signals, RDMA map failures, quota write headers, session-check flags, and multi-target mixed success/failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsCommKit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsCommKit.h -->
# sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsCommKit.h

## Purpose
Defines the generic communication-kit public interface and shared per-operation state structures for storage reads, writes, fsync, and stat-storage requests.

## Important APIs and Types
Public APIs initialize/release emergency pools, run generic communication, invoke read/write/fsync/stat-storage communication, and initialize file/fsync/stat-storage state. `CommKitState` enumerates state-machine phases. `CommKitTargetInfo` is the base state for each target. `FileOpState`, `FsyncContext`, `FsyncState`, and `StatStorageState` extend it with operation-specific fields.

## Control Flow
Callers allocate operation states, initialize them, link them into lists, and pass them to the operation-specific communicate wrapper. The driver in `FhgfsOpsCommKit.c` mutates `state`, `nodeResult`, socket/node/header fields, and operation-specific counters.

## State and Persistence
All structs are per I/O request except the emergency pools declared by API. `FileOpState` owns data iterators, offsets, transfer counters, session-check flags, expected result, and optional RDMA mapping pointer. `FsyncContext` stores flags that decide whether a remote fsync message is needed.

## Dependencies and Integration Points
Includes `PathInfo`, optional `RdmaInfo`, iov iterator compatibility, and common comm-kit context definitions. Used by remoting and storage I/O code to communicate with chunk targets.

## Risks
The base struct must remain first in derived states used with `container_of`. Callers must keep state lists alive until communication completes. `nodeResult` uses negative BeeGFS error conventions, which differ from Linux errno.

## Test Signals
Compile call sites, initialize states for single and multi-target operations, verify list linkage, result interpretation, RDMA-enabled builds, and session-check flag propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsCommKit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsCommKitCommon.h -->
# sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsCommKitCommon.h

## Purpose
Provides shared types, constants, callback contracts, and inline poll/error handling for BeeGFS communication-kit implementations.

## Important APIs and Types
Defines `BEEGFS_COMMKIT_MSGBUF_SIZE`, debug flags, retry flags, `CKTargetBadAction`, `CommKitContextOps`, and `CommKitContext`. Inline helpers `__FhgfsOpsCommKitCommon_pollStateSocks()` and `__FhgfsOpsCommKitCommon_handlePollError()` centralize socket polling behavior.

## Control Flow
Operation implementations fill a `CommKitContextOps` table with target-state handling, header preparation, send/receive callbacks, logging hooks, retry flags, and a log context. The poll helper computes timeout based on how many states are waiting/done/unconnectable/bufferless; if any state can still progress, it uses nonblocking poll, otherwise `connMsgLongTimeout`. Poll errors mark `pollTimedOut` so individual states invalidate sockets.

## State and Persistence
`CommKitContext` is per communication run and tracks app/logger/private data/io info, target list, retry/done/acquired connection counts, poll state, logged flags, retry limits, and optional NVFS result. No durable state.

## Dependencies and Integration Points
Depends on logging, write response messages, messaging/socket toolkits, `RemotingIOInfo`, node stores, `Config`, and poll abstractions. Included by both generic and vector comm-kit headers.

## Risks
The invariant comment requires counters never exceed state count; bugs in state transitions can create busy loops or invalid timeouts. Poll timeout logging is rate-limited per context, so repeated failures may only show the first log. `CommKitErrorInjectRate` exists only under debug configuration.

## Test Signals
Unit or integration tests for polling timeout selection, poll timeout/error propagation, signal interruption logging, counter invariants under mixed state sets, and operation callback tables with/without send/receive phases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsCommKitCommon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsCommKitVec.c -->
# sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsCommKitVec.c

## Purpose
Implements the older/page-vector-oriented storage read/write communication path that operates directly on `FhgfsChunkPageVec` pages and updates page completion state.

## Important APIs and Functions
`FhgfsOpsCommKitVec_rwFileCommunicate()` is the public read/write entry. Read stages prepare/send request, receive length headers and page data, handle read errors, invalidate sockets, cleanup, and finish pages. Write stages prepare request, send header, send page data, receive write response, invalidate sockets, cleanup, and finish write pages. Internal helpers compute offsets from page vector progress and set inode writeback counters/timestamps.

## Control Flow
Read prepare resolves buddy mirror target, references node, acquires socket, serializes `ReadLocalFileV2Msg`, sends it, then repeatedly receives int64 length headers and exact data into page buffers. Each full server fragment increments `nodeResult` and may request another header. Write prepare resolves node/socket and serializes `WriteLocalFileMsg`; send-header and send-data push each page buffer synchronously, then receive/deserialize `WriteLocalFileRespMsg`. Public wrapper retries communication errors up to configured retry count and then calls page finalization for both success and non-retriable errors.

## State and Persistence
`FhgfsCommKitVec` owns per-request transfer state: page vector pointer, initial/current offset, target/mirror flags, message buffer, node/socket refs, response/result, successful page count, and loop flag. Write path increments/decrements inode writeback counters and updates last writeback/isize-write time. Page finalization marks read pages uptodate/zeroed/error and write pages complete/error.

## Dependencies and Integration Points
Depends on read/write local file messages, mirror buddy mapper, node stores, sockets, `MessagingTk`, `FhgfsInode`, `FhgfsOpsPages`, `FhgfsChunkPageVec`, and `RemotingIOInfo`. It integrates directly with page cache read/writeback code.

## Risks
This path uses blocking socket calls and a simpler single-state retry loop, unlike the generic nonblocking comm kit. It lacks the generic target-state checks before resolving/acquiring targets, so behavior under offline/bad targets depends on lower layers and retry. Read error handling can set `nodeResult` to internal/communication errors after partial page progress; finalization must not mark unread pages as valid. Write finalization compares server-reported bytes to internal page iteration; mismatches set inode write page error.

## Test Signals
Read/write page-vector tests for full, short, EOF, partial-page, and error reads; write response values less/greater than sent size; socket send/recv failures; interrupted signals; retry exhaustion; buddy primary/secondary flags and forwarding; netbench mode; quota header data; inode writeback counter balance; page uptodate/dirty/error transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsCommKitVec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsCommKitVec.h -->
# sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsCommKitVec.h

## Purpose
Declares the page-vector communication state and entry points for BeeGFS storage read/write operations that work on `FhgfsChunkPageVec`.

## Important APIs and Types
`FhgfsCommKitVec` stores read/write union state, header length, successful page count, page vector, initial offset, target ID, message buffer, mirror/session flags, node/socket refs, result, and loop control. `CommKitVecHelper` carries shared app/logger/io info. Public helpers assign initial state, set first-write-done, compute remaining data size, compute current offset, and run read/write communication.

## Control Flow
Callers build a `FhgfsCommKitVec` with `FhgfsOpsCommKitVec_assignRWfileState()`, optionally set first-write-done/mirror flags, and pass it to `FhgfsOpsCommKitVec_rwFileCommunicate()`. Inline offset calculation derives current offset from page vector total minus remaining size.

## State and Persistence
The state is per page-vector I/O request. It references caller-owned page vector and message buffer. Result state uses BeeGFS negative error codes or positive byte counts.

## Dependencies and Integration Points
Includes remoting, page wrappers, chunk page vectors, Linux fs, common comm-kit types, and `RemotingIOInfo`. Used by page cache I/O paths.

## Risks
Caller must supply a valid 4 KiB-capable message buffer and live page vector. The inline constructor ignores `pageIdx` and `numPages` arguments, which may indicate legacy API drift. Mirror flags must be initialized or explicitly changed before communication.

## Test Signals
Compile users, validate offset/remaining calculations as page vectors advance, check constructor defaults, and run read/write page-vector communication tests for mirror and session-check combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsCommKitVec.h -->
