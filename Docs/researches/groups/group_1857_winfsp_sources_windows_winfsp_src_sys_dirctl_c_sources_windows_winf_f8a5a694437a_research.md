# Group Research: group_1857_winfsp_sources_windows_winfsp_src_sys_dirctl_c_sources_windows_winf_f8a5a694437a

Scope: `Docs/research_subset_a.md` includes `sources/windows/winfsp`. This grouped report covers the five requested WinFsp kernel-driver files and preserves source-tree-aligned marker blocks for final splitting.

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/dirctl.c -->
# File Research: sources/windows/winfsp/src/sys/dirctl.c

Purpose:
Implements WinFsp directory-control IRP handling for filesystem volume devices. It covers `IRP_MN_QUERY_DIRECTORY` and `IRP_MN_NOTIFY_CHANGE_DIRECTORY`, bridging Windows directory query buffers to WinFsp user-mode transaction responses and FSRTL directory change notifications.

Major entry points and roles:
- `FspDirectoryControl` is the `IRP_MJ_DIRECTORY_CONTROL` dispatch routine. It routes only filesystem-volume device objects to `FspFsvolDirectoryControl`.
- `FspFsvolDirectoryControl` switches minor functions between query directory and notify-change-directory.
- `FspFsvolQueryDirectory` validates the file object, directory status, and optional filename pattern, then delegates to retryable query logic.
- `FspFsvolQueryDirectoryRetry` is the main query path. It handles restart/index/single-entry flags, probes or locks the output buffer, consults cached directory info, computes an appropriate user-mode query size, builds `FspFsctlTransactQueryDirectoryKind`, and posts the IRP to the WinFsp I/O queue when kernel cache data is insufficient.
- `FspFsvolDirectoryControlPrepare` allocates a per-process shared buffer via `FspProcessBufferAcquire` and publishes its user-mode address in the request.
- `FspFsvolDirectoryControlComplete` consumes user-mode responses, optionally stores cacheable `FSP_FSCTL_DIR_INFO` buffers in the file node meta cache, copies results into the caller buffer, and reposts to user mode when a response contains no matching entries but scanning should continue.
- `FspFsvolNotifyChangeDirectory` registers change-notification IRPs with WinFsp/FSRTL notification state and hooks completion so the driver can release its device reference after FSRTL completes the IRP.

Directory copying behavior:
- `FspFsvolQueryDirectoryCopy` converts WinFsp `FSP_FSCTL_DIR_INFO` records into Windows `FILE_DIRECTORY_INFORMATION`, `FILE_FULL_DIR_INFORMATION`, `FILE_ID_FULL_DIR_INFORMATION`, `FILE_NAMES_INFORMATION`, `FILE_BOTH_DIR_INFORMATION`, or `FILE_ID_BOTH_DIR_INFORMATION`.
- It applies wildcard matching through `FspFileNameInExpression` unless the cached match-all sentinel is used.
- It supports two marker modes: filename marker strings and `DirectoryMarkerAsNextOffset`, where the marker is a `UINT64` next offset supplied by the filesystem.
- Output records are aligned with `FSP_FSCTL_ALIGN_UP(..., sizeof(LONGLONG))`, and previous records receive `NextEntryOffset`.
- It distinguishes `STATUS_BUFFER_TOO_SMALL` from `STATUS_BUFFER_OVERFLOW`: too small means even the fixed header cannot fit, while overflow may copy a truncated first filename.
- EA-size fields are populated only for EA-capable volumes. For reparse points, the EA-size field is used to carry the reparse tag, matching Windows/NTFS behavior noted in the source comments.

Caching and scan state:
- `FspFsvolQueryDirectoryCopyCache` uses `FileDesc->DirInfoCacheHint` and `FileDesc->DirectoryMarker` to resume scanning cached directory info. It resets hints when cache state changes or restart/index flags force a reset.
- `FspFsvolQueryDirectoryCopyInPlace` performs the same conversion directly from the current response buffer when caching is not used.
- `DirectoryHasSuchFile` converts a first `STATUS_NO_MORE_FILES` into `STATUS_NO_SUCH_FILE` when no matching entry has ever been returned for the current pattern.
- Query-size selection is tuned by volume parameters: directory info cache timeout, `PassQueryDirectoryPattern`, `PassQueryDirectoryFileName`, max component length, and whether the pattern is a full wildcard, partial wildcard, or literal file name.

Concurrency and lifetime:
- Query handling acquires `FSP_FILE_NODE` resources in full or main mode depending on whether it may need user-mode traffic. It uses owner handoff (`FspFileNodeSetOwner`, `FspFileNodeReleaseOwner`) across asynchronous requests.
- User-mode process buffers are released in `FspFsvolQueryDirectoryRequestFini`, attaching back to the original process when needed before `FspProcessBufferRelease`.
- Notify-change completion cannot run pageable cleanup directly, so `FspFsvolNotifyChangeDirectoryCompletion` queues `FspFsvolNotifyChangeDirectoryCompletionWork`, which dereferences the fsvol device and frees the completion context.

Dependencies:
- Declared shared types and helpers come from `sys/driver.h`.
- Uses WinFsp file-node/file-desc APIs for directory markers, meta-cache references, owner transfer, and cache invalidation state.
- Uses Windows kernel APIs and FSRTL concepts: IRPs, MDLs, `MmGetSystemAddressForMdlSafe`, `FsRtlDoesNameContainWildCards`, notify packages, `IoGetTopLevelIrp`, and work items.
- User-mode contract depends on `FSP_FSCTL_TRANSACT_REQ/RSP`, especially `Req.QueryDirectory` and `FSP_FSCTL_DIR_INFO`.

Research notes:
- The most important invariants are buffer bounds, aligned record traversal, and synchronized file-node owner release across retry/completion paths.
- Query-directory cache correctness depends on file-node directory change numbers and `FileDesc` marker/hint state.
- Notify-change deliberately clears `TopLevelIrp` because FSRTL may complete the IRP immediately before normal completion handling can run.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/dirctl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/driver.c -->
# File Research: sources/windows/winfsp/src/sys/driver.c

Purpose:
Defines WinFsp kernel driver initialization, device registration, silo-aware global device setup/finalization, privileged unload handling, and global dispatch/callback tables.

Major entry points and roles:
- `DriverEntry` initializes tracing and side-by-side identity, installs all major IRP dispatch routines, installs I/O prepare/complete callback tables, configures Fast I/O and cache-manager callbacks, initializes silos, process buffers, timers, and global control devices.
- `DriverUnload` reverses normal initialization by finalizing devices, timers, process buffers, silos, and tracing.
- `FspDriverMultiVersionInitialize` enables NX pool runtime behavior and detects OS-version-specific features or routines such as `CcCoherencyFlushAndPurgeCache`, `MdlMappingNoWrite`, and a Windows 10 RS4 reparse-point case-sensitivity fix.
- `FspDriverInitializeDevices` creates disk and network filesystem control devices, optionally creates side-by-side symbolic links, creates the internal MUP device, registers an UNC provider with `FsRtlRegisterUncProviderEx`, registers the disk device as a filesystem, and references primary device objects so explicit unload can delete them later.
- `FspDriverFinalizeDevicesEx` unregisters the disk filesystem, deregisters MUP, removes symlinks, and either fully deletes devices or calls `FspDeviceDoIoDeleteDevice` for unload-time teardown.
- `FspDriverUnload` handles the WinFsp control unload request, requiring host silo context and `SE_LOAD_DRIVER_PRIVILEGE`, calling `ZwUnloadDriver`, finalizing every silo's devices, stopping fsvol I/O queues, and deleting remaining device objects.

Dispatch table setup:
- Driver major functions are wired for create, close, read, write, information, EA, volume information, directory control, filesystem/device control, shutdown, lock, cleanup, and security operations.
- Prepare/complete callbacks map asynchronous user-mode transaction paths back to per-operation handlers, including `FspFsvolDirectoryControlPrepare/Complete` and EA completion routines.
- Fast I/O callbacks include read/write, basic/standard/network-open info, query open, device control, section acquisition, modified-write acquisition, and cache flush acquisition. Cache manager callbacks cover lazy write and read-ahead acquisition/release.

Device topology:
- Disk control device name is based on `FSP_FSCTL_DISK_DEVICE_NAME` plus optional side-by-side suffix and uses `FILE_DEVICE_DISK_FILE_SYSTEM`.
- Network control device uses `FSP_FSCTL_NET_DEVICE_NAME` and `FILE_DEVICE_NETWORK_FILE_SYSTEM`.
- The internal MUP device name includes the container GUID when running in a non-host silo, allowing per-container UNC provider identity.
- Only the disk device is registered with `IoRegisterFileSystem`; the network path is handled through MUP registration.

Failure handling:
- `DriverEntry` tracks partial initialization with booleans and unwinds in reverse order on failure.
- `FspDriverInitializeDevices` similarly unwinds registration, MUP, devices, and symbolic links on failure.
- `FspDriverUnload` is serialized by `FspDriverUnloadMutex` and guarded by `FspDriverUnloadDone`.

Dependencies:
- Consumes declarations, global types, and macros from `sys/driver.h`.
- Uses Windows driver APIs: `IoRegisterFileSystem`, `IoUnregisterFileSystem`, `IoCreateSymbolicLink`, `IoDeleteSymbolicLink`, `FsRtlRegisterUncProviderEx`, `FsRtlDeregisterUncProvider`, `ZwUnloadDriver`, `SeSinglePrivilegeCheck`, object references, and fast I/O dispatch structures.
- Depends on WinFsp device, silo, process-buffer, timer, MUP, and I/O queue subsystems implemented in neighboring driver modules.

Research notes:
- This file is the kernel driver's composition root: it does not implement individual filesystem semantics, but it wires every operation into the common dispatch and transaction framework.
- Silo handling is central. Device creation/finalization is called both at global driver startup and per-silo lifecycle.
- Explicit unload is more involved than normal unload because it asks the service manager to unload the driver, finalizes silo devices, stops fsvol I/O queues, and deletes device lists.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/driver.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/driver.h -->
# File Research: sources/windows/winfsp/src/sys/driver.h

Purpose:
Central internal header for the WinFsp kernel driver. It defines driver-wide macros, dispatch function types, shared data structures, inline helpers, device/file-node contracts, I/O queue and transaction APIs, meta-cache APIs, and compatibility shims used by the sys driver sources.

Major content areas:
- Includes Windows kernel headers (`ntifs.h`, mount/storage/security support) and public WinFsp headers (`winfsp/fsctl.h`, `winfsp/fsext.h`).
- Defines driver names, registry root, security descriptors for control/virtual devices, private status codes (`FSP_STATUS_IOQ_POST`, best-effort post), allocation tags, and I/O increment.
- Provides debug, trace, enter/leave, and return macros that wrap filesystem critical-region entry, top-level IRP management, device references, logging, asynchronous queue posting, and IRP completion.
- Declares all major dispatch routines, I/O prepare/complete callbacks, Fast I/O callbacks, cache-manager callbacks, and resource propagation helpers.

Key structures and protocols:
- `FSP_SILO_GLOBALS` stores per-silo control devices, MUP provider handle, MUP device name buffer, and initialization flags.
- Process-buffer APIs cap shared buffers at `FspProcessBufferSizeMax` (64 KiB) and provide acquire/release/collect primitives used by read/write/query-directory paths.
- IRP context helpers pack a request pointer plus low-bit flags into `Irp->Tail.Overlay.DriverContext[2]`; separate helpers access current request, ordinary flags, and propagated top-level IRP flags.
- `FSP_QEVENT` implements a synchronization-event-like primitive using `KQUEUE`, a dummy entry, and a spin lock, giving LIFO wait behavior and thread-count limiting.
- `FSP_IOQ` models WinFsp's pending/process/retried IRP queue with cancel-safe queues, pending capacity, timeout handling, stopped state, and process buckets.
- `FSP_META_CACHE` is the generic cache behind security descriptors, directory info, stream info, and EA buffers. It tracks timeout, capacity, max item size, item indexes, list state, and hash buckets.
- `FSP_FSCTL_TRANSACT_REQ_HEADER` prefixes user-mode transaction requests with finalizer context, optional response/work item, and aligned request storage. `FspIopRequestContext` exposes per-request context slots used heavily by asynchronous completions.

Device model:
- Device extension kinds identify fsctl, fsmup, fsvrt, and fsvol objects.
- `FSP_DEVICE_EXTENSION` is the base with spin lock, refcount, kind, timer emulation, and delete state.
- `FSP_FSVOL_DEVICE_EXTENSION` is the main mounted volume state: links to fsctl/fsvrt/fsvol devices, swap VPB, volume params, provider, volume prefix, I/O queue, security/dir/stream/EA meta caches, expiration work, delete/rename resources, context tables, volume info cache, notify state, statistics, and filesystem-extension data.
- `FSP_FSVRT_DEVICE_EXTENSION` tracks virtual volume identity, sector size, mount mutex, mountdev state, persistent flag, unique ID, and mount point.
- `FSP_FSMUP_DEVICE_EXTENSION` tracks prefix/class tables for UNC routing.

File object model:
- `FSP_FILE_NODE_NONPAGED` holds resources, section object pointers, nonpaged info spin lock, and meta-cache item indexes.
- `FSP_FILE_NODE` is the FCB-like object: advanced FCB header, ref/open/handle/share state, active/context-table links, file name, cached basic/file info, change numbers for file/security/dir/stream/EA metadata, file lock, oplock state, cache-manager TLS flags, fsvol backpointer, user context, index number, directory/root flags, stream main-file relation, and inline filename buffer.
- `FSP_FILE_DESC` is the per-open CCB-like object: file node, second user context, granted access and per-handle flags, directory query pattern/marker/cache hint, EA query index/change count, and stream main-file handle/object.
- Inline acquisition/release macros standardize main, paging I/O, and full file-node locking, including owner release for asynchronous operations.

Important helper declarations:
- File and EA name validation/upcase/compare/match helpers.
- Registry, GUID, security, mount manager, mountdev, MUP, volume, notification, oplock, cache-manager, safe-MDL, work-item, and IRP hook helpers.
- File-node cache functions for security, directory info, stream info, and EA buffers map to the generic meta-cache dereference routine.
- Volume readiness, notify locking, context table locking, rename/delete resource helpers, and statistics macros.

Compatibility shims:
- Redefines `RtlEqualMemory` for environments where it maps to unavailable `memcmp`.
- Defines local `FSP_FILE_STAT_INFORMATION`, `FSP_FILE_STAT_LX_INFORMATION`, and `FSP_ATOMIC_CREATE_ECP_CONTEXT` for WDKs missing these types or flags.
- Provides multi-version declarations such as `FSP_MV_CcCoherencyFlushAndPurgeCache`.

Dependencies:
- This header is consumed by the WinFsp sys driver C files and depends on public WinFsp FSCTL/FSEXT ABI definitions.
- It is tightly coupled to Windows kernel resource, IRP, file-object, cache-manager, oplock, MUP, mountmgr, and FSRTL notification APIs.
- It declares cross-module interfaces rather than implementing most subsystem behavior.

Research notes:
- This is the most important file for understanding WinFsp kernel-driver invariants. Most source files rely on its enter/leave macros for correct IRP completion and device-reference lifetime.
- The file establishes the core mapping from Windows FSD concepts to WinFsp's user-mode transaction architecture: file nodes/descriptors, per-volume I/O queues, process buffers, and meta caches.
- Any change to `DriverContext` packing, request header layout, file-node lock ownership, or device extension layout would affect many asynchronous code paths.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/driver.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/driver.inf.in -->
# File Research: sources/windows/winfsp/src/sys/driver.inf.in

Purpose:
Template INF file for installing the WinFsp kernel driver package.

Contents:
- `[Version]` declares Windows NT signature, `Volume` setup class, volume class GUID `{71a27cdd-812a-11d0-bec7-08002be2092f}`, `PnpLockdown = 1`, and template placeholders for catalog file and provider.
- `[DestinationDirs]` sets the default destination directory to `12`, the system drivers directory.
- `[DefaultInstall.!ArchDecoration!]` installs by copying files from `Driver.CopyFiles`.
- `[Driver.CopyFiles]`, `[SourceDisksFiles]`, and `[SourceDisksNames]` are parameterized by `!DriverFile!` and identify the driver binary as coming from disk `1 = Disk1`.

Dependencies:
- Build or packaging scripts must substitute `!CatalogFile!`, `!Provider!`, `!ArchDecoration!`, and `!DriverFile!`.
- The resulting INF participates in Windows driver installation/signing flow rather than runtime driver logic.

Research notes:
- The template is intentionally minimal and copy-install oriented.
- Runtime behavior is determined by the driver binary and service configuration; this file mainly captures installation metadata.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/driver.inf.in -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/ea.c -->
# File Research: sources/windows/winfsp/src/sys/ea.c

Purpose:
Implements extended-attribute query and set IRP handling for WinFsp filesystem volume devices. It validates EA buffers, serves cached EA data when available, posts query/set EA transactions to user mode, updates file-node EA cache and metadata, and emits EA change notifications.

Major entry points and roles:
- `FspQueryEa` and `FspSetEa` are major dispatch routines for `IRP_MJ_QUERY_EA` and `IRP_MJ_SET_EA`, routing only fsvol devices to internal handlers.
- `FspFsvolQueryEa` validates EA support and file-object state, tries to serve the query from the file-node EA meta cache, otherwise buffers the user output, creates `FspFsctlTransactQueryEaKind`, stores the file-node owner in request context, and posts to the I/O queue.
- `FspFsvolQueryEaComplete` validates user-mode response EA data, releases the asynchronous file-node owner, reacquires the file node, attempts to populate/reference the EA cache, copies matching EA records into the caller buffer, and returns the resulting EA status.
- `FspFsvolSetEa` buffers and validates the originating process EA input, creates `FspFsctlTransactSetEaKind`, copies the EA input into the request buffer, and posts to user mode with full file-node ownership.
- `FspFsvolSetEaComplete` updates file info from the response, validates optional returned EA data, refreshes or invalidates the cached EA buffer, increments `EaChangeCount`, reports a `FILE_NOTIFY_CHANGE_EA` modification, releases ownership, and completes successfully.

EA copy behavior:
- `FspFsvolQueryEaCopy` chooses between name-list query mode (`EaList` supplied) and index scan mode.
- `FspFsvolQueryEaGetCopy` iterates caller-supplied `FILE_GET_EA_INFORMATION` records, ignores duplicate requested names, validates EA names, searches the source `FILE_FULL_EA_INFORMATION` list case-insensitively, and emits either the matching EA or a zero-length placeholder value for missing names.
- `FspFsvolQueryEaIndexCopy` implements restart/index/single-entry enumeration. It advances from one-based EA indexes, copies aligned `FILE_FULL_EA_INFORMATION` records, updates `FileDesc->EaIndex`, and returns Windows EA statuses such as `STATUS_NO_MORE_EAS`, `STATUS_NO_EAS_ON_FILE`, `STATUS_NONEXISTENT_EA_ENTRY`, `STATUS_BUFFER_TOO_SMALL`, and `STATUS_BUFFER_OVERFLOW`.
- Case preservation is controlled by `VolumeParams.CasePreservedExtendedAttributes`; when disabled, copied EA names are uppercased in place with `FspEaNameUpcase`.

Cache and consistency:
- Cached EA data is referenced through `FspFileNodeReferenceEa` and released via `FspFileNodeDereferenceEa`.
- Query completion validates filesystem-provided EA buffers with `FspEaBufferFromFileSystemValidate`; this validator may alter the buffer, so response buffers are treated as mutable.
- Index-based scans detect stale enumeration state: if no restart/index flag is present and the file-node `EaChangeCount` differs from `FileDesc->EaChangeCount`, the query returns `STATUS_EA_CORRUPT_ERROR`.
- Set completion increments `FileNode->EaChangeCount`, so existing EA enumerations can detect mutation.

Validation and buffer handling:
- Originating-process set buffers are validated with `FspEaBufferFromOriginatingProcessValidate` before being sent to user mode.
- Filesystem-returned EA buffers are validated before caching or copying.
- Query output uses `FspBufferUserBuffer` for buffered write access; set input uses buffered read access.
- Copy routines compute record sizes from `FIELD_OFFSET(FILE_FULL_EA_INFORMATION, EaName) + name length + null byte + value length` and align output advancement with `FSP_FSCTL_ALIGN_UP(..., sizeof(ULONG))`.

Dependencies:
- Uses declarations and macros from `sys/driver.h`, especially `FSP_NEXT_EA`, file-node/file-desc APIs, I/O request APIs, and EA validation helpers.
- Uses Windows EA structures: `FILE_GET_EA_INFORMATION`, `FILE_FULL_EA_INFORMATION`, query/set EA stack parameters, and EA-specific NTSTATUS values.
- Depends on WinFsp user-mode transaction kinds `FspFsctlTransactQueryEaKind` and `FspFsctlTransactSetEaKind`.

Research notes:
- The critical invariants are EA-list structural validation, aligned traversal, case-insensitive matching, and correct distinction between caller-provided invalid EA names versus filesystem-returned inconsistent EA lists.
- The query completion path has a subtle cache branch: if cache insertion is not needed or not possible, it safely copies directly from the response buffer.
- Set EA deliberately accepts an invalid or absent returned EA buffer by invalidating the EA cache, while still using returned file info and completing the set operation successfully.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/ea.c -->