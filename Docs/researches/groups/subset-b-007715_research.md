# subset-b-007715 research

This grouped report covers the OpenAFS Windows redirector kernel `fs` source files assigned to subset-b-007715. Each section is wrapped with reconciliation markers for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSAuthGroupSupport.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSAuthGroupSupport.cpp

Purpose: implements process authentication group (PAG/AuthGroup) lookup, creation, activation, reset, and SID/session-to-GUID mapping for the Windows OpenAFS redirector. It bridges Windows process/thread identity, token SIDs, logon sessions, thread DACL-encoded GUIDs, and the redirector service's request AuthGroup field.

Important APIs/types/functions: `AFSRetrieveAuthGroup()` resolves an AuthGroup from the thread DACL, thread active group, process active group, or process validation fallback. `AFSIsLocalSystemAuthGroup()`, `AFSIsLocalSystemSID()`, and `AFSIsNoPAGAuthGroup()` classify special identities. `AFSCreateSetProcessAuthGroup()` allocates per-process `AFSProcessAuthGroupCB` entries and optionally activates them on the current process or thread. `AFSQueryProcessAuthGroupList()` enumerates GUIDs for the current process. `AFSSetActiveProcessAuthGroup()` and `AFSResetActiveProcessAuthGroup()` set or clear active process/thread AuthGroups. `AFSCreateAuthGroupForSIDorLogonSession()` maintains the global SID/session AuthGroup tree. `AFSQueryAuthGroup()` returns the GUID for a SID/session pair.

Control flow: most process-scoped operations locate the current `AFSProcessCB` in `Specific.Control.ProcessTree` under the tree lock, then take `pProcessCB->Lock` for list/thread mutations. SID-based global mapping hashes `SID + SessionId` into a 64-bit key and uses `Specific.Control.AuthGroupTree`. `AFSRetrieveAuthGroup()` first trusts an impersonation-token default-DACL ACE inserted by `AFSProcessSetProcessDacl()`, then checks explicit thread/process active state, then falls back to `AFSValidateProcessEntry()`.

State/persistence: state is in nonpaged process control blocks, per-process AuthGroup linked lists, per-thread active pointers, global `AFSNoPAGAuthGroup`, and the auth-group B-tree. AuthGroups are GUIDs produced by `ExUuidCreate()`. No on-disk persistence occurs here; identity state lives until process/auth tree teardown or reset. The DACL path stores an AuthGroup marker in the process token default DACL, making AuthGroup propagation visible through token state.

Dependencies/integration: depends on `AFSBTreeSupport.cpp` for tree lookup/insert, `AFSGeneric.cpp` helpers for caller SID/session and DACL updates, `AFSCommon.h` structures, Windows token APIs, `RtlHashUnicodeString`, `RtlStringFromGUID`, ERESOURCE locks, and IOCTL dispatch in `AFSCommSupport.cpp`. `AFSProcessRequest()` calls `AFSRetrieveAuthGroup()` when building service requests.

Risks: lock ordering between tree locks and process locks must remain consistent. Pointers such as `ActiveAuthGroup` refer into linked-list entries, so freeing or replacing list nodes would invalidate active state. Hashing SID/session into a 64-bit table key assumes hash collisions are acceptable or rare; there is no secondary SID compare in the tree entry. DACL parsing assumes the ACE layout and `AFS_DACL_SID_LENGTH` are exact. Permission checks intentionally allow LocalSystem to create groups for other SIDs/sessions, so regression tests need to protect that boundary.

Test signals: exercise normal caller SID/session creation, LocalSystem delegated logon-session creation, rejected non-LocalSystem delegated SID/session requests, process versus thread activation/reset, NoPAG fallback, thread-DACL retrieval, buffer-overflow sizing for `AFSQueryProcessAuthGroupList()`, and concurrent process/tree mutation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSAuthGroupSupport.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSBTreeSupport.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSBTreeSupport.cpp

Purpose: provides a small binary-search-tree utility for `AFSBTreeEntry` nodes keyed by `HashIndex`. It is used by control-device state such as process and AuthGroup lookup tables.

Important APIs/types/functions: `AFSLocateHashEntry()` walks left/right links to find a hash key and returns the located entry through an output pointer. `AFSInsertHashEntry()` inserts a new node below an existing top node and sets its parent link. `AFSRemoveHashEntry()` detaches a node, reconnects right and left subtrees, updates the top node if necessary, and clears the removed node links.

Control flow: lookup compares the target hash with the current node, descending right for larger hashes and left for smaller hashes. Insert repeats the same descent and attaches at the first missing child link; equal hashes trigger a warning, assertion, and failure. Remove handles leaf removal, right-subtree replacement, left-subtree reattachment to the leftmost node of the right subtree, or left-subtree promotion when no right child exists.

State/persistence: mutates only caller-owned in-memory tree pointers (`leftLink`, `rightLink`, `parentLink`, `HashIndex`). It does no allocation, freeing, or locking; callers own lifetime and synchronization.

Dependencies/integration: included through `AFSCommon.h`. Auth/process management uses these helpers with ERESOURCE locks around `ProcessTree` and `AuthGroupTree`.

Risks: the tree is unbalanced, so sorted or adversarial hash insertion can degrade lookup/insert/remove to linear time. Duplicate hash handling asserts and returns unsuccessful without collision chaining. `AFSLocateHashEntry()` returns `STATUS_SUCCESS` even when a non-null tree does not contain the key, leaving callers to check the output pointer. Remove assumes the node is actually in the supplied tree and that parent/child links are coherent.

Test signals: cover empty lookup, missing lookup with unchanged output pointer, duplicate insert, root/leaf/one-child/two-child removals, parent-link correctness after removal, and long ordered insertion sequences to observe performance and stack-free iterative behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSBTreeSupport.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSCleanup.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSCleanup.cpp

Purpose: handles `IRP_MJ_CLEANUP` for both the control device and redirector device path. It tears down service/redirector instances opened on the control device and forwards real file cleanup requests to the library device.

Important APIs/types/functions: `AFSCleanup()` is the top-level dispatch handler. It detects `AFS_CONTROL_INSTANCE` to call `AFSCleanupIrpPool()` and `AFSDeregisterService()`, detects `AFS_REDIRECTOR_INSTANCE` to call `AFSCloseRedirector()`, and otherwise delegates to `AFSCommonCleanup()`. `AFSCommonCleanup()` validates the FCB and library state, forwards the IRP to `LibraryDeviceObject`, and marks `FO_CLEANUP_COMPLETE` if completing locally.

Control flow: control-device cleanup is completed immediately after instance-specific cleanup. Redirector file cleanup skips root opens and redirector FCBs, then calls `AFSCheckLibraryState()`. If the library returns pending, the IRP remains owned by the library path. Otherwise the stack is skipped, the request is called into the library, and `AFSClearLibraryRequest()` is invoked.

State/persistence: may shut down the communication IRP pool and service registration, close redirector state, and set `FO_CLEANUP_COMPLETE` on local completion. No durable persistence.

Dependencies/integration: uses control flags stored in `FileObject->FsContext`, global `AFSDeviceObject`, `AFSDeviceExt`, library-device forwarding, `AFSCommSupport.cpp` pool cleanup, and exception/trace helpers.

Risks: correctness depends on `FsContext` being either a flag-bearing control instance or an `AFSFcb` depending on device object. Pending library-state handling must avoid double completion. Cleanup closes service resources, so stale control handles can affect all queued service requests.

Test signals: control-device handle cleanup after initialization, redirector instance cleanup, root-open cleanup, library unavailable/pending/successful forwarding, and FO flag setting only for locally completed file cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSCleanup.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSClose.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSClose.cpp

Purpose: handles `IRP_MJ_CLOSE`. Control-device closes complete immediately; redirector file closes are forwarded to the user-mode/library device when appropriate.

Important APIs/types/functions: `AFSClose()` dispatches by device object. `AFSCommonClose()` extracts the FCB, rejects root/redirector FCB closes as local success, calls `AFSCheckLibraryState()`, forwards to `LibraryDeviceObject`, and clears the library request marker.

Control flow: if `DeviceObject == AFSDeviceObject`, the IRP is completed as success. Otherwise the close path checks the FCB from `FileObject->FsContext`; root opens complete locally, regular objects are gated on library state, and non-pending success is transferred with `IoSkipCurrentIrpStackLocation()`/`IoCallDriver()`.

State/persistence: no file state is modified here beyond completion/forwarding. The library path owns any actual close-side teardown of cached file state.

Dependencies/integration: depends on `AFSCommon.h`, `AFSDeviceObject`, `AFSCheckLibraryState()`, `AFSClearLibraryRequest()`, and the library device object in the control extension.

Risks: double completion if library-state pending handling is changed incorrectly. Root/redirector FCB identification depends on valid `NodeTypeCode`. The local `pDeviceExt` assignment is unused except for retrieving the extension and can hide stale assumptions.

Test signals: control close, root close, regular close with library unavailable, pending library queue, successful library forwarding, and exception-path status behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSClose.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSCommSupport.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSCommSupport.cpp

Purpose: implements the kernel/control-device communication channel used to pass redirector work to the OpenAFS service/library and receive results. It also validates and dispatches control IOCTLs for service initialization, redirector initialization, auth-group operations, tracing, shutdown, cache invalidation, and library passthrough.

Important APIs/types/functions: `AFSReleaseFid()` wraps a release-FID service request. `AFSProcessRequest()` builds `AFSPoolEntry` requests, attaches file/name/data/AuthGroup metadata, queues them, and optionally waits synchronously for completion. `AFSCheckIoctlPermissions()` centralizes IOCTL access control. `AFSProcessControlRequest()` is the control-device IOCTL switch. `AFSInitIrpPool()` activates service queues. `AFSCleanupIrpPool()` cancels queued and result-pool requests. `AFSInsertRequest()` appends to the request queue and signals worker events. `AFSProcessIrpRequest()` lets the user service dequeue work. `AFSProcessIrpResult()` matches synchronous results by request index and wakes the original kernel waiter.

Control flow: kernel callers enqueue work under `CommServiceCB.IrpPoolLock`; synchronous requests use a stack `AFSPoolEntry` with an event and move into `ResultPool` until the service posts a result. Asynchronous requests allocate a standalone pool entry and are freed after the service dequeues them. Service worker threads issue `IOCTL_AFS_PROCESS_IRP_REQUEST` and block on normal or release-only events; release-only workers only drain `AFS_REQUEST_TYPE_RELEASE_FILE_EXTENTS` to avoid extent deadlock. Results enter through `IOCTL_AFS_PROCESS_IRP_RESULT`, search `ResultPool`, copy result data to the waiting caller's buffer, unmap file IO buffers if needed, and signal the event.

State/persistence: queue state is in `AFSCommSrvcCB`: request/result list heads/tails, request index, queue count, pool-control flag, worker events, and service process pointer. `AFSProcessRequest()` increments `OutstandingServiceRequestCount` and updates an event used by shutdown. The module also sets per-handle `FsContext` flags for initialized control/redirector instances. No durable storage, but registry/debug and redirector IOCTLs can affect broader persistent state through called helpers.

Dependencies/integration: integrates with `AFSAuthGroupSupport.cpp` for request AuthGroup resolution, `AFSGeneric.cpp` for shutdown/sysname/reparse helpers and allocation wrappers, redirector/library initialization, trace configuration, service registration checks, group/SID checks (`AFSIsService`, `AFSIsUser`, `AFSIsInGroup`), MDL mapping APIs, and standard Windows IRP/IOCTL machinery.

Risks: synchronous requests can block indefinitely because `KeWaitForSingleObject()` uses no timeout. Queue lock ordering must remain IRP-pool before result-pool. User-output buffer sizing relies heavily on asserts in `AFSProcessIrpRequest()`, so checked and free builds may differ if the service supplies a too-small buffer. IOCTL permission policy is security-critical and new IOCTLs must be added to both permission and dispatch logic. Cleanup cancellation must not free stack-backed synchronous entries; this code signals them instead.

Test signals: service initialization and duplicate initialization, permission rejection for non-service/non-admin IOCTLs, normal and release-only worker dequeue, synchronous result matching and buffer truncation, shutdown/cancel while requests are pending, mapped file IO buffer unmap paths, WOW64 flagging, AuthGroup propagation, and library passthrough fallback in the default IOCTL branch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSCommSupport.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSCreate.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSCreate.cpp

Purpose: handles `IRP_MJ_CREATE` for the control device and redirector. It opens the control device, opens the redirector root, or forwards real file creates to the library.

Important APIs/types/functions: `AFSCreate()` chooses control versus redirector handling. `AFSCommonCreate()` validates the current process AuthGroup, treats null filename/root opens as redirector opens, checks library state, and forwards create IRPs. `AFSControlDeviceCreate()` completes control opens with `FILE_OPENED`. `AFSOpenRedirector()` assigns the redirector FCB to `FileObject->FsContext` and returns opened status.

Control flow: control-device creates complete locally. Redirector creates first call `AFSValidateProcessEntry()` for current process AuthGroup tracing. If the file object or name buffer is null, it opens the redirector root locally; otherwise it forwards through `LibraryDeviceObject` after `AFSCheckLibraryState()`.

State/persistence: root opens store `pDeviceExt->Fcb` in the file object's `FsContext`. Process validation may populate process/auth tracking outside this file. No durable persistence.

Dependencies/integration: depends on AuthGroup validation in the control process tree, `AFSDeviceObject`, `AFSRDRDeviceObject`, library-device state, `RtlStringFromGUID()`, and common completion/exception tracing.

Risks: create-time process validation side effects are security-sensitive. Null filename is interpreted as a volume/root open. Pending library state must not complete the IRP locally. Root-open `FsContext` must remain valid through cleanup/close paths.

Test signals: control open, root/volume open, regular file create forwarding, process AuthGroup located/not located, library unavailable and pending states, and exception status translation to `STATUS_ACCESS_DENIED`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSCreate.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSData.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSData.cpp

Purpose: defines global storage for the Windows OpenAFS redirector kernel module. The `NO_EXTERN` include pattern makes this translation unit own the globals declared elsewhere.

Important APIs/types/functions: globals include `AFSDriverObject`, `AFSDeviceObject`, `AFSRDRDeviceObject`, `AFSFastIoDispatch`, `AFSRegistryPath`, debug/trace flags, server/share names, cache-manager callbacks, max direct/dirty IO settings, debug-log buffers/events, dump trace state, `AFSAuthGroupFlags`, `AFSActiveAuthGroup`, `AFSNoPAGAuthGroup`, `AFSSetInformationToken`, and `AFSDebugTraceFnc`.

Control flow: no executable control flow beyond static initialization. Other modules read/write these globals during driver initialization, dispatch, tracing, memory handling, auth, and shutdown.

State/persistence: all state is process/kernel global and initialized to null/zero or default function pointers. Registry-reading code in `AFSGeneric.cpp` later populates debug and size settings. No direct persistence here.

Dependencies/integration: included by all `AFSCommon.h` consumers through extern declarations. It anchors shared device object pointers, fast I/O dispatch table, cache manager callbacks, and AuthGroup globals used across this subset.

Risks: globals create broad implicit coupling and initialization-order hazards. Incorrect default values can disable tracing, break device dispatch, or make special AuthGroup comparisons invalid. The exported C linkage block means name/linkage assumptions matter.

Test signals: driver initialization should verify all global pointers/strings/callbacks are populated before dispatch use; shutdown should leave no dangling dump/debug buffers; AuthGroup code needs initialized NoPAG/active GUIDs before requests are processed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSData.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSDevControl.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSDevControl.cpp

Purpose: top-level `IRP_MJ_DEVICE_CONTROL` dispatch entry. It routes control-device IOCTLs to kernel control handling and redirector-device IOCTLs to redirector handling.

Important APIs/types/functions: `AFSDevControl()` extracts the current stack location, calls `AFSProcessControlRequest()` for `AFSDeviceObject`, otherwise calls `AFSRDRDeviceControl()`.

Control flow: the device object determines the target namespace. Exceptions are trapped by `AFSExceptionFilter()` with trace dumping.

State/persistence: no local state mutation beyond whatever the delegated IOCTL handler does. Control-device IOCTLs may initialize pools, services, redirector state, tracing, AuthGroups, and shutdown.

Dependencies/integration: depends on `AFSCommSupport.cpp` for control IOCTL dispatch and the redirector implementation for `AFSRDRDeviceControl()`.

Risks: a wrong device-object comparison can expose control IOCTLs to redirector handles or vice versa. The local `pIrpSp` is currently unused after assignment, so future edits should avoid assuming validation happened here.

Test signals: issue representative IOCTLs against control and redirector device objects, verify unsupported/misrouted requests are rejected in delegated layers, and exercise exception tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSDevControl.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSDirControl.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSDirControl.cpp

Purpose: handles `IRP_MJ_DIRECTORY_CONTROL` and forwards directory enumeration/change-notification work to the library device for redirector file objects.

Important APIs/types/functions: `AFSDirControl()` rejects the control device with `STATUS_INVALID_DEVICE_REQUEST`, gates redirector requests through `AFSCheckLibraryState()`, forwards with `IoCallDriver()`, and calls `AFSClearLibraryRequest()`.

Control flow: control-device requests complete locally as invalid. Redirector requests follow the common library-forwarding pattern: check state, complete locally on non-pending failure, leave pending alone, or skip the stack and call the library device.

State/persistence: no local persistent state. Directory state is owned by the library/redirector path.

Dependencies/integration: uses the control device extension's `LibraryDeviceObject`, shared completion and exception helpers, and the library request-state protocol.

Risks: pending library-state handling is the main correctness hazard. Directory control can be frequent and buffer-sensitive; this wrapper assumes the library validates detailed query parameters.

Test signals: control-device rejection, successful forwarding of query directory and notify change requests, library unavailable, pending queue behavior, and no local completion after `IoCallDriver()` ownership transfer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSDirControl.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSEa.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSEa.cpp

Purpose: handles extended attribute query and set IRPs. The control device returns EA-not-supported immediately, while redirector objects are forwarded to the library if available.

Important APIs/types/functions: `AFSQueryEA()` handles `IRP_MJ_QUERY_EA`. `AFSSetEA()` handles `IRP_MJ_SET_EA`. Both default to `STATUS_EAS_NOT_SUPPORTED`, reject `AFSDeviceObject`, call `AFSCheckLibraryState()`, and forward to the library device on success.

Control flow: both functions share the same pattern: local invalid/not-supported completion for control device, library-state gate, then `IoSkipCurrentIrpStackLocation()` and `IoCallDriver()` for redirector objects.

State/persistence: no local state or EA persistence. Any actual EA behavior is delegated to the library.

Dependencies/integration: depends on shared control extension, `LibraryDeviceObject`, `AFSCheckLibraryState()`, and `AFSClearLibraryRequest()`.

Risks: the initial status communicates unsupported EAs for control-device requests, but redirector objects can still be library-handled; callers must not infer global EA absence from this wrapper alone. Pending and error completion rules mirror other wrappers and must stay consistent.

Test signals: query/set EA on control device, query/set EA on redirector when library ready/unavailable/pending, and exception path trace dump.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSEa.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSFSControl.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSFSControl.cpp

Purpose: handles filesystem-control IRPs (`IRP_MJ_FILE_SYSTEM_CONTROL`) for the redirector by rejecting the control device and forwarding valid redirector requests to the library.

Important APIs/types/functions: `AFSFSControl()` checks for `AFSDeviceObject`, returns `STATUS_INVALID_DEVICE_REQUEST` for control requests, gates on `AFSCheckLibraryState()`, forwards via `IoCallDriver()`, and clears the library request marker.

Control flow: this is a standard dispatch wrapper. It completes local failures and transfers ownership to the library on success.

State/persistence: no local persistent state. Filesystem-control operations may affect mount/volume state in the library.

Dependencies/integration: uses `AFSDeviceObject`, the control extension's `LibraryDeviceObject`, `AFSCompleteRequest()`, and exception tracing.

Risks: FSCTLs are broad and security-sensitive; detailed validation is delegated. The wrapper must not complete IRPs after library ownership transfer or while pending in `AFSCheckLibraryState()`.

Test signals: control-device FSCTL rejection, forwarding of mount/volume FSCTLs, library-state pending/failure behavior, and completion status propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSFSControl.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSFastIoSupport.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSFastIoSupport.cpp

Purpose: supplies the driver fast-I/O callback routines and cache-manager locking callbacks. Most data fast paths deliberately return `FALSE`, forcing normal IRP processing, while acquire/release callbacks coordinate FCB, paging, and section-object resources.

Important APIs/types/functions: `AFSFastIoCheckIfPossible()`, read/write/info/lock/unlock/devctl/network-open/MDL/compressed/query-open callbacks return `FALSE`. `AFSFastIoAcquireFile()` takes FCB and section-object resources exclusively and references the section-create file object. `AFSFastIoReleaseFile()` releases those resources and dereferences saved file objects. `AFSFastIoAcquireForCCFlush()` and `AFSFastIoReleaseForCCFlush()` coordinate paging and section-object locks for cache flush. Cache-manager callback analogs in `AFSGeneric.cpp` handle lazy write and read ahead.

Control flow: direct fast-I/O callbacks are stubs that decline the fast path. Acquire callbacks assume `FileObject->FsContext` is an `AFSFcb`, acquire resources with `AFSAcquire*()`, set `FSRTL_CACHE_TOP_LEVEL_IRP` when needed, and release in reverse-like order. `AFSFastIoAcquireFile()` stores `SectionCreateFO` only if not already set and references it until release.

State/persistence: mutates in-memory FCB resources and `Specific.File.SectionCreateFO`. It also manipulates the thread's top-level IRP marker for cache-manager recursion control. No durable persistence.

Dependencies/integration: relies on FCB/NPFcb structures from `AFSCommon.h`, resource wrappers in `AFSGeneric.cpp`, Cache Manager (`CcGetFileObjectFromSectionPtrs`), object reference APIs, and the `FAST_IO_DISPATCH` table declared in `AFSData.cpp`.

Risks: fast I/O stub returns protect correctness by avoiding unsupported direct paths, but they can cost performance. Acquire/release imbalance can deadlock cache manager paths. `AFSFastIoAcquireForCCFlush()` checks `SectionObjectResource` shared state and then acquires exclusive or shared, so resource recursion/ownership semantics matter. `FileObject->FsContext` must be a valid file FCB, not a redirector root/control flag.

Test signals: verify every unsupported fast callback returns `FALSE`; stress cache flush/lazy-write/read-ahead with concurrent close/cleanup; validate no leaked `SectionCreateFO` references; assert top-level IRP is set and cleared; run Driver Verifier-style resource tracking for acquire/release symmetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSFastIoSupport.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSFileInfo.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSFileInfo.cpp

Purpose: handles file information query and set IRPs by rejecting control/root opens and forwarding regular redirector file-object operations to the library.

Important APIs/types/functions: `AFSQueryFileInfo()` handles query information. `AFSSetFileInfo()` handles set information. Both validate `DeviceObject`, extract `AFSFcb` from `FileObject->FsContext`, reject null or `AFS_REDIRECTOR_FCB` root opens, call `AFSCheckLibraryState()`, and forward to `LibraryDeviceObject`.

Control flow: control-device and root-open requests complete with `STATUS_INVALID_DEVICE_REQUEST`. Regular file-object requests use the standard library-forwarding sequence and clear the library request marker after calling the lower device.

State/persistence: no direct local metadata persistence; all file info reads/updates are delegated. Status and completion are local only for invalid requests.

Dependencies/integration: depends on FCB node typing, global control extension, library-device forwarding, common completion, and exception tracing.

Risks: misclassified root FCBs can prevent legitimate metadata operations or forward invalid ones. Set-information operations can include rename, allocation, disposition, and timestamps, so delegated validation must be comprehensive. Pending library-state behavior must not double-complete.

Test signals: query/set on control device, root redirector open rejection, regular file query/set forwarding, library unavailable/pending, and exception status conversion to `STATUS_UNSUCCESSFUL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSFileInfo.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSFlushBuffers.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSFlushBuffers.cpp

Purpose: handles flush-buffer IRPs and forwards redirector flushes to the library while rejecting the control device.

Important APIs/types/functions: `AFSFlushBuffers()` rejects `AFSDeviceObject` with `STATUS_INVALID_DEVICE_REQUEST`, calls `AFSCheckLibraryState()`, forwards to `LibraryDeviceObject`, and calls `AFSClearLibraryRequest()`.

Control flow: follows the common dispatch-wrapper pattern without a structured exception wrapper. Local invalid or library-state failure is completed immediately; pending or forwarded requests are left to the library/lower path.

State/persistence: local code persists no state. Flush semantics and cache durability are implemented by the library/redirector lower path.

Dependencies/integration: depends on `AFSDeviceObject`, `AFSDeviceExt`, library state management, and IRP completion helpers.

Risks: flush operations are durability-sensitive; this wrapper assumes `AFSCheckLibraryState()` and the library device will serialize correctly with cache manager callbacks. Unlike several sibling dispatchers, this function uses `__Enter` but no explicit `__try/__except`, so exception behavior depends on macro definitions.

Test signals: control-device rejection, forwarded flush on regular files, library unavailable/pending behavior, interaction with cache-manager flush callbacks, and shutdown-time flush handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSFlushBuffers.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSGeneric.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSGeneric.cpp

Purpose: provides shared framework utilities for the Windows OpenAFS redirector: exception handling, ERESOURCE wrappers, IRP completion, registry access, control-device initialization/teardown, server/share naming, sysname list management, kernel IOCTL sending, allocation retry behavior, shutdown coordination, cache-manager callbacks, caller SID/session/DACL helpers, and reparse-point policy.

Important APIs/types/functions: `AFSExceptionFilter()` logs exception context and optionally bugchecks/breaks. `AFSAcquireExcl()`, `AFSAcquireSharedStarveExclusive()`, `AFSAcquireShared()`, `AFSReleaseResource()`, and `AFSConvertToShared()` wrap ERESOURCE use with critical-region handling. `AFSCompleteRequest()` completes IRPs. `AFSReadRegistry()` loads debug, trace, IO, dirty-file, and shutdown policy values. `AFSUpdateRegistryParameter()` writes registry parameters. `AFSInitializeControlDevice()` and `AFSRemoveControlDevice()` initialize/delete locks, events, queues, process trees, auth trees, and library state. `AFSReadServerName()`, `AFSReadMountRootName()`, and `AFSInitServerStrings()` configure server/share names. `AFSSetSysNameInformation()` and `AFSResetSysNameList()` maintain 32/64-bit sysname lists. `AFSSendDeviceIoControl()` and `AFSIrpComplete()` build synchronous kernel IOCTLs. `AFSExAllocatePoolWithTag()` and `AFSExFreePoolWithTag()` implement allocation retry and memory-available signaling. `AFSShutdownRedirector()` coordinates graceful shutdown. `AFSAcquireFcbForLazyWrite()`, `AFSReleaseFcbFromLazyWrite()`, `AFSAcquireFcbForReadAhead()`, and `AFSReleaseFcbFromReadAhead()` support cache manager callbacks. `AFSGetCallerSID()`, `AFSGetSessionId()`, `AFSCheckThreadDacl()`, and `AFSProcessSetProcessDacl()` support AuthGroup identity. `AFSSetReparsePointPolicy()` and `AFSGetReparsePointPolicy()` manage global reparse policy.

Control flow: initialization establishes all control-device resources and sets library queues inactive/cancelled. Dispatchers call the resource wrappers and completion helpers throughout the driver. Registry reads occur during startup to populate global settings. Shutdown sets the redirector shutdown flag, waits up to 30 seconds for outstanding service requests and held extents, processes queued results, then unloads the library. Cache-manager callbacks acquire paging/section resources, set top-level IRP markers, and release them on completion. Identity helpers prefer impersonation tokens, fall back to primary tokens, and convert token SID/session data for AuthGroup operations.

State/persistence: persistent external state is the driver registry parameters read/written under the service Parameters key. In-memory state includes global debug flags, trace settings, max IO/dirty sizes, control extension locks/events/queues, process/auth trees, sysname lists, memory wait counters, outstanding service counts, reparse policy, and cache-manager resource ownership. Allocation wrappers signal `MemoryAvailableEvent` on frees.

Dependencies/integration: all modules in this subset depend on these helpers through `AFSCommon.h`. The file integrates with Windows kernel APIs (`RtlQueryRegistryValues`, `ZwOpenKey`, `IoAllocateIrp`, `SeQueryInformationToken`, token DACL APIs, ERESOURCE, Cache Manager, Object Manager), `AFSCommSupport.cpp` shutdown/request counters, AuthGroup support, network provider connection publication, and library load/unload paths outside this subset.

Risks: resource wrappers require every successful acquire to be released exactly once or critical regions remain unbalanced. Registry string construction uses fixed lengths and manual buffer copying. `AFSRemoveControlDevice()` frees only tree heads directly, so full tree/list lifetime must be handled elsewhere or leaks can occur. `AFSExAllocatePoolWithTag()` can wait 30 seconds on allocation failure and may break into the debugger. `AFSGetSessionId()` calls `SeQueryInformationToken()` with an integer cast as an output pointer, which is unusual and should be validated against the expected kernel contract in this codebase. DACL ACE insertion sizes and `AFSSetInformationToken` availability are security-critical.

Test signals: startup registry defaults and non-defaults, clean/unclean shutdown flags, control-device init/remove leak checks, sysname replacement and allocation failure cleanup, kernel IOCTL completion/freeing, memory allocation retry wakeups, shutdown timeout paths, lazy-write/read-ahead resource tracking, SID/session retrieval under impersonation and primary tokens, DACL AuthGroup ACE add/update/query, and global reparse policy set/get.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSGeneric.cpp -->
