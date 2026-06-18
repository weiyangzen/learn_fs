# subset-b-007718 research

Grouped research for OpenAFS Windows redirector kernel library files. Each section is bounded for reconciliation into the source-tree-aligned per-file outputs.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSCreate.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSCreate.cpp

## Purpose

`AFSCreate.cpp` implements the Windows redirector library's `IRP_MJ_CREATE` handling. It is the central open/create path for the AFS redirector device, volume roots, ordinary files and directories, special pseudo-files such as `_._AFS_IOCTL_._`, and special share names. It converts a Windows create IRP into redirector object lookup, AFS service authorization, FCB/CCB construction, share-access registration, cache-manager setup, and persistent in-memory reference state.

## Important APIs, types, and functions

- `AFSCreate(PDEVICE_OBJECT, PIRP)` is the dispatch entry. It handles control-device opens when the file object or filename is missing, rejects use before `AFSRDRDeviceObject` is initialized, delegates real file-system opens to `AFSCommonCreate`, catches exceptions, and completes the IRP.
- `AFSCommonCreate(PDEVICE_OBJECT, PIRP)` is the main router. It retrieves `AFSDeviceExt`, create disposition/options, desired access, auth group, parses the pathname with `AFSParseName`, handles global-root opens, performs name lookup with `AFSLocateNameEntry`, and dispatches to root/open/create/overwrite/target-directory/special-file paths.
- `AFSOpenAFSRoot` and `AFSOpenRoot` open the synthetic AFS global root and a volume root. `AFSOpenRoot` validates/enumerates the root, calls `AFSProcessRequest(AFS_REQUEST_TYPE_OPEN_FILE)`, initializes the root FCB, checks share access, allocates a CCB, and marks the object held by the service.
- `AFSProcessCreate` creates a new child by calling `AFSCreateDirEntry`, evaluating the new node, initializing its FCB/CCB, reporting directory notifications, setting share access, updating parent child-open counts, and rolling back the directory entry on failure.
- `AFSOpenTargetDirectory` supports `SL_OPEN_TARGET_DIRECTORY` for rename-style operations. It opens the parent directory, rewrites `FileObject->FileName` to the target component, and reports whether the target exists.
- `AFSProcessOpen` opens an existing object. It validates the entry, handles pending delete and delete-on-close, checks image-section conflicts for write/delete opens, asks the service for granted access, validates that access with `AFSCheckAccess`, builds a CCB, updates share access and open counts, and records service-held state.
- `AFSProcessOverwriteSupersede` handles `FILE_OVERWRITE`, `FILE_OVERWRITE_IF`, and `FILE_SUPERSEDE`. It rejects read-only volumes/files, validates and initializes the FCB, checks truncation safety with `MmCanFileBeTruncated`, zeros sizes under paging I/O synchronization, trims extents, calls `AFSUpdateFileInformation`, updates attributes, and calls `CcSetFileSizes`.
- `AFSControlDeviceCreate` allows kernel-mode control-device opens and rejects user-mode direct opens.
- `AFSOpenIOCtlFcb` creates/opens the per-directory PIOCtl pseudo FCB and sends `AFS_REQUEST_TYPE_PIOCTL_OPEN` to the service.
- `AFSOpenSpecialShareFcb` opens special-share pipe-like entries and sends `AFS_REQUEST_TYPE_PIPE_OPEN`.
- Core types include `AFSVolumeCB`, `AFSObjectInfoCB`, `AFSDirectoryCB`, `AFSFcb`, `AFSCcb`, `AFSNameArrayHdr`, `AFSFileOpenCB`, `AFSFileOpenResultCB`, and open/close request Cbs for PIOCtl and pipes.

## Control flow

The create path first separates control-device opens from file-system opens. File-system opens require a global root and a non-shutdown redirector device. `AFSCommonCreate` obtains the caller auth group, ensures the global root is enumerated, and parses the name into a root-relative file name, parsed-name state, root filename, volume, parent directory entry, and name array.

If no volume is returned, the request targets the synthetic `\\Server\\GlobalRoot` layer. The code strips leading/trailing separators, permits only the root itself, `_._AFS_IOCTL_._`, or a special-share name under an already located special parent, and otherwise returns name-not-found.

For real volumes, the code validates the path format, then performs lookup. Reparse handling has two modes. Without a reparse policy override, lookup either substitutes target names normally or, if `FILE_OPEN_REPARSE_POINT` is set, disables mount-point, symlink, and DFS-link target evaluation. With `AFSIgnoreReparsePointToFile()` in effect, the code clones the name array and may run a first lookup that ignores the reparse-open flag, then reruns lookup with target evaluation disabled if the policy does not apply. Lookup can also return `STATUS_REPARSE`, in which case the IRP information is set to `IO_REPARSE`.

Once lookup is complete, `SL_OPEN_TARGET_DIRECTORY` routes to `AFSOpenTargetDirectory`; create dispositions route to `AFSProcessCreate`; missing final components route to PIOCtl or name-not-found; volume roots route to `AFSOpenRoot`; overwrite/supersede dispositions route to `AFSProcessOverwriteSupersede`; all other existing objects route to `AFSProcessOpen`. Successful opens then bind `FileObject->FsContext` and `FsContext2`, set section object pointers for file/PIOCtl FCBs, mark cacheability or no-buffering, set fast I/O read for execute opens, update last access time, insert the CCB on the FCB, and transfer the parsed full name/name array into the CCB.

## State and persistence behavior

This file owns the lifetime-sensitive state transitions for open objects. It increments and decrements volume references with explicit reference reasons, directory-entry `DirOpenReferenceCount`, FCB `OpenReferenceCount` and `OpenHandleCount`, parent `ChildOpenHandleCount` and `ChildOpenReferenceCount`, and CCB insertion/removal. It sets durable in-memory flags such as `AFS_OBJECT_HELD_IN_SERVICE`, `AFS_DIR_ENTRY_PENDING_DELETE`, `AFS_OBJECT_FLAGS_DIRECTORY_ENUMERATED`, `AFS_FCB_FLAG_FILE_MODIFIED`, and `CCB_FLAG_MASK_OPENED_REPARSE_POINT`.

State persisted outside the kernel library is mediated through service calls. Open/create access is held with `AFS_REQUEST_FLAG_HOLD_FID`; failed post-service opens release service access via `AFS_REQUEST_TYPE_RELEASE_FILE_ACCESS`; overwrite/supersede pushes changed file size/timestamps/attributes through `AFSUpdateFileInformation`; PIOCtl and pipe opens notify the service with dedicated request types.

## Dependencies and integration points

The implementation depends on WDK IRP and file-system APIs (`IoGetCurrentIrpStackLocation`, `IoCheckShareAccess`, `IoSetShareAccess`, `IoUpdateShareAccess`, `MmFlushImageSection`, `MmCanFileBeTruncated`, `CcSetFileSizes`, section object pointers, file object flags, and create dispositions/options). It also depends on redirector-local infrastructure declared in `AFSCommon.h`: name parsing/location, auth-group retrieval, volume/object/Fcb/Ccb initialization, directory enumeration/validation, service request callbacks, extent trimming, notification reporting, debug tracing, exception filtering, and custom pool allocation/free routines.

It integrates with `AFSDirControl.cpp` through `AFSFsRtlNotifyFullReportChange` after create operations, with cache and extent code through FCB section/extents state, with service/user-mode communication through `AFSProcessRequest`, and with the framework through global callback pointers defined in `AFSData.cpp`.

## Risks and edge cases

- Reference balancing is complex. Many paths switch `pVolumeCB`, `pParentDirectoryCB`, `pDirectoryCB`, and `pNameArray` ownership after `AFSLocateNameEntry`; missed ownership transitions can leak or prematurely free live objects.
- The two-pass reparse policy path clones and restores name arrays and root names. Bugs here can produce wrong target semantics, stale substituted names, or pool misuse.
- Create and overwrite paths make local object state changes before or around service calls. Rollback paths must keep directory trees, FCB sizes, extents, and service-held access synchronized.
- Section object operations are protected by exception handlers, but failures map to sharing, delete, or user-mapped-file errors. These paths are important for executable files and memory-mapped files.
- Control-device create permits only kernel callers. Any future relaxation needs to preserve the model that user-mode access goes through the file-system/security component.
- Special pseudo-files intentionally do not release some parent directory references in their helper routines; callers must preserve those ownership assumptions.

## Test signals

Useful tests include root open before and after initialization, shutdown-mode create rejection, full global-root enumeration, exact PIOCtl and special-share opens, create/open/open-if/overwrite/supersede matrix coverage, delete-on-close on files/directories/root, `SL_OPEN_TARGET_DIRECTORY` rename preparation, share-access conflicts, read-only volume and read-only attribute rejection, symlink/mountpoint/DFS reparse policy behavior, service open denial and access-mask denial, memory-mapped overwrite rejection, image-section write/delete conflicts, failure-injection for CCB/FCB/name-array allocation, and leak/reference-count tracing around all failure exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSCreate.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSData.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSData.cpp

## Purpose

`AFSData.cpp` is the single definition unit for the redirector library's global variables. It defines device objects, shared names, cache configuration, debug/control flags, callback entry points supplied by the framework, security globals, global directory entries, and OS-version state. The file has no active control flow beyond initialization through static zero/default values, but it is foundational because most other library files use these symbols as shared process-wide kernel state.

## Important APIs, types, and functions

- `#define NO_EXTERN` before including `AFSCommon.h` selects definitions instead of declarations for the shared globals.
- Device/global handles: `AFSLibraryDriverObject`, `AFSLibraryDeviceObject`, `AFSControlDeviceObject`, `AFSRDRDeviceObject`, and `AFSSysProcess`.
- Name globals: `AFSRegistryPath`, `AFSServerName`, `AFSMountRootName`, `AFSPIOCtlName`, and `AFSGlobalRootName`.
- Root and directory globals: `AFSGlobalRoot`, `AFSSpecialShareNames`, `AFSGlobalDotDirEntry`, and `AFSGlobalDotDotDirEntry`.
- Debug/cache/control state: `AFSDebugFlags`, `AFSLibCacheManagerCallbacks`, `AFSLibControlFlags`, `AFSLibCacheBaseAddress`, `AFSLibCacheLength`, `AFSDebugTraceFnc`, and `AFSDbgLogMsg`.
- Framework callbacks: `AFSProcessRequest`, `AFSAddConnectionEx`, `AFSExAllocatePoolWithTag`, `AFSExFreePoolWithTag`, `AFSDumpTraceFilesFnc`, and `AFSRetrieveAuthGroupFnc`.
- Security globals: `AFSRtlSetSaclSecurityDescriptor`, `AFSDefaultSD`, `AFSRtlSetGroupSecurityDescriptor`, and `SeWorldSidAuthority`.
- System state: `AFSRtlSysVersion`.

## Control flow

There are no functions in this file. Load-time behavior is controlled by C/C++ global initialization. Most pointer globals start as `NULL`, integral flags as `0`, `AFSDbgLogMsg` defaults to `AFSDefaultLogMsg`, and `AFSDumpTraceFilesFnc` defaults to `AFSDumpTraceFiles_Default`. Later initialization paths, especially `AFSInitializeLibrary` reached from `AFSDevControl.cpp`, are expected to populate the framework callbacks and global device/name/security/cache state before dispatch handlers use them.

## State and persistence behavior

The state is process-wide for the loaded kernel library. It persists for the lifetime of the driver/library load and is shared by create, directory, cache, service, connection, and debug paths. Because callback pointers and device-object pointers begin as null, dispatch paths guard some use sites, such as `AFSCreate` rejecting file-system opens until `AFSRDRDeviceObject` and `AFSGlobalRoot` are ready. Other use sites assume initialization has already succeeded.

The global directory entries for `"."`, `".."`, special share names, and the PIOCtl name shape enumeration and open behavior across all CCBs. The cache-manager globals hold shared callbacks/base/length used by cache and extent code. The debug callback pointers control whether tracing routes to defaults or framework-supplied logging.

## Dependencies and integration points

Every file that includes `AFSCommon.h` depends on these definitions. `AFSCreate.cpp` uses `AFSRDRDeviceObject`, `AFSGlobalRoot`, `AFSPIOCtlName`, `AFSSpecialShareNames`, framework allocation/free callbacks, debug callbacks, and auth/service callbacks. `AFSDirControl.cpp` uses `AFSControlDeviceObject`, `AFSGlobalDotDirEntry`, `AFSGlobalDotDotDirEntry`, `AFSPIOCtlName`, and allocation/free callbacks. `AFSDevControl.cpp` initializes many of these globals indirectly through library initialization and can replace `AFSDebugTraceFnc` through `IOCTL_AFS_CONFIG_LIBRARY_TRACE`.

## Risks and edge cases

- These globals are mutable shared kernel state. Initialization ordering is critical; null callbacks or device objects can crash callers that do not explicitly guard them.
- Callback pointer replacement and use require concurrency discipline outside this file. The debug trace callback is updated with an interlocked operation in `AFSDevControl.cpp`, but most other initialization is expected to occur before concurrent file-system traffic.
- `extern "C"` exposes unmangled names, which is important for C/driver integration but also means duplicate definitions would be linker-visible if `NO_EXTERN` is misused elsewhere.
- Default debug and dump callbacks reduce startup fragility, but allocation, auth retrieval, service requests, and connection callbacks have no safe default here.

## Test signals

Initialization tests should verify that `AFSInitializeLibrary` fills all required callbacks and globals before file-system dispatch begins, that create/open paths return readiness failures while root/device globals are unset, that debug tracing works before and after `IOCTL_AFS_CONFIG_LIBRARY_TRACE`, and that unload/reinitialize paths reset or replace global state without stale callback/device-object use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSData.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSDevControl.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSDevControl.cpp

## Purpose

`AFSDevControl.cpp` implements the library dispatch handler for `IRP_MJ_DEVICE_CONTROL`. It validates IOCTL buffer sizes and caller mode, invokes initialization and management routines, updates cache/network/volume state, answers status queries, and completes the IRP. This file is the kernel-library side of the control channel used by the file-system/framework component and network provider support code.

## Important APIs, types, and functions

- `AFSDevControl(PDEVICE_OBJECT, PIRP)` is the only function. It reads `Parameters.DeviceIoControl.IoControlCode`, switches on the IOCTL, validates `SystemBuffer` lengths, calls the appropriate AFS helper, sets `Irp->IoStatus.Information` where needed, catches exceptions, and completes the IRP.
- Initialization IOCTL: `IOCTL_AFS_INITIALIZE_LIBRARY_DEVICE` accepts `AFSLibraryInitCB`, requires `KernelMode`, and runs `AFSInitializeLibrary`, `AFSInitializeWorkerPool`, `AFSInitializeGlobalDirectoryEntries`, and `AFSInitializeSpecialShareNameList`.
- Connection IOCTLs: `IOCTL_AFS_ADD_CONNECTION`, `IOCTL_AFS_CANCEL_CONNECTION`, `IOCTL_AFS_GET_CONNECTION`, `IOCTL_AFS_LIST_CONNECTIONS`, and `IOCTL_AFS_GET_CONNECTION_INFORMATION` use `AFSNetworkProviderConnectionCB` and related result buffers.
- Extent/cache IOCTLs: `IOCTL_AFS_SET_FILE_EXTENTS`, `IOCTL_AFS_RELEASE_FILE_EXTENTS`, `IOCTL_AFS_SET_FILE_EXTENT_FAILURE`, and `IOCTL_AFS_INVALIDATE_CACHE`.
- State/status IOCTLs: `IOCTL_AFS_NETWORK_STATUS`, `IOCTL_AFS_VOLUME_STATUS`, `IOCTL_AFS_STATUS_REQUEST`, and `IOCTL_AFS_GET_OBJECT_INFORMATION`.
- Trace configuration: `IOCTL_AFS_CONFIG_LIBRARY_TRACE` accepts `AFSDebugTraceConfigCB` and updates `AFSDebugTraceFnc`.
- The internal Windows remote redirector IOCTL `0x140390` (`IOCTL_LMR_DISABLE_LOCAL_BUFFERING`) is recognized and explicitly returns `STATUS_NOT_SUPPORTED`.

## Control flow

The dispatch handler obtains the stack location and IOCTL code, then processes one switch arm. Most arms perform simple structural validation before forwarding to the corresponding implementation. Variable-length input is checked with `FIELD_OFFSET` arithmetic, notably remote-name lengths for add-connection and extent-array length for set-extents. Some operations write results into the same `AssociatedIrp.SystemBuffer` used for input, consistent with buffered IOCTLs.

Initialization is special. It is accepted only from kernel mode, checks for an `AFSLibraryInitCB`, and then performs four ordered initialization stages. A failure in any stage breaks out and completes the IOCTL with that failure. The default arm returns `STATUS_NOT_IMPLEMENTED` and notes that security checks elsewhere mean new IOCTLs must also be added in the framework communication support file.

After the switch, exception handling maps unexpected faults to `STATUS_UNSUCCESSFUL`, emits trace/dump output, writes `Irp->IoStatus.Status`, completes the request through `AFSCompleteRequest`, and returns the final status.

## State and persistence behavior

This file mutates global library state indirectly. Initialization populates device/library globals, worker threads, synthetic directory entries, and special-share lists. Connection IOCTLs update network-provider mappings. Extent IOCTLs update cached file extent state. Invalidate-cache, network-status, and volume-status IOCTLs alter runtime cache/reachability state. Trace configuration changes the global debug trace callback pointer.

The handler itself stores no persistent local state. `Irp->IoStatus.Information` is part of the public contract for result sizes; several setter operations explicitly reset it to zero.

## Dependencies and integration points

`AFSDevControl` depends on WDK buffered IOCTL conventions (`Irp->AssociatedIrp.SystemBuffer`, `InputBufferLength`, `OutputBufferLength`, `RequestorMode`) and redirector helper routines declared through `AFSCommon.h`. It integrates with `AFSData.cpp` by initializing and updating global symbols, with worker-pool/cache/extent code through the extent and cache IOCTLs, with network-provider support through connection IOCTLs, and with object/status code through status query routines. The default-arm comment identifies `..\\fs\\AFSCommSupport.cpp` as the framework-side companion for IOCTL exposure and security checks.

## Risks and edge cases

- IOCTLs share the same system buffer for input and output. Length validation must remain exact for every structure, especially variable-length connection names and extent arrays.
- `IOCTL_AFS_SET_FILE_EXTENTS` reads `pExtents->ExtentCount` only after ensuring the buffer contains that field, then validates the full array. This pattern must be preserved for any variable-length additions.
- Initialization is ordered but partial failure cleanup is not visible in this file. Callers must handle retry/unload safety in the underlying initialization routines.
- `IOCTL_AFS_CONFIG_LIBRARY_TRACE` uses `InterlockedCompareExchangePointer` with identical exchange/comparand values from the incoming config, which effectively only updates when the old value already equals the new value. That may be intentional as a guarded compare, or it may be a suspicious no-op pattern worth reviewing against intended trace reconfiguration behavior.
- Unknown IOCTL behavior is tied to security checks in a companion framework file. Adding a new IOCTL in only one side can make it unreachable or unsafe.

## Test signals

Tests should cover kernel-mode versus user-mode initialization access, undersized buffers for every IOCTL, variable-length add-connection and set-extents boundary cases, status/output length reporting, initialization-stage failures, unsupported `0x140390`, trace-callback configuration behavior, exception-path completion, and cross-checking that every accepted IOCTL is also allowed and marshalled by the framework communication layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSDevControl.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSDirControl.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSDirControl.cpp

## Purpose

`AFSDirControl.cpp` implements `IRP_MJ_DIRECTORY_CONTROL` for the Windows OpenAFS redirector library. It handles directory enumeration (`IRP_MN_QUERY_DIRECTORY`), change notification registration (`IRP_MN_NOTIFY_CHANGE_DIRECTORY`), snapshot-based enumeration stability, pseudo-entry handling for `"."`, `".."`, and PIOCtl, and FsRtl notification reporting for directory mutations.

## Important APIs, types, and functions

- `AFSDirControl(PDEVICE_OBJECT, PIRP)` dispatches minor functions to `AFSQueryDirectory` or `AFSNotifyChangeDirectory`, completes non-pending IRPs, and catches exceptions.
- `AFSQueryDirectory(PIRP)` validates that the file object references a directory/root FCB, establishes the query mask and restart/index state on the CCB, enumerates or verifies the backing directory, snapshots it, locks the caller buffer, and packs one or more directory information records.
- `AFSNotifyChangeDirectory(PIRP)` validates the directory, rejects deleted/pending-delete state, and registers the notification through `AFSFsRtlNotifyFullChangeDirectory`.
- `AFSLocateNextDirEntry(AFSObjectInfoCB *, AFSCcb *)` advances `Ccb->CurrentDirIndex`, returns dot/dot-dot pseudo-entries, PIOCtl pseudo-entry, or a snapshot-backed directory entry, and returns it with `DirOpenReferenceCount` held.
- `AFSLocateDirEntryByIndex` locates an entry by a stored directory index within the CCB snapshot.
- `AFSSnapshotDirectory(AFSFcb *, AFSCcb *, BOOLEAN)` creates a per-CCB snapshot of directory entry name hashes, skipping deleted and pending-delete entries and avoiding duplicate hashes.
- `AFSFsRtlNotifyFullChangeDirectory` builds a stable notify mask from the parent object's FID and calls `FsRtlNotifyFilterChangeDirectory`.
- `AFSFsRtlNotifyFullReportChange` builds a FID/component name path and calls `FsRtlNotifyFilterReportChange`.
- `AFSNotifyReportChangeCallback` is a framework-safe callback stub for notification filtering.
- `AFSIsNameInSnapshot` detects duplicate hashes while snapshotting.
- `AFSProcessDirectoryQueryDirect` optimizes a non-wildcard query against an unenumerated directory by asking the service to evaluate only the named target.

## Control flow

`AFSQueryDirectory` starts by retrieving `AFSFcb` and `AFSCcb` from the file object. It accepts only directory/root node types and sets an enumeration event on the FCB. Initial queries take the FCB resource exclusively, construct the query mask, and set flags such as `CCB_FLAG_FULL_DIRECTORY_QUERY`, `CCB_FLAG_DIR_OF_DIRS_ONLY`, `CCB_FLAG_MASK_CONTAINS_WILD_CARDS`, and `CCB_FLAG_MASK_PIOCTL_QUERY`. Subsequent queries take the resource shared and respect direct-query completion state.

The directory tree lock is then acquired. If the directory has not been enumerated and the mask is a non-wildcard name, `AFSProcessDirectoryQueryDirect` can query the service for just that entry. Symlink direct queries that need target attributes return `STATUS_REPARSE_OBJECT`, causing the normal enumerate/snapshot path to run. Otherwise, the directory is enumerated with `AFSEnumerateDirectory`; if marked verify, `AFSVerifyEntry` runs and the CCB snapshot is refreshed.

After snapshot setup and optional PIOCtl entry initialization, index/restart flags update `CurrentDirIndex`. The code then computes the base record length for the requested information class and loops through `AFSLocateNextDirEntry`. Each entry is filtered for delete state, mask match, directory-only semantics, and wildcard expression matching. It validates entries marked verify, computes reparse/directory/hidden attributes, fills the requested `FILE_*_DIR_INFORMATION` shape, copies as much of the filename as fits, links `NextEntryOffset`, updates `IoStatus.Information`, and handles `STATUS_BUFFER_OVERFLOW`, `STATUS_NO_SUCH_FILE`, or `STATUS_NO_MORE_FILES`.

Change notify registration builds a synthetic path based on the directory object's FID rather than the user-visible name. Reporting changes similarly uses parent FID plus component name and reports through FsRtl using the CCB as target context.

## State and persistence behavior

Directory enumeration state is stored per CCB: mask name, flags, current directory index, directory snapshot, auth group, full filename/name array, and notify mask. The snapshot persists across query calls for stable enumeration even if the underlying directory tree changes, but entries are resolved back through the live case-sensitive tree when returned.

Directory-level state lives in `AFSObjectInfoCB::Specific.Directory`, including tree locks, node counts, list heads, case-sensitive tree heads, and optional PIOCtl directory CBs. The file also updates `LastAccessCount` on snapshot entries and sets/clears enumeration state through `AFSSetEnumerationEvent` and `AFSClearEnumerationEvent`.

Notification state is held in the control device extension's `NotifySync` and `DirNotifyList`, keyed by FID-derived masks stored in CCBs.

## Dependencies and integration points

The file depends on WDK directory APIs and structures (`FILE_DIRECTORY_INFORMATION`, `FILE_FULL_DIR_INFORMATION`, `FILE_BOTH_DIR_INFORMATION`, `FILE_NAMES_INFORMATION`, `FILE_ID_*` variants, `FsRtlIsNameInExpression`, `FsRtlDoesNameContainWildCards`, `FsRtlNotifyFilterChangeDirectory`, and `FsRtlNotifyFilterReportChange`). It integrates with service/name code through `AFSEnumerateDirectory`, `AFSVerifyEntry`, `AFSValidateEntry`, `AFSRetrieveFileAttributes`, and `AFSEvaluateTargetByName`.

It interacts with `AFSCreate.cpp` through CCB initialization, name-array/full-name storage, PIOCtl directory entry creation, and notification reporting after creates. It uses globals from `AFSData.cpp`: `AFSRDRDeviceObject`, `AFSControlDeviceObject`, `AFSPIOCtlName`, `AFSGlobalDotDirEntry`, and `AFSGlobalDotDotDirEntry`.

## Risks and edge cases

- Buffer packing is sensitive. The first record may be partial with `STATUS_BUFFER_OVERFLOW`; later records must be omitted if they do not fit, with the index backed up so a later query can return them.
- Snapshot entries store hashes, not direct pointers. This avoids stale pointers but depends on hash uniqueness checks and live tree lookup.
- Direct non-wildcard service queries skip full enumeration but cannot fully handle symlink target attributes, so the `STATUS_REPARSE_OBJECT` fallback is important.
- Lock ordering spans FCB resources, directory tree locks, and CCB locks. PIOCtl initialization temporarily drops and reacquires locks, which is a concurrency-sensitive path.
- Dot-name hiding and reparse-point-to-file policy alter returned attributes and can affect user-visible enumeration behavior.
- Notification masks are FID-derived synthetic paths. They must match report paths exactly or notifications will be missed.

## Test signals

Tests should cover all supported information classes, empty directories, dot/dot-dot relative and root enumeration, restart scan, index-specified scan, single-entry scan, wildcard and case-insensitive masks, directory-only masks (`<` and `*.`), PIOCtl mask enumeration, non-wildcard direct query before enumeration, symlink fallback from direct query, small output buffers and overflow behavior, deleted/pending-delete skips, verify/enumerate refresh, hide-dot-names attributes, mountpoint/DFS/symlink reparse attributes, notify registration, notify report delivery, and concurrent enumeration while directory contents change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSDirControl.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSEa.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSEa.cpp

## Purpose

`AFSEa.cpp` implements the redirector library dispatch handlers for extended attributes: `IRP_MJ_QUERY_EA` and `IRP_MJ_SET_EA`. OpenAFS on this path does not support EAs, so both handlers consistently return `STATUS_EAS_NOT_SUPPORTED` after tracing and completing the IRP.

## Important APIs, types, and functions

- `AFSQueryEA(PDEVICE_OBJECT, PIRP)` is the query-EA dispatch handler. It retrieves the current stack location only for trace context, emits a file-object trace message, completes the request with `STATUS_EAS_NOT_SUPPORTED`, catches exceptions, and returns that status.
- `AFSSetEA(PDEVICE_OBJECT, PIRP)` is the set-EA dispatch handler. It follows the same pattern and also returns `STATUS_EAS_NOT_SUPPORTED`.
- Both functions use `IoGetCurrentIrpStackLocation`, `AFSDbgTrace`, `AFSCompleteRequest`, `AFSExceptionFilter`, and `AFSDumpTraceFilesFnc`.

## Control flow

Each function initializes `ntStatus` to `STATUS_EAS_NOT_SUPPORTED`, fetches `pIrpSp`, enters a guarded block, logs the file object pointer, completes the IRP with the unsupported status, and returns. If an exception occurs, the exception handler logs the exception and dumps traces; the status remains the unsupported-EA status because no alternate status is assigned in the handler.

## State and persistence behavior

These handlers do not allocate memory, mutate FCB/CCB state, call the AFS service, or persist any metadata. They only complete the incoming IRP. The absence of EA support is therefore stateless and uniform for all file objects.

## Dependencies and integration points

The file depends on common dispatch support from `AFSCommon.h`, especially tracing, request completion, and exception filtering. It integrates with the driver's major-function dispatch table as the implementation for query/set EA requests. It deliberately does not integrate with create/open, object information, cache, service, or directory code.

## Risks and edge cases

- The behavior is intentionally simple, but callers expecting Windows EA semantics will always receive unsupported status.
- Completion occurs inside the `__try` block. If completion itself faults, the exception path logs/dumps but does not attempt a second completion.
- Any future EA support would need to add buffer probing/validation, service contracts, metadata persistence, and access checks; none of that scaffolding exists here.

## Test signals

Tests should verify that query-EA and set-EA IRPs complete exactly once with `STATUS_EAS_NOT_SUPPORTED`, that the returned status is independent of file type and open mode, that tracing does not require a non-null file object beyond what `IoGetCurrentIrpStackLocation` supplies, and that unsupported EA behavior does not alter FCB/CCB reference counts or service state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSEa.cpp -->
