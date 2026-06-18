# subset-b-007716 Research

Grouped research for the OpenAFS Windows redirector filesystem layer files under `sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSInit.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSInit.cpp

## Purpose
`AFSInit.cpp` contains `DriverEntry`, the kernel driver's primary initialization routine. It establishes global driver state, reads registry configuration, initializes tracing/dump support, creates the secure control device and symbolic link, installs dispatch and Fast I/O tables, creates control queues/resources, registers shutdown and process-notify callbacks, initializes the redirector device, and seeds the system process entry used by auth-group tracking.

## Important APIs, Control Flow, And State
`DriverEntry` first initializes global strings and OS-version-dependent callbacks, including `ZwSetInformationToken` discovery and an XP-only service table fallback on 32-bit builds. It reads registry settings through `AFSReadRegistry`, enforces optional clean-shutdown policy, allocates `AFSRegistryPath`, and records dirty shutdown state with `AFSUpdateRegistryParameter` when requested. It creates `AFSDeviceObject` via `IoCreateDeviceSecure`, initializes notification state, calls `AFSInitializeControlDevice`, and exposes `\\??\\AFSRedirector`.

The dispatch table routes IRP majors to local shims such as `AFSCreate`, `AFSRead`, `AFSWrite`, `AFSDevControl`, `AFSShutdown`, `AFSLockControl`, security handlers, and `AFSSystemControl`, with all unhandled operations defaulting to `AFSDefaultDispatch`. It also fills `AFSFastIoDispatch` and cache-manager callbacks used by the library-backed cache/Fcb layer. Runtime state initialized here includes worker queue events/resources, `AFSSysProcess`, process tree root via `AFSInitializeProcessCB`, `AFSCacheManagerCallbacks`, and `AFSDbgLogLock`.

## Dependencies And Integration Points
This file ties together registry helpers, logging, dump-file support, generic control-device setup, process/auth support, RDR device registration, Fast I/O handlers, cache manager callbacks, and all filesystem IRP dispatch modules declared in `AFSCommon.h`. It depends heavily on Windows kernel APIs: `IoCreateDeviceSecure`, `IoCreateSymbolicLink`, `IoRegisterShutdownNotification`, `PsSetCreateProcessNotifyRoutine*`, `MmGetSystemRoutineAddress`, `RtlGetVersion`, and FSD/Fast I/O structures.

## Risks And Test Signals
Initialization has many partially initialized resources; failure unwinding must keep `AFSRegistryPath`, symbolic links, control device resources, shutdown registration, and debug locks balanced. Process-notify registration deliberately ignores final registration status by resetting `ntStatus` to success, so callback absence is a possible diagnostic gap. Clean-shutdown registry flags can prevent driver load. Test signals include driver load/unload under missing registry values, clean/unclean shutdown policy, XP/Vista+ callback paths, control device access ACLs, symbolic-link communication, Fast I/O table population, and failure injection for each allocation or device creation step.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSInit.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSInternalDevControl.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSInternalDevControl.cpp

## Purpose
`AFSInternalDevControl.cpp` implements the `IRP_MJ_INTERNAL_DEVICE_CONTROL` dispatch entry. In this filesystem redirector layer it is a stub: internal device controls are not implemented and every request is completed locally with `STATUS_NOT_IMPLEMENTED`.

## Important APIs, Control Flow, And State
`AFSInternalDevControl` retrieves the current stack location but does not inspect any control code. Inside structured exception handling, it calls `AFSCompleteRequest(Irp, STATUS_NOT_IMPLEMENTED)` and returns that status. The `DeviceObject` is explicitly unused. No persistent state is read or written except tracing/dump activity on exception.

## Dependencies And Integration Points
The handler is installed by `DriverEntry` and may also be resubmitted by `AFSSubmitLibraryRequest` if an IRP was queued while the library was unavailable. It depends on `AFSCompleteRequest`, `AFSExceptionFilter`, `AFSDbgTrace`, and `AFSDumpTraceFilesFnc` from the shared support layer.

## Risks And Test Signals
Because it always completes, callers expecting pass-through internal IOCTL behavior will fail at this shim. The unused `pIrpSp` assignment is harmless but signals that no control-code filtering exists. Test with an internal-device-control IRP against both control and redirector devices and verify completion status, no library in-flight accounting, and exception dump behavior if stack access faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSInternalDevControl.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSLibrarySupport.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSLibrarySupport.cpp

## Purpose
`AFSLibrarySupport.cpp` manages the loadable OpenAFS redirector library driver that performs most filesystem work. The fs shim owns library lifecycle, request queuing while the library is unavailable, in-flight request accounting while unloading, resubmission of queued IRPs, initial callback negotiation, and trace callback reconfiguration.

## Important APIs, Control Flow, And State
`AFSLoadLibrary` serializes on `LoadLibraryEvent`, stores the service registry path, calls `ZwLoadDriver`, opens `AFS_LIBRARY_CONTROL_DEVICE_NAME`, saves `LibraryFileObject` and `LibraryDeviceObject`, sets `AFS_LIBRARY_LOADED`, clears `AFS_LIBRARY_QUEUE_CANCELLED`, then drains queued IRPs with `AFSProcessQueuedResults(FALSE)`. On error it unloads/frees the stored service path.

`AFSUnloadLibrary` clears `AFS_LIBRARY_LOADED`, optionally marks `AFS_LIBRARY_QUEUE_CANCELLED`, waits until `InflightLibraryRequests` reaches zero using `InflightLibraryEvent`, cancels queued IRPs, dereferences the library file object, clears the library device object, unloads the driver, and frees `LibraryServicePath`.

`AFSCheckLibraryState` is the gate every pass-through dispatch uses. It rejects redirector shutdown, queues the IRP when the library is not loaded, or increments `InflightLibraryRequests` and clears the in-flight event when loaded. `AFSClearLibraryRequest` decrements that count and signals when zero. `AFSQueueLibraryRequest` appends an `AFSLibraryQueueRequestCB` and marks the IRP pending. `AFSProcessQueuedResults` either completes queued IRPs as cancelled or calls `AFSSubmitLibraryRequest`, whose switch dispatches the original IRP major function back into the correct fs handler.

`AFSInitializeLibrary` sends `IOCTL_AFS_INITIALIZE_LIBRARY_DEVICE` with device objects, server/mount names, debug flags, cache information, cache callbacks, and function pointers (`AFSProcessRequest`, `AFSDbgLogMsg`, `AFSAddConnectionEx`, pool wrappers, dump tracing, auth lookup). `AFSConfigLibraryDebug` pushes the current trace function pointer through `IOCTL_AFS_CONFIG_LIBRARY_TRACE`.

## Dependencies And Integration Points
This file is central to integration between the lightweight filesystem dispatch layer and the loadable library device. It depends on control-device extension state, event/resource synchronization, `ZwLoadDriver/ZwUnloadDriver`, `IoGetDeviceObjectPointer`, IRP completion/resubmission helpers, all major IRP handlers, the communication layer, network-provider list updates, cache manager callback state, and global trace settings.

## Risks And Test Signals
The in-flight count is safety-critical: every successful `AFSCheckLibraryState` must be balanced by `AFSClearLibraryRequest`, with `AFSWrite` taking two references because completion can outlive the caller. Queue cancellation races with redirector shutdown and library reload must not leak IRPs. `AFSProcessQueuedResults` resubmits through top-level handlers, so recursion and double-completion behavior need coverage. Test signals include library load failure, queued requests before load, unload while reads/writes are pending, queue cancellation, trace reconfiguration with/without a loaded library, and exact in-flight event behavior under concurrent dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSLibrarySupport.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSLockControl.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSLockControl.cpp

## Purpose
`AFSLockControl.cpp` implements the `IRP_MJ_LOCK_CONTROL` dispatch shim. Lock and unlock IRPs for redirector file objects are forwarded to the loaded library driver; control-device requests are rejected.

## Important APIs, Control Flow, And State
`AFSLockControl` rejects `AFSDeviceObject` with `STATUS_INVALID_DEVICE_REQUEST`, then calls `AFSCheckLibraryState`. If the library is absent, the IRP may be queued and returned as `STATUS_PENDING`; if the gate fails, the IRP is completed with the error. On success it calls `IoSkipCurrentIrpStackLocation`, forwards to `LibraryDeviceObject` with `IoCallDriver`, and immediately calls `AFSClearLibraryRequest` to release the unload guard for the caller's library submission.

## Dependencies And Integration Points
The implementation depends on `AFSLibrarySupport.cpp` for queueing and in-flight accounting, `AFSCompleteRequest` for local completion, and exception/dump tracing. The real byte-range lock semantics live in the library driver; this layer is a state gate and pass-through.

## Risks And Test Signals
The shim assumes the library owns completion after `IoCallDriver`; completing locally after forwarding would be wrong. Exception handling completes with the exception status, but only after dumping trace state. Tests should cover control-device rejection, absent-library queuing, normal pass-through to library, unload while lock IRPs are in flight, and lock/unlock failures propagated from the library.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSLockControl.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSLogSupport.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSLogSupport.cpp

## Purpose
`AFSLogSupport.cpp` implements the kernel trace ring buffer, runtime trace configuration, trace-buffer export, trace dump-file writing, and dump support buffer allocation for the fs layer. It provides `AFSDbgLogMsg`, the callback passed to the library driver.

## Important APIs, Control Flow, And State
`AFSDbgLogMsg` filters by `AFSTraceComponent` and `AFSTraceLevel`, serializes on `AFSDbgLogLock`, writes a monotonically numbered prefix into `AFSDbgBuffer`, wraps when space is low or formatting overflows, sets `AFS_DBG_LOG_WRAPPED`, and optionally mirrors to the debugger under `AFS_DBG_TRACE_TO_DEBUGGER`. `AFSInitializeDbgLog` allocates the nonpaged circular buffer when `AFSDbgBufferLength > 0`, installs `AFSDebugTraceFnc`, and tags the initial timestamp entry; `AFSTearDownDbgLog` frees it.

`AFSConfigureTrace` updates level, subsystem, debug flags, and buffer length, persists changes through `AFSUpdateRegistryParameter`, clamps buffer length to `AFS_DBG_LOG_MAXLENGTH`, reallocates the ring buffer, and calls `AFSConfigLibraryDebug` so the library sees the current callback. `AFSGetTraceConfig` reports globals; `AFSGetTraceBuffer` copies wrapped tail then head into a caller buffer. `AFSTagInitialLogEntry` records local time. `AFSDumpTraceFiles` opens `AFSDumpFileLocation`, serializes on `AFSDumpFileEvent`, creates a timestamped log file under that directory, and writes the current trace buffer using `AFSDumpBuffer`. `AFSInitializeDumpFile` allocates the dump filename buffer and a 64 KiB paged dump staging buffer.

## Dependencies And Integration Points
The file depends on resource locking wrappers, pool allocation wrappers, registry helpers, file I/O (`ZwCreateFile`, `ZwWriteFile`), local time conversion, global dump location set during redirector initialization, and the library-debug IOCTL path. It exports trace state to user/service IOCTL paths via `AFSGetTraceConfig` and `AFSGetTraceBuffer`.

## Risks And Test Signals
Trace formatting uses a `va_list` twice on overflow without restarting it, which is a portability/correctness risk. `AFSGetTraceBuffer` requires the caller length to be at least `AFSDbgBufferLength`, not just used length. Dumping reads `AFSDbgBuffer` without holding the lock across the full write, so dumps are best-effort snapshots. Tests should cover trace disabled/enabled, component and level filtering, wrap behavior, dynamic resize, registry persistence failures, library trace callback changes, dump path absence, concurrent dump serialization, and buffer export after wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSLogSupport.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSNetworkProviderSupport.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSNetworkProviderSupport.cpp

## Purpose
`AFSNetworkProviderSupport.cpp` maintains the redirector's provider enumeration list exposed to network-provider style queries. It inserts server/share/directory connection records and classifies them for Windows network resource enumeration.

## Important APIs, Control Flow, And State
`AFSAddConnectionEx` locks `ProviderListLock`, chooses the top-level provider list for server entries or the first server's child list for shares/directories, checks for duplicate `RemoteName` case-insensitively, strips a trailing slash in place, allocates an `AFSProviderConnectionCB` with inline remote-name storage, derives `ComponentName` by walking backward to the final path separator, calls `AFSInitializeConnectionInfo`, stores caller flags, and appends to either `ProviderEnumerationList` or the server's `EnumerationList`.

`AFSInitializeConnectionInfo` dissects the UNC-like name. Server-level entries are `RESOURCEDISPLAYTYPE_SERVER`, `RESOURCE_GLOBALNET`, and `RESOURCEUSAGE_CONTAINER` with comment `AFS Root`. Share-level entries are connectable disk shares, optionally attached if `LocalName` is set, with comment `AFS Share`. Deeper entries are connected directory resources with comment `AFS Directory`.

## Dependencies And Integration Points
The library receives `AFSAddConnectionEx` as a callback during `AFSInitializeLibrary`, so service/library discovery of cells/shares feeds this provider list. The data structure is stored in the RDR device extension and uses constants from `AFSDefines.h` mirroring Windows `NETRESOURCE` fields. It depends on `FsRtlDissectName`, pool wrappers, and the provider structures from shared headers.

## Risks And Test Signals
`AFSAddConnectionEx` mutates the caller's `RemoteName` buffer when removing a trailing slash, which is risky if the buffer is immutable or reused. Non-server insertions assume a single server at `ProviderEnumerationList`; multiple server support would need more precise parent selection. Comment buffers are allocated separately and are not freed here. Tests should cover duplicate insertions, trailing slash names, server before share ordering, share insertion without server, case-insensitive matching, component derivation, and cleanup by whatever tears down provider entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSNetworkProviderSupport.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSProcessSupport.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSProcessSupport.cpp

## Purpose
`AFSProcessSupport.cpp` tracks process creation/destruction and assigns OpenAFS authentication-group GUIDs to processes and threads. It bridges Windows process/session/SID information to the redirector's PAG/auth-group model and records whether the current process is the user-mode service.

## Important APIs, Control Flow, And State
`AFSProcessNotify` and `AFSProcessNotifyEx` adapt legacy and Vista+ process callbacks into `AFSProcessCreate` and `AFSProcessDestroy`. Creation locks `ProcessTree`, allocates an `AFSProcessCB` through `AFSInitializeProcessCB`, records creator process/thread IDs, then validates/assigns an auth group. Destruction removes the B-tree entry, frees per-process auth-group and thread lists, deletes the process resource, and frees the process CB.

`AFSValidateProcessEntry` is the core. It locates or creates the process entry, locks the parent and process CBs, records 64-bit state on 64-bit builds, obtains the caller SID and session ID, reuses an existing non-NoPAG auth group when possible, otherwise inherits from the creating parent thread or parent process, and finally hashes `(sessionId, SID hash)` into `AuthGroupTree`. If no SID entry exists it allocates an `AFSSIDEntryCB` and creates a GUID with `ExUuidCreate`. It stores the selected GUID in `ActiveAuthGroup`, marks local-system SIDs, and calls `AFSProcessSetProcessDacl` once per non-impersonating process to install the custom DACL ACE.

Support functions query 64-bit process state, initialize thread CBs, test whether a SID is the current token user or a group member, and set/query the static `AFSServicePid` through `AFSRegisterService`, `AFSDeregisterService`, and `AFSIsService`.

## Dependencies And Integration Points
This file depends on the process and auth-group B-trees in the control device extension, B-tree helpers, `AFSGetCallerSID`, `AFSGetSessionId`, `AFSIsLocalSystemSID`, `AFSIsNoPAGAuthGroup`, `AFSProcessSetProcessDacl`, resource wrappers, token APIs (`SeCaptureSubjectContext`, `SeQueryInformationToken`), and pool wrappers. The auth lookup callback `AFSRetrieveAuthGroup` in other files consumes these structures.

## Risks And Test Signals
Lock ordering across `ProcessTree`, parent process lock, process lock, and `AuthGroupTree` is delicate. The code calls `AFSProcessCreate` while holding or upgrading tree locks in some paths, so recursion/deadlock behavior needs review. Auth-group inheritance depends on creation thread IDs being captured accurately. SID/session hash collisions are possible in the combined key if SID hash collides. Tests should cover legacy and Ex callbacks, process destruction cleanup, impersonation vs non-impersonation paths, parent-thread and parent-process inheritance, local-system marking, DACL install failures, concurrent validation of the same process, 32-bit process detection on 64-bit OS, and service PID registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSProcessSupport.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSQuota.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSQuota.cpp

## Purpose
`AFSQuota.cpp` contains quota IRP handlers, but quota operations are not supported by this redirector shim. `IRP_MJ_QUERY_QUOTA` and `IRP_MJ_SET_QUOTA` are commented out in `DriverEntry`, and both handlers return `STATUS_NOT_SUPPORTED` if called.

## Important APIs, Control Flow, And State
`AFSQueryQuota` and `AFSSetQuota` retrieve the current IRP stack, log the file object at error level under `AFS_SUBSYSTEM_FILE_PROCESSING`, complete the IRP with `STATUS_NOT_SUPPORTED`, and return. Neither checks library state nor forwards to the library device. No quota state is kept in this file.

## Dependencies And Integration Points
The handlers are declared in `AFSCommon.h` and could be installed in the dispatch table, but current initialization leaves quota dispatch disabled. They depend only on `AFSCompleteRequest`, tracing, exception filtering, and dump support.

## Risks And Test Signals
The disabled dispatch table means these functions may be unreachable in normal operation, but direct invocation should still complete cleanly. Tests should verify quota IRPs receive unsupported behavior if enabled, do not alter library in-flight counts, and do not leak or double-complete under exception conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSQuota.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSRDRSupport.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSRDRSupport.cpp

## Purpose
`AFSRDRSupport.cpp` creates, registers, initializes, and tears down the redirector device. It also handles MUP path queries, service-provided redirector initialization, cache backing setup, root FCB creation/removal, and library initialization/closure.

## Important APIs, Control Flow, And State
`AFSInitRDRDevice` creates `AFSRDRDeviceObject`, initializes RDR tree/list locks and events, initializes the root FCB with `AFSInitRdrFcb`, clears `DO_DEVICE_INITIALIZING`, increments stack size, and registers as a UNC provider using `FsRtlRegisterUncProviderEx` when available or legacy `FsRtlRegisterUncProvider` plus `IoRegisterFileSystem`.

`AFSRDRDeviceControl` answers MUP `IOCTL_REDIR_QUERY_PATH` and `_EX` by accepting paths whose first component matches `AFSServerName`, returning `LengthAccepted`; other control codes fail with `STATUS_INVALID_DEVICE_REQUEST`.

`AFSInitializeRedirector` loads the library service, records cache block sizing, max RPC length, dump-file location, max direct I/O and dirty thresholds, dot-file/short-name/reparse/direct-service flags, and cache backing. Cache backing is either a service-provided memory mapping locked through an MDL or an opened cache file referenced by handle/object. It then stores path/link limits and calls `AFSInitializeLibrary` with the global file ID.

`AFSCloseRedirector` unloads the library and releases memory cache MDL, cache file handle/object/name, dump location, and root FCB. `AFSInitRdrFcb` allocates a paged `AFSFcb` plus nonpaged `AFSNonPagedFcb`, initializes FsRtl advanced header, main/paging resources, and atomically publishes it. `AFSRemoveRdrFcb` atomically removes and frees those resources.

## Dependencies And Integration Points
This file integrates the fs shim with MUP/UNC routing, the library lifecycle, cache manager callbacks, user-mode redirector initialization IOCTL structures, cache-file persistence, global tracing dump location, and shared FCB types from the wider OpenAFS redirector headers. It depends on `AFSLoadLibrary`, `AFSInitializeLibrary`, `AFSUnloadLibrary`, `AFSExAllocatePoolWithTag`, FsRtl, Zw file APIs, MDL page locking, and device extension layouts.

## Risks And Test Signals
Failure unwind has several subtle points: MDLs should be freed with the correct MDL routine, cache handle/object order must remain balanced, and `pDevExt = NULL` after FCB removal in the failure path can obscure later cleanup. The direct I/O minimum uses `5 * 1024 * 1204`, likely a typo for `1024 * 1024`. MUP query code trusts type-3 buffers and path lengths. Tests should cover UNC acceptance/rejection, registration on legacy and modern OS paths, memory-cache vs file-cache initialization, direct-service mode, dump location allocation, unload while initialized, duplicate root FCB publication, and injected failures at every cache setup stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSRDRSupport.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSRead.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSRead.cpp

## Purpose
`AFSRead.cpp` implements the `IRP_MJ_READ` dispatch shim. It validates that reads target the redirector device, gates them on library availability, and forwards accepted IRPs to the loaded library driver.

## Important APIs, Control Flow, And State
`AFSRead` rejects control-device reads with `STATUS_INVALID_DEVICE_REQUEST`. It then calls `AFSCheckLibraryState`; failure completes locally, `STATUS_PENDING` means the request has been queued, and success increments the library in-flight count. The routine skips the current stack location, calls `IoCallDriver` on `LibraryDeviceObject`, and balances the in-flight count with `AFSClearLibraryRequest`. Exception handling dumps traces and returns `STATUS_INSUFFICIENT_RESOURCES` without local completion in that exceptional path.

## Dependencies And Integration Points
The real read path is in the library driver; this shim depends on `AFSLibrarySupport.cpp` for gating and unload safety, the control device extension for `LibraryDeviceObject`, and common completion/exception/dump utilities.

## Risks And Test Signals
Read IRPs can be queued while the library is loading, so callers must handle `STATUS_PENDING`. Since no completion routine is installed, the unload guard only protects submission, not asynchronous completion; this is intentional for normal reads but differs from writes. Tests should cover control-device rejection, library absent queued reads, pass-through success/failure propagation, unload racing with read submission, and exception behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSRead.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSSecurity.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSSecurity.cpp

## Purpose
`AFSSecurity.cpp` implements security descriptor query/set dispatch. It rejects control-device and redirector-root FCB operations, then forwards valid file security IRPs to the library driver.

## Important APIs, Control Flow, And State
`AFSSetSecurity` and `AFSQuerySecurity` share the same flow: trace entry, reject `AFSDeviceObject`, fetch `AFSFcb` from `FileObject->FsContext`, reject missing FCB or `AFS_REDIRECTOR_FCB` root opens, call `AFSCheckLibraryState`, complete on gate failure unless queued, skip the current stack, forward to `LibraryDeviceObject`, and call `AFSClearLibraryRequest`.

## Dependencies And Integration Points
The handlers depend on FCB node type definitions from shared redirector structures, library gating, common completion, and exception/dump support. Actual ACL/security descriptor semantics are delegated to the library driver.

## Risks And Test Signals
The code assumes `FileObject` and `FsContext` are valid when non-control device security IRPs arrive; malformed IRPs can fault into the exception path. Root opens are intentionally denied, so behavior must align with Windows expectations for network root security queries. Tests should cover root FCB rejection, null FsContext rejection, query and set forwarding, queued behavior during library load, and propagation of library security failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSSecurity.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSShutdown.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSShutdown.cpp

## Purpose
`AFSShutdown.cpp` handles `IRP_MJ_SHUTDOWN` and records clean shutdown state for configurations that require it. The actual filesystem shutdown hook is currently a no-op.

## Important APIs, Control Flow, And State
`AFSShutdown` retrieves the IRP stack, and if `AFS_DBG_REQUIRE_CLEAN_SHUTDOWN` is set in `AFSDebugFlags`, writes `AFS_REG_SHUTDOWN_STATUS` as `1` through `AFSUpdateRegistryParameter`. It calls `AFSShutdownFilesystem`, normalizes any failure back to success, completes the IRP, and returns success. `AFSShutdownFilesystem` currently just returns `STATUS_SUCCESS`.

## Dependencies And Integration Points
This file participates in the clean-shutdown contract enforced by `DriverEntry`, which rejects load if clean shutdown was required and the registry did not show a clean value. It depends on registry update helpers, tracing, exception filtering, dump support, and `AFSCompleteRequest`.

## Risks And Test Signals
Because `AFSShutdownFilesystem` is empty and failures are suppressed, shutdown persistence relies almost entirely on the registry marker. Tests should verify the shutdown marker transitions from dirty at load to clean at shutdown, behavior when registry writes fail, completion of shutdown IRPs, and that unload/redirector closure paths elsewhere handle real resource cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSShutdown.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSSystemControl.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSSystemControl.cpp

## Purpose
`AFSSystemControl.cpp` implements `IRP_MJ_SYSTEM_CONTROL` as an unsupported/stub WMI system-control handler. It logs and completes requests locally with `STATUS_NOT_IMPLEMENTED`.

## Important APIs, Control Flow, And State
`AFSSystemControl` ignores the device object, obtains the IRP stack, traces the file object at warning level, completes via `AFSCompleteRequest`, and returns `STATUS_NOT_IMPLEMENTED`. No library forwarding, persistent state updates, or in-flight accounting occur.

## Dependencies And Integration Points
The handler is installed in `DriverEntry` and can also be selected by `AFSSubmitLibraryRequest` for queued system-control IRPs. It depends on the shared trace, completion, exception-filter, and dump helpers.

## Risks And Test Signals
Any WMI/system-control integration is unavailable through this driver. Test by issuing system-control IRPs and confirming local completion, no call into the library, stable logging, and no double completion under exception handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSSystemControl.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSVolumeInfo.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSVolumeInfo.cpp

## Purpose
`AFSVolumeInfo.cpp` handles volume-information IRPs. Query requests are forwarded to the library driver; set requests are rejected as invalid.

## Important APIs, Control Flow, And State
`AFSQueryVolumeInfo` rejects control-device requests, gates on `AFSCheckLibraryState`, completes on errors unless queued, skips the current stack location, forwards to `LibraryDeviceObject`, and clears the in-flight guard. `AFSSetVolumeInfo` logs the file object and completes with `STATUS_INVALID_DEVICE_REQUEST` without forwarding. No local volume metadata is maintained.

## Dependencies And Integration Points
Volume query answers come from the library driver. This file depends on library state management, common completion/exception support, and the control device extension's `LibraryDeviceObject`.

## Risks And Test Signals
Set-volume operations always fail, so callers attempting label or filesystem metadata changes should receive a consistent invalid-device response. Query behavior depends on library readiness and can pend through the queue. Tests should cover query pass-through, set rejection, absent-library queuing, control-device rejection, and library failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSVolumeInfo.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSWrite.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSWrite.cpp

## Purpose
`AFSWrite.cpp` implements the write dispatch path and its completion routine. Unlike most pass-through shims, writes take a second library in-flight reference so the library cannot unload while an asynchronously completed write IRP is still outstanding.

## Important APIs, Control Flow, And State
`AFSWrite` rejects control-device writes, calls `AFSCheckLibraryState` once to guard the caller's submission, then calls it a second time to guard the lifetime of the IRP/completion pair. If the second check fails, it clears the first reference and completes or returns pending as appropriate. On success it copies the stack to the next location, installs `AFSWriteComplete` for success/error/cancel, calls the library device with `IoCallDriver`, and clears the caller's reference.

`AFSWriteComplete` clears the IRP lifetime reference with `AFSClearLibraryRequest`, preserves pending state with `IoMarkIrpPending` when `PendingReturned` is set, traces completion, and returns `STATUS_CONTINUE_COMPLETION`.

## Dependencies And Integration Points
The file depends on library unload accounting from `AFSLibrarySupport.cpp`, common completion, trace and dump helpers, and the control device extension. Actual write caching, service I/O, and file mutation semantics live in the library driver.

## Risks And Test Signals
Balancing the two in-flight references is critical; leaks block unload, undercounts permit unload during completion. Exception handling after references are taken could leave imbalance if not carefully tested. Test signals include control-device rejection, library absent on first and second checks, synchronous and pending writes, cancellation/error completion, unload waiting for write completion, and correct `PendingReturned` propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSWrite.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/Include/AFSCommon.h -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/Include/AFSCommon.h

## Purpose
`AFSCommon.h` is the central public header for the fs-layer compilation unit. It brings Windows kernel headers and OpenAFS shared user/redirector headers into an `extern "C"` block, includes local defines/structs/externs, and declares the cross-file API surface used by all fs modules.

## Important APIs, Control Flow, And State
The header declares driver entry/unload, auth-group APIs, B-tree helpers, communication request APIs, every major IRP dispatch handler, generic resource/completion/registry/device helpers, Fast I/O callbacks, library lifecycle APIs, RDR device APIs, trace/dump APIs, and process tracking APIs. It also declares `ZwQueryInformationProcess`, sets `AFS_KERNEL_MODE`, pulls in `ntifs.h`, `wdmsec.h`, `initguid.h`, `ntstrsafe.h`, and conditionally includes `AFSExtern.h` unless `NO_EXTERN` is defined.

## Dependencies And Integration Points
This header is the glue between the fs shim, the loadable library, shared redirector structures, user IOCTL contracts, provider contracts, and generic utility modules. It exposes the same dispatch handlers installed by `DriverEntry` and resubmitted by `AFSSubmitLibraryRequest`.

## Risks And Test Signals
Because it is broad, prototype drift between this header and implementations can break many files. Duplicate `AFSSetVolumeInfo` declaration is benign but untidy. Include order matters because `AFSDefines.h` defines GUIDs under `initguid.h`. Build tests should compile all fs modules with and without `NO_EXTERN`, verify C linkage, and catch signature mismatches across dispatch, library callback, and Fast I/O APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/Include/AFSCommon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/Include/AFSDefines.h -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/Include/AFSDefines.h

## Purpose
`AFSDefines.h` centralizes fs-layer constants, flags, registry value names, device names, network-provider constants, extent geometry, GUIDs, and the `PAFSSetInformationToken` function pointer type.

## Important APIs, Control Flow, And State
Registry defines cover debug flags, trace level/subsystem/buffer size, max dirty/direct I/O, NetBIOS and mount-root names, shutdown status, and clean-shutdown requirement. Device defines name the control device and symbolic link. Flag macros wrap bit tests and interlocked set/clear operations. Timing/cache constants define one-second units, server flush/purge delays, read-ahead granularity, directory enumeration buffer size, and write-to-EOF detection.

The header defines directory CCB/entry flags, network-provider `WN_*`, `RESOURCE*`, `RESOURCETYPE*`, `RESOURCEUSAGE*`, and `RESOURCEDISPLAYTYPE*` constants, instance identifiers, extent skip-list geometry, maximum extent release count, control-device security GUID, debug ring maximum/wrap flag, connection/process/auth-group flags, special share count, OpenAFS DFS reparse tag/GUID, directory enumeration sentinel indexes, library state flags, custom DACL SID GUID and length, and `PAFSSetInformationToken`.

## Dependencies And Integration Points
The constants are consumed across initialization, logging, process/auth, provider enumeration, extent/cache management, directory enumeration, library lifecycle, and security DACL code. GUID definitions rely on `initguid.h` inclusion from `AFSCommon.h`.

## Risks And Test Signals
Interlocked flag macros assume lvalue widths compatible with `InterlockedOr/And`. `QuadAlign` casts through `ULONG`, which is unsafe for 64-bit pointer-sized values if used on pointers. Constants duplicated from Windows networking headers can drift. Tests should include 32/64-bit builds, static analysis for pointer truncation, trace buffer clamping, library flag transitions, provider enumeration values, and reparse tag/GUID correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/Include/AFSDefines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/Include/AFSExtern.h -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/Include/AFSExtern.h

## Purpose
`AFSExtern.h` declares the fs-layer global variables defined elsewhere, primarily in `AFSData.cpp`. It lets all modules share driver/device objects, configuration, tracing state, server names, auth-group identifiers, callback pointers, and dump buffers.

## Important APIs, Control Flow, And State
The globals include `AFSDriverObject`, `AFSDeviceObject`, `AFSRDRDeviceObject`, `AFSFastIoDispatch`, `AFSRegistryPath`, debug/trace flags, max I/O/dirty settings, `AFSSysProcess`, `AFSMUPHandle`, server/mount/global-root names, `AFSDbgLogLock`, debug ring pointers/length/counter/flags, dump-file location/name/event/buffer, cache-manager callbacks, auth-group flags and GUIDs, `AFSSetInformationToken`, and `AFSDebugTraceFnc`.

## Dependencies And Integration Points
Every implementation in this subset reads or writes some of these globals. `DriverEntry` initializes many of them, `AFSLogSupport.cpp` owns debug/dump state, `AFSRDRSupport.cpp` owns RDR device/cache-related use, `AFSLibrarySupport.cpp` passes callbacks and names to the library, and `AFSProcessSupport.cpp` consumes auth/process globals.

## Risks And Test Signals
Global state makes initialization order and teardown order critical. Many pointers are nullable during early failure or shutdown; callers must guard accordingly. Tests should exercise partial initialization failure, repeated load/unload, trace reconfiguration, redirector close, and static analysis for globals accessed without locks where concurrency matters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/Include/AFSExtern.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/Include/AFSStructs.h -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/Include/AFSStructs.h

## Purpose
`AFSStructs.h` defines small fs-layer control structures used by library request queuing, process/auth-group tracking, DACL update work, and legacy service-table lookup.

## Important APIs, Control Flow, And State
`AFSLibraryQueueRequestCB` is a singly linked queued-IRP node used while the library is unloaded. `AFSProcessCB` is a process-tree B-tree entry keyed by process ID and contains a resource lock, flags, parent/creator process and thread IDs, active auth-group pointer, process auth-group list, and thread list. `AFSThreadCB` links thread-specific auth-group state by thread ID. `AFSSIDEntryCB` is an auth-group B-tree entry keyed by `(sessionId, SID hash)` and stores a generated GUID. `AFSProcessAuthGroupCB` stores per-process auth group list entries. `AFSSetDaclRequestCB` carries a process pointer, completion status, and event for DACL update work. `AFSSrvcTableEntry` describes the legacy system service table layout used by XP fallback code in `DriverEntry`.

## Dependencies And Integration Points
`AFSLibrarySupport.cpp` allocates and drains `AFSLibraryQueueRequestCB`. `AFSProcessSupport.cpp` allocates and frees process, thread, SID, and process-auth-group CBs. Generic B-tree helpers operate on the embedded `AFSBTreeEntry`. The service-table struct is only relevant to 32-bit XP routine lookup.

## Risks And Test Signals
Several structs store raw `GUID *` pointers rather than owned GUID values; lifetime depends on SID entries, global NoPAG GUID, or process auth lists remaining valid. Linked lists are manually freed at process destruction. Tests should cover process teardown with thread/auth lists, auth-group pointer lifetime, queued IRP node cleanup on cancel and resubmit, and 32-bit legacy build compatibility for `AFSSrvcTableEntry`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/Include/AFSStructs.h -->
