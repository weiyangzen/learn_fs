# Research Group subset-b-007725

This grouped report covers the OpenAFS Windows redirector library files assigned to `subset-b-007725`. Each section is source-tree-aligned and delimited for reconciliation into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSNetworkProviderSupport.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSNetworkProviderSupport.cpp

## Purpose
`AFSNetworkProviderSupport.cpp` is the redirector-library side of the Windows network-provider connection interface. It maintains per-logon-session mapped-drive and UNC connection records, exposes add/cancel/get/list/get-info helpers for provider IOCTLs, validates AFS `\\server\share` names against the redirector's global-root namespace, and bridges provider enumeration requests into live AFS directory enumeration.

The file is not the user-mode network provider itself. It is the kernel redirector support layer that stores provider state in `AFSDeviceExt->Specific.RDR.ProviderConnectionList` and `ProviderEnumerationList`, using `AFSProviderConnectionCB` nodes and returning packed `AFSNetworkProviderConnectionCB` records defined in `common/AFSProvider.h`.

## Important APIs, Types, And Functions
The externally declared entry points are `AFSAddConnection`, `AFSCancelConnection`, `AFSGetConnection`, `AFSListConnections`, `AFSInitializeConnectionInfo`, `AFSLocateEnumRootEntry`, `AFSEnumerateConnection`, `AFSGetConnectionInfo`, and `AFSIsDriveMapped`.

`AFSNetworkProviderConnectionCB` is the variable-length IOCTL payload containing version, enumeration index, resource type/scope/display/usage, comment and remaining-path offsets, remote-name length, current authentication id, local drive letter, and trailing remote-name storage. `AFSCancelConnectionResultCB` returns version, WNet-style status, and the removed local name. `AFSProviderConnectionCB` is the in-kernel list node: forward link, optional child `EnumerationList`, flags, resource metadata, `AuthenticationId`, `LocalName`, `RemoteName`, `ComponentName`, and allocated `Comment`.

`AFSAddConnection` obtains the caller's authentication id with `AFSGetAuthenticationId`, normalizes the remote name by trimming a trailing slash, rejects duplicate local/auth/remote entries, validates the server component against `AFSServerName`, validates the first share component through `AFSLocateEnumRootEntry`, allocates a single provider node plus remote-name storage, initializes display metadata through `AFSInitializeConnectionInfo`, and appends the node to `ProviderConnectionList`.

`AFSCancelConnection` removes one connection by local drive or UNC remote name for the caller's authentication id. It returns `WN_NOT_CONNECTED` when no matching node exists, unlinks the node, frees its allocated comment buffer, reports the removed `LocalName`, and frees the node.

`AFSGetConnection` maps a local drive letter in the caller's authentication id back to the stored remote name. It validates output capacity and returns `STATUS_INVALID_PARAMETER` for unknown drives.

`AFSListConnections` implements both `RESOURCE_GLOBALNET` namespace enumeration and connected-resource enumeration. It can enumerate the top-level provider tree, enumerate a server's shares, enumerate a share's live directory contents through `AFSEnumerateConnection`, or list attached connections for the caller's authentication id.

`AFSGetConnectionInfo` implements provider resource-information lookup. It accepts full paths such as `\\server\share\dir...`, looks for the best existing connection prefix on a component boundary, falls back to an enumeration-root share, and can validate/create a share enumeration entry by asking the service via `AFSEvaluateTargetByName` and `AFSAddConnectionEx`. It also returns the remaining path portion separately when the query name extends below the matched provider resource.

`AFSEnumerateConnection` converts a global-root share entry into a directory enumeration by locating the share directory in `AFSGlobalRoot`, evaluating it with `AFSEvaluateRootEntry`, walking `DirectoryNodeListHead`, and writing file/directory connection records into the caller's buffer.

`AFSIsDriveMapped` scans `ProviderConnectionList` under `ProviderListLock` and compares local drive letters case-insensitively.

## Control Flow
All persistent provider-list mutations occur under `ProviderListLock` in exclusive mode; read/list operations use shared mode except when `AFSGetConnectionInfo` temporarily drops it to evaluate or create a missing share. Most entry points begin by calling `AFSGetAuthenticationId`, making provider mappings per logon session rather than process-global.

Add flow is: get authentication id, take exclusive provider lock, search existing mappings, strip leading `\\` for validation, dissect server/share with `FsRtlDissectName`, validate server name, validate share against the provider enumeration tree, restore the original remote name, allocate/copy the provider node, derive its final `ComponentName` by scanning backward to the last slash, initialize metadata, append to the connection list, and return a WNet status through `ResultStatus`.

Enumeration flow has two lanes. For `RESOURCE_GLOBALNET`, no remote name starts at `ProviderEnumerationList`; a server-only name enumerates that root's `EnumerationList`; a share name calls `AFSEnumerateConnection` to enumerate live directory entries. For non-global scopes, it walks `ProviderConnectionList`, filters out non-attached entries and mismatched authentication ids, honors `CurrentIndex`, and writes packed records until the buffer is full.

Connection-info flow deliberately does not validate every path component below a share. It first checks server identity, preserves any path below the share as `RemainingPath`, finds the longest existing connection prefix for the caller's authentication id, then falls back to share enumeration. If the share has not been discovered yet, it drops the provider lock, asks the service to evaluate the share under `AFSGlobalRoot`, adds a provider entry through the library callback `AFSAddConnectionEx`, reacquires the provider lock, and looks up the share again.

## State And Persistence Behavior
The state is in-memory redirector state only. User-visible persistent mappings live outside this file in Windows network-provider/MPR behavior; this code records the mappings currently known to the redirector for each authentication id. Connection nodes own their remote-name storage inline after the `AFSProviderConnectionCB` allocation and own `Comment.Buffer` allocations created by `AFSInitializeConnectionInfo`.

`ProviderEnumerationList` represents the global AFS provider namespace and share roots. It is populated elsewhere, including through `AFSAddConnectionEx` callbacks and global-root enumeration code. `AFSEnumerateConnection` observes live directory state beneath the global root and holds/release-counts `AFSDirectoryCB` entries while evaluating and enumerating them.

There is no disk write in this file. Persistence or freshness of share/directory names depends on the redirector's global-root and volume cache, service callbacks, and current AFS authentication group.

## Dependencies And Integration Points
This file depends on Windows kernel string and FSRTL APIs (`UNICODE_STRING`, `FsRtlDissectName`, `RtlCompareUnicodeString`, `RtlUpcaseUnicodeChar`), OpenAFS redirector globals (`AFSRDRDeviceObject`, `AFSGlobalRoot`, `AFSServerName`), synchronization helpers (`AFSAcquireShared`, `AFSAcquireExcl`, `AFSReleaseResource`), allocation callbacks (`AFSExAllocatePoolWithTag`, `AFSExFreePoolWithTag`), B-tree directory lookup helpers, service-backed target evaluation (`AFSEvaluateTargetByName`, `AFSEvaluateRootEntry`), and the external `AFSAddConnectionEx` callback supplied by the framework.

It integrates with name parsing through `AFSIsDriveMapped`, with global-root discovery through `ProviderEnumerationList`, with the user-mode network provider through provider IOCTL payloads, and with directory cache/evaluation paths through `AFSEnumerateConnection`.

## Risks And Edge Cases
Provider state is a singly linked list with manual ownership. Leaks or use-after-free bugs are possible if comment buffers, inline remote-name buffers, or node links are changed without matching the existing ownership contract.

Several paths manipulate `UNICODE_STRING.Buffer` to point inside allocated buffers, including stripping leading slashes and later freeing `uniRemoteName.Buffer`. In `AFSListConnections`, the allocated `uniRemoteName.Buffer` is advanced by one WCHAR when trimming a leading `\\`, so the cleanup free can use an interior pointer rather than the original allocation base. That deserves targeted validation or repair before changing nearby parsing.

`AFSGetConnectionInfo` includes a trace call in the no-connection branch using a newly declared uninitialized `UNICODE_STRING uniFullName`, which is a diagnostics risk in error paths. The function also intentionally accepts partial prefix matches on component boundaries, so a stale or maliciously broad mapping can influence resource-information results below a share.

Remote-name parsing tolerates trailing slash and leading slash variants but does not normalize all slash forms consistently across functions. `AFSAddConnection` requires share validation against existing enumeration roots, whereas `AFSGetConnectionInfo` can create a share entry dynamically, so behavior can differ between explicit add and informational lookup.

`AFSEnumerateConnection` returns `STATUS_OBJECT_NAME_COLLISION` on case-insensitive share collisions and stops silently when the output buffer fills. Callers must interpret copied length and enumeration index correctly.

## Test Signals
Exercise add/cancel/get/list/get-info using mapped drives and UNC-only connections, with different authentication ids, duplicate local mappings, duplicate UNC mappings with no local name, trailing slash variants, invalid server names, invalid share names, and dynamic share creation through `AFSGetConnectionInfo`.

Enumeration tests should cover top-level `RESOURCE_GLOBALNET`, server-only enumeration, share directory enumeration, `CurrentIndex` resume behavior, attached-only filtering for connected scope, buffer-full behavior, comment/remaining-path offsets, and case-insensitive share collisions.

Concurrency tests should add/cancel/list while global-root enumeration changes, and low-memory tests should fail provider-node, comment, remaining-path, and share-name allocations. Regression tests should verify `AFSIsDriveMapped` for uppercase/lowercase drive letters and verify cancellation frees comment buffers without corrupting the linked list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSNetworkProviderSupport.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSQuota.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSQuota.cpp

## Purpose
`AFSQuota.cpp` provides the dispatch handlers for quota query and quota set IRPs in the OpenAFS redirector library. In this lib implementation both handlers are stubs: they trace the incoming file object, complete the IRP with `STATUS_SUCCESS`, and return.

## Important APIs, Types, And Functions
The file exports `AFSQueryQuota(PDEVICE_OBJECT, PIRP)` and `AFSSetQuota(PDEVICE_OBJECT, PIRP)`, matching prototypes in `Include/AFSCommon.h` and major-function registration through the redirector initialization path. Both handlers fetch the current stack location with `IoGetCurrentIrpStackLocation`, use `AFSDbgTrace` for diagnostics, and call `AFSCompleteRequest`.

No AFS quota-specific structure is inspected. The input `DeviceObject` is explicitly unreferenced. The handlers do not look at `IrpSp->Parameters.QueryQuota` or `SetQuota` fields, and they do not report quota data.

## Control Flow
Each function enters with `ntStatus = STATUS_SUCCESS`, obtains `pIrpSp`, logs an entry trace at error level, completes the IRP, and exits. Exceptions are caught with `AFSExceptionFilter`; the exception block logs and dumps trace files but does not update `ntStatus` or complete the IRP if the exception occurred before completion.

## State And Persistence Behavior
There is no state mutation, no service call, and no persistence. Quota information is not cached or enforced in this file. Any AFS volume size/quota-style information exposed to Windows callers is instead surfaced through `AFSVolumeInfo.cpp` via `AFSRetrieveVolumeSizeInformation`.

## Dependencies And Integration Points
The handlers depend only on normal redirector dispatch plumbing, `AFSCompleteRequest`, tracing, and exception filtering. They integrate with the IRP major-function table so Windows quota operations have a dispatch target even though quota support is not implemented here.

## Risks And Edge Cases
Returning success for quota query/set without returning quota records can mislead callers that expect a failure such as `STATUS_INVALID_DEVICE_REQUEST`, `STATUS_NOT_IMPLEMENTED`, or `STATUS_QUOTA_NOT_ENABLED`. Set-quota requests are silently accepted and have no effect.

The functions complete inside the `__try` block. If a fault occurs before `AFSCompleteRequest`, the exception path only logs and dumps traces; completion status could be ambiguous depending on where the fault happened.

## Test Signals
Test quota query and set IRPs against files and directories, asserting completion status, `IoStatus.Information`, and user-mode API behavior. Include callers that expect enumeration records, malformed buffers, null file objects, and set-quota attempts to verify whether silent success is acceptable for the redirector contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSQuota.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSRead.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSRead.cpp

## Purpose
`AFSRead.cpp` implements read dispatch for the OpenAFS Windows redirector library. It routes reads for ordinary files, pioctl nodes, and special share/pipe nodes; selects cached, noncached cache-file extent, or direct-service IO paths; synchronizes with file locks, EOF, invalidation, and section objects; and completes the IRP with the number of bytes read.

The file is one of the central data-plane components of the redirector. Ordinary cached reads are served through the Windows Cache Manager, ordinary noncached reads are served from mapped AFS extents backed by the local cache file unless direct service IO is enabled, pioctl reads are sent to the service as `AFS_REQUEST_TYPE_PIOCTL_READ`, and special-share reads are sent as `AFS_REQUEST_TYPE_PIPE_READ`.

## Important APIs, Types, And Functions
The public handlers are `AFSRead`, `AFSCommonRead`, `AFSIOCtlRead`, and `AFSShareRead`. Static helpers are `AFSCachedRead`, `AFSNonCachedRead`, and `AFSNonCachedReadDirect`.

`AFSRead` is the dispatch shim registered for `IRP_MJ_READ`; it calls `AFSCommonRead(AFSRDRDeviceObject, Irp, NULL)` and maps exceptions to `STATUS_INSUFFICIENT_RESOURCES`.

`AFSCommonRead` is the main policy and validation routine. It pins the `FILE_OBJECT`, rejects redirector-shutdown requests, decodes `AFSFcb` and `AFSCcb`, routes `AFS_IOCTL_FCB` and `AFS_SPECIAL_SHARE_FCB`, checks cache-file readiness for persistent-cache mode, handles zero-length and MDL-complete requests, normalizes noncached reads to cached reads when a data section exists, takes paging or section-object resources, enforces byte-range locks, rejects deleted or invalid objects, applies EOF/truncation logic, initializes cache maps, handles MDL cached reads, and then calls one of the lower-level read helpers.

`AFSCachedRead` maps the IRP buffer or MDL chain, calls `CcCopyRead` one segment at a time, updates `IoStatus.Information`, advances `FileObject->CurrentByteOffset` for synchronous IO, and completes the IRP.

`AFSNonCachedRead` maps the user buffer, zero-fills the requested region beyond EOF, requests extent mappings through `AFSRequestExtentsAsync`, waits/re-requests until `AFSDoExtentsMapRegion` succeeds, builds IO runs with `AFSGetExtents` and `AFSSetupIoRun`, references active extents, queues reads against the cache file via `AFSQueueStartIos`, waits on an `AFSGatherIo` event, dereferences extents, optionally releases cached extents with flush, updates synchronous byte offset, frees temporary gather/run allocations, and completes the IRP.

`AFSNonCachedReadDirect` bypasses the cache file and sends `AFS_REQUEST_TYPE_PROCESS_READ_FILE` to the user-mode service with an `AFSFileIOCB`. It passes the system buffer and MDL, sets `AFS_REQUEST_FLAG_CACHE_BYPASS` when the file object has `FO_NO_INTERMEDIATE_BUFFERING`, and uses `AFSFileIOResultCB.Length` as the completed byte count.

`AFSIOCtlRead` maps the IRP buffer into service addressability with `AFSMapToService`, sends `AFS_REQUEST_TYPE_PIOCTL_READ` with `AFSPIOCtlIORequestCB`, and reports `AFSPIOCtlIOResultCB.BytesProcessed`.

`AFSShareRead` maps the IRP system buffer and sends a synchronous `AFS_REQUEST_TYPE_PIPE_READ` for special-share pipe semantics, accepting both success and `STATUS_BUFFER_OVERFLOW` as data-bearing outcomes.

## Control Flow
The top-level read path first validates object type and service/cache readiness. `AFS_IOCTL_FCB` and `AFS_SPECIAL_SHARE_FCB` are handled before ordinary-file cache checks. Ordinary reads then pass through common safety gates: zero-length completion, MDL completion, noncached promotion for already-cached file objects, resource acquisition, byte-range lock check, deletion/invalid flags, EOF beyond-start handling, read-length truncation to file size, and cache-map initialization for cached IO.

Cached reads retain the section-object resource and use `CcCopyRead` or `CcMdlRead`. Noncached reads release paging, section-object, and main resources before issuing lower-level IO to avoid holding file resources across cache-file/service operations. Both helper paths own IRP completion, so `AFSCommonRead` sets `bCompleteIrp = FALSE` before dispatching them.

Persistent-cache noncached flow starts by requesting extents asynchronously. It loops under `ExtentsResource` until the requested region is mapped, reissuing extent requests after the configured `ExtentRequestTimeCount` interval and waiting on `AFSWaitForExtentMapping`. Once extents are mapped, it either reads through `AFSProcessExtentRun` in nonpersistent-cache mode or sets up cache-file IO runs and waits for gathered completion. Extents are active-referenced while IO is in flight.

Direct-service noncached flow skips extent mapping entirely and asks the service to read file data. This path is selected by `AFS_DEVICE_FLAG_DIRECT_SERVICE_IO`; cache-file readiness is relaxed when `AFS_REDIR_INIT_PERFORM_SERVICE_IO` is set.

## State And Persistence Behavior
The read path updates transient kernel state: IRP status/information, synchronous file-object current byte offset, cache-map initialization state, active extent references, extent request events, and optional extent release/flush decisions. It does not directly change AFS file contents.

Persistent-cache reads consume local cache-file state through extents and cache-file `FILE_OBJECT` references. Nonpersistent-cache reads use mapped extents as the data source through `AFSProcessExtentRun`. Direct-service reads rely on the user-mode redirector service to fill the caller's buffer and optionally bypass service caching.

The FCB's `Header.FileSize`, allocation sizes, section-object resource, paging resource, `Specific.File.ExtentsResource`, file lock, object invalid/deleted flags, and CCB auth group are core state inputs. Pioctl/share reads also use `RequestID`, root FID, parent FID, and directory name state carried by `AFSCcb` and `AFSObjectInfoCB`.

## Dependencies And Integration Points
This file depends on Windows Cache Manager APIs (`CcInitializeCacheMap`, `CcCopyRead`, `CcMdlRead`, `CcMdlReadComplete`, read-ahead and dirty-page threshold tuning), Memory Manager buffer APIs (`MmGetSystemAddressForMdlSafe`, MDL byte counts), FSRTL byte-range locks, kernel events/resources, and normal IRP stack semantics.

OpenAFS integration points include `AFSRequestExtentsAsync`, `AFSDoExtentsMapRegion`, `AFSWaitForExtentMapping`, `AFSGetExtents`, `AFSSetupIoRun`, `AFSReferenceActiveExtents`, `AFSDereferenceActiveExtents`, `AFSQueueStartIos`, `AFSReferenceCacheFileObject`, `AFSReleaseCacheFileObject`, `AFSReleaseExtentsWithFlush`, `AFSProcessExtentRun`, `AFSProcessRequest`, `AFSMapToService`, `AFSUnmapServiceMappedBuffer`, and the common FCB/CCB/object-info layout.

The file is tightly coupled with write/extent code because active extent references and release-with-flush policies must agree across read and write operations.

## Risks And Edge Cases
EOF arithmetic uses `StartingByte + Length` and casts differences to `ULONG`; callers that pass pathological offsets need coverage to avoid unsigned underflow/overflow around file-size truncation. `AFSCommonRead` guards starts beyond EOF before helper calls, but helper paths still contain EOF zeroing logic that assumes nonnegative byte counts.

IRP completion ownership is delicate. Cached, noncached, direct, pioctl, and share helpers do not all complete IRPs in the same function; `AFSCommonRead` relies on `bCompleteIrp` transitions and early `try_return` paths to avoid double completion.

Resource ordering is critical. The top path takes paging and section resources for validation but releases them before noncached service/cache-file IO. Changes that hold FCB resources across extent waits or cache-file IO can deadlock with invalidation, flush, or cache-manager callbacks.

The persistent-cache noncached path waits synchronously for extents and re-requests after a timeout. If service extent delivery stalls, read latency can become very high. If active extents are not dereferenced on all failure paths, later invalidation or cache trimming can stall.

MDL reads have special failure cleanup: when `CcMdlRead` partially succeeds and then fails, the code calls `CcMdlReadComplete` if `IoStatus.Information > 0`. That behavior should remain aligned with Cache Manager contracts.

Direct-service reads expose a kernel buffer pointer and MDL metadata in `AFSFileIOCB`; the service must treat only the mapped contract as valid. `FO_NO_INTERMEDIATE_BUFFERING` changes request flags but alignment validation is not visible in this file.

## Test Signals
Ordinary-file tests should cover cached reads, MDL cached reads and MDL completion, noncached reads through cache extents, direct-service reads, nonpersistent-cache reads, zero-length reads, starts at EOF, starts beyond EOF, reads truncated at EOF, synchronous current-byte-offset updates, paging IO versus nonpaging IO, byte-range lock conflicts, deleted directory entries, invalid objects, cache-file unavailable, and redirector shutdown.

Extent tests should cover first-request success, wait and re-request after timeout, failed extent request, failed extent wait, stack versus heap IO-run allocation, gathered IO failure, active extent reference cleanup, and release-with-flush threshold behavior.

Service-special tests should cover pioctl read mapping/unmapping and byte count, parent FID propagation, special-share pipe reads with normal success and `STATUS_BUFFER_OVERFLOW`, service failures, low-memory buffer mapping failures, and malformed FCB/CCB state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSRead.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSSecurity.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSSecurity.cpp

## Purpose
`AFSSecurity.cpp` implements security descriptor query and set dispatch for the redirector library. Set-security is a no-op stub that completes successfully. Query-security returns a single default security descriptor (`AFSDefaultSD`) for all supported objects, denying SACL requests and copying the descriptor into the caller buffer.

## Important APIs, Types, And Functions
The exported handlers are `AFSSetSecurity(PDEVICE_OBJECT, PIRP)` and `AFSQuerySecurity(PDEVICE_OBJECT, PIRP)`.

`AFSSetSecurity` only traces the file object and completes the IRP with `STATUS_SUCCESS`; it does not inspect requested security information or call into the service.

`AFSQuerySecurity` reads `SecurityInformation` from the IRP stack, extracts `PFILE_OBJECT`, `AFSFcb`, and `AFSCcb`, rejects null FCBs, rejects `SACL_SECURITY_INFORMATION` with `STATUS_ACCESS_DENIED`, checks that `AFSDefaultSD` exists, computes its length with `RtlLengthSecurityDescriptor`, reports required length with `STATUS_BUFFER_OVERFLOW` when the caller buffer is too small or absent, locks the user buffer with `AFSLockUserBuffer`, copies `AFSDefaultSD`, sets `Irp->IoStatus.Information`, unlocks/frees the MDL, completes the IRP, and returns.

## Control Flow
Query-security has a simple validation sequence: decode IRP stack, validate FCB, reject SACL, validate default descriptor, check output length, lock user buffer, copy descriptor, and clean up. Cleanup always releases the MDL when allocated, then the function completes the IRP outside the `__try` block.

The CCB is decoded but not used. The requested security-information bits other than SACL do not influence which portions of the descriptor are copied; the whole default descriptor is returned.

## State And Persistence Behavior
Security state is global and process-resident. `AFSDefaultSD` is initialized elsewhere during library initialization and freed during teardown. This file does not store per-file ACLs, owner/group values, or inherited security. Set-security requests do not persist and are not relayed to AFS.

## Dependencies And Integration Points
The file depends on Windows security descriptor routines, MDL/user-buffer locking, `AFSDefaultSD` from `AFSData.cpp`/initialization, tracing, exception filtering, and `AFSCompleteRequest`. It integrates with Windows security query APIs through the redirector dispatch table, but semantic authorization for AFS data is handled elsewhere through AFS credentials and access checks, not through NTFS-style per-object descriptors here.

## Risks And Edge Cases
Returning a universal default descriptor can be surprising to callers expecting object-specific ACLs. It may be adequate as a projection layer, but tools that inspect owner/DACL information will not see AFS ACL semantics.

Set-security silently succeeds without changing anything. That can make administrative tools believe a security change was accepted even though it is not persisted or enforced.

SACL requests are denied unconditionally, which is sensible without audit privilege handling but should be tested because backup/security tools may request SACL together with DACL or owner bits.

`RtlZeroMemory` is not applied to unused output portions; only the descriptor length is copied. The code relies on `AFSLockUserBuffer` and caller length checks to protect the copy.

## Test Signals
Test owner, group, DACL, and combined query masks; SACL-only and SACL-combined masks; too-small buffer length with `IoStatus.Information` set to descriptor length; null user buffer; missing `AFSDefaultSD`; invalid FCB; and normal copy with MDL lock/unlock. Set-security tests should verify the current silent-success/no-effect behavior and decide whether that is intentional API compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSSecurity.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSShutdown.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSShutdown.cpp

## Purpose
`AFSShutdown.cpp` provides the redirector library's shutdown dispatch handler. In this lib version the actual filesystem shutdown helper is a placeholder returning `STATUS_SUCCESS`; the dispatch path calls it, normalizes any failure back to success, completes the IRP, and returns.

## Important APIs, Types, And Functions
The exported functions are `AFSShutdown(PDEVICE_OBJECT, PIRP)` and `AFSShutdownFilesystem(void)`. `AFSShutdown` is registered for `IRP_MJ_SHUTDOWN` by the initialization code. It obtains the current stack location but does not use it, invokes `AFSShutdownFilesystem`, calls `AFSCompleteRequest`, and handles exceptions through `AFSExceptionFilter`.

`AFSShutdownFilesystem` currently declares `ntStatus = STATUS_SUCCESS` and returns it without setting flags, flushing extents, closing cache files, or notifying the service.

## Control Flow
Shutdown dispatch is intentionally success-biased. Even if `AFSShutdownFilesystem` returned an error, `AFSShutdown` would replace it with `STATUS_SUCCESS` before completing the IRP. Exceptions are logged and trace files are dumped, but no alternate completion status is assigned in the exception block.

## State And Persistence Behavior
This file mutates no state. It does not set `AFS_DEVICE_FLAG_REDIRECTOR_SHUTDOWN`, tear down volumes, flush cached data, drain workers, or persist any state. Those behaviors, if present, live in other teardown and worker modules.

## Dependencies And Integration Points
The file depends on dispatch registration, `AFSCompleteRequest`, tracing, and exception filtering. It integrates with system shutdown notification only as an IRP endpoint; substantive shutdown ordering is external.

## Risks And Edge Cases
The main risk is false success. If future code adds real shutdown work inside `AFSShutdownFilesystem`, the dispatch wrapper currently hides failures. As written, shutdown behavior depends on other parts of the driver having already flushed or quiesced important state.

Because the current helper is empty, tests should not assume this path protects cache consistency. It is a compatibility hook rather than a full shutdown implementation.

## Test Signals
Test that `IRP_MJ_SHUTDOWN` completes successfully and does not crash with normal file-object/device state. If shutdown work is added later, add tests for failure propagation policy, cache flush ordering, worker shutdown, volume teardown, and interaction with reads/writes racing shutdown flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSShutdown.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSSystemControl.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSSystemControl.cpp

## Purpose
`AFSSystemControl.cpp` implements the redirector library handler for `IRP_MJ_SYSTEM_CONTROL`. In this lib implementation it is a minimal stub: log the incoming file object, complete the IRP with `STATUS_SUCCESS`, and return.

## Important APIs, Types, And Functions
The file exports `AFSSystemControl(PDEVICE_OBJECT, PIRP)`. It ignores the device object, obtains the current IRP stack location with `IoGetCurrentIrpStackLocation`, logs through `AFSDbgTrace`, completes via `AFSCompleteRequest`, and wraps the body in `__try/__except` using `AFSExceptionFilter`.

The handler does not inspect WMI/system-control minor functions, GUIDs, buffers, or provider registration state.

## Control Flow
There is one straight-line path: initialize success, get stack location, trace the file object at warning level, complete the IRP, return success. The exception handler logs and dumps trace files.

## State And Persistence Behavior
No state is read except the stack location for logging, and no state is mutated or persisted. The file does not register, query, or update WMI data.

## Dependencies And Integration Points
This is a dispatch-table integration point for system-control IRPs. It depends only on common tracing, exception filtering, and completion helpers. Real observability is likely provided by the driver's own trace mechanisms rather than WMI through this handler.

## Risks And Edge Cases
Completing all system-control requests successfully without forwarding or interpreting them can confuse WMI clients or verifier expectations if the driver is expected to participate in WMI. If the file system stack expects unsupported system-control IRPs to be passed down or failed with a specific status, this stub should be checked against the redirector's device stack design.

## Test Signals
Issue representative system-control IRPs and verify the expected completion status, no leaked IRPs, and no unexpected WMI registration assumptions. Driver Verifier/WMI-focused tests should confirm that success-with-no-data is acceptable for this redirector.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSSystemControl.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSVolume.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSVolume.cpp

## Purpose
`AFSVolume.cpp` creates, caches, references, and removes redirector volume control blocks (`AFSVolumeCB`). It initializes the volume root object/directory structures, inserts non-reserved volumes into the global volume hash tree and list, retrieves volume metadata from the service, tears down volume-owned resources, and tracks reference counts by reason.

## Important APIs, Types, And Functions
The exported routines are `AFSInitVolume`, `AFSRemoveVolume`, `AFSVolumeIncrement`, and `AFSVolumeDecrement`.

`AFSInitVolume(GUID *AuthGroup, AFSFileID *RootFid, LONG VolumeReferenceReason, AFSVolumeCB **VolumeCB)` is both lookup and constructor. For non-reserved cell ids, it first retrieves `AFSVolumeInfoCB` via `AFSRetrieveVolumeInformation`, then takes the global volume tree/list locks and checks whether another thread already inserted the volume. On a hit it increments the existing volume by the caller's reason, releases global locks, exclusively acquires the volume lock, returns the existing `AFSVolumeCB`, and leaves the volume lock held for the caller. On a miss, or for reserved/global-root style entries with `Cell == 0`, it allocates and initializes a new volume.

The new-volume allocation path creates a paged `AFSVolumeCB`, nonpaged `AFSNonPagedVolumeCB`, nonpaged root `AFSNonPagedObjectInfoCB`, nonpaged root `AFSNonPagedDirectoryCB`, and paged root `AFSDirectoryCB`. It initializes `VolumeLock`, `ObjectInfoTreeLock`, object-info lock, directory-node-header lock, the root directory entry name `"\"`, root object file id, directory attributes, volume metadata, and object/directory back-pointers. Non-reserved volumes are inserted into `Specific.RDR.VolumeTree` using `AFSCreateHighIndex` and into `VolumeListHead/Tail`.

`AFSRemoveVolume` assumes `VolumeReferenceCount == 0`, removes non-reserved volumes from the hash tree and doubly linked volume list, removes any PIOCtl directory FCB/object, releases service-held FIDs, deletes ERESOURCEs, frees nonpaged and paged root structures, and finally frees the volume control block.

`AFSVolumeIncrement` and `AFSVolumeDecrement` update both total `VolumeReferenceCount` and the per-reason `VolumeReferences[Reason]` counters with interlocked operations and assert nonnegative counts on decrement.

## Control Flow
Initialization deliberately calls the service before taking volume-tree locks to avoid blocking global volume structures on communication. It then locks both the volume tree and list to handle races. If a matching volume exists, it returns the existing object with a new reference and the volume lock held.

When constructing a volume, the function initializes resources before publishing the volume in shared structures. It increments the volume reference before taking its volume lock, initializes root directory/object state, copies service volume information, and only inserts into hash/list for real cell entries. Reserved entries such as the global root are allocated but not inserted into the normal volume cache.

Failure cleanup frees each allocation that succeeded. Global tree/list locks are released through `bReleaseLocks`. On success the returned volume lock remains acquired, matching the existing-volume hit path.

Removal is the inverse path. It unlinks the volume from global structures, tears down special PIOCtl child state if present, releases service FID ownership when `AFS_OBJECT_HELD_IN_SERVICE` is set, deletes resources if currently owned, frees nonpaged object/volume/directory memory, frees root directory memory, and frees the VCB.

## State And Persistence Behavior
The persistent state is in-memory redirector volume cache state. `AFSVolumeCB` stores volume references, object-info tree, root object info, root directory entry, root FCB pointer, service-provided `AFSVolumeInfoCB`, hash-tree linkage, list linkage, and nonpaged locks. The service remains authoritative for volume metadata and size; this file caches metadata at initialization.

There is no direct disk persistence. Volume lifetime is governed by reference counts and global cache membership. Per-reason counts expose why a volume is held (`MOUNTPT`, `BUILD_ROOT`, `LOCATE_NAME`, `PARSE_NAME`, etc.), which is useful for diagnostics and leak detection.

## Dependencies And Integration Points
This file depends on redirector device extension state (`VolumeTree`, `VolumeListLock`, `VolumeListHead/Tail`), service communication (`AFSRetrieveVolumeInformation`, `AFSReleaseFid`), B-tree helpers (`AFSLocateHashEntry`, `AFSInsertHashEntry`, `AFSRemoveHashEntry`), object cleanup (`AFSRemoveFcb`, `AFSObjectInfoDecrement`, `AFSDeleteObjectInfo`), resource helpers, and allocation callbacks.

It integrates with name resolution and mount-point traversal (`AFSBuildRootVolume`, `AFSBuildMountPointTarget`, `AFSLocateNameEntry`), object/FID caching, PIOCtl support, and any path that holds or releases `AFSVolumeCB` references.

## Risks And Edge Cases
Ownership and lock contracts are non-obvious: successful `AFSInitVolume` returns with `VolumeLock` acquired exclusively in both lookup-hit and new-allocation paths. Callers must release it consistently.

Failure cleanup calls `AFSReleaseResource(pVolumeCB->VolumeLock)` when `pNonPagedVcb != NULL`; this assumes the volume lock was acquired before the failure. Allocation-order changes could make that unsafe.

The function retrieves volume metadata before checking for an existing cached volume, so concurrent initializers can issue redundant service calls. That is intentional for lock ordering but can amplify load under mount storms.

Reference reasons are used as array indexes without visible range checks in `AFSVolumeIncrement/Decrement`; invalid reasons would corrupt adjacent memory. Callers must pass constants below `AFS_VOLUME_REFERENCE_MAX`.

Removal assumes the caller has already drained references and synchronized against new lookup/increment paths. If a volume remains reachable in a name array, directory entry, or worker while `AFSRemoveVolume` runs, freed locks and object-info pointers could be reused.

## Test Signals
Test first initialization of global-root/reserved volumes and real cell volumes, concurrent initialization of the same real volume, service metadata failure, allocation failures at each allocation site, hash/list insertion and removal, returned-lock ownership, reference increment/decrement by each reason, underflow assertions, PIOCtl child cleanup, service-held FID release, and removal of head/tail/middle volume-list nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSVolume.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSVolumeInfo.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSVolumeInfo.cpp

## Purpose
`AFSVolumeInfo.cpp` handles Windows filesystem volume-information queries for the redirector. It validates the target FCB, selects the requested `FS_INFORMATION_CLASS`, formats data from cached `AFSVolumeInfoCB`, retrieves live size/allocation data from the service for size classes, and completes the IRP. Set-volume-information is a no-op stub.

## Important APIs, Types, And Functions
The public dispatch routines are `AFSQueryVolumeInfo(PDEVICE_OBJECT, PIRP)` and `AFSSetVolumeInfo(PDEVICE_OBJECT, PIRP)`. Helper formatters are `AFSQueryFsVolumeInfo`, `AFSQueryFsSizeInfo`, `AFSQueryFsDeviceInfo`, `AFSQueryFsAttributeInfo`, and `AFSQueryFsFullSizeInfo`.

`AFSQueryVolumeInfo` obtains `FILE_OBJECT`, `AFSFcb`, `AFSObjectInfoCB`, and `AFSVolumeCB`, detects DOS-device-style opens from the file name, takes the volume lock shared, rejects pioctl, special-share, and invalid FCB node types, and switches on the requested class: `FileFsVolumeInformation`, `FileFsSizeInformation`, `FileFsDeviceInformation`, `FileFsAttributeInformation`, and `FileFsFullSizeInformation`.

`AFSQueryFsVolumeInfo` fills `FILE_FS_VOLUME_INFORMATION`. For DOS-device opens it returns just the volume label; otherwise it exposes `cell#volumeLabel` by concatenating `VolumeInfo->Cell`, a `#`, and `VolumeInfo->VolumeLabel`. It returns `STATUS_BUFFER_OVERFLOW` when the fixed header fits but the complete label does not.

`AFSQueryFsSizeInfo` and `AFSQueryFsFullSizeInfo` build a minimal `AFSFileID` from `CellID` and `VolumeID`, call `AFSRetrieveVolumeSizeInformation`, and copy total/available allocation units, sectors per allocation unit, and bytes per sector into Windows size structures.

`AFSQueryFsDeviceInfo` reports `FILE_DEVICE_DISK` rather than `FILE_DEVICE_NETWORK_FILE_SYSTEM` to keep Win32 `GetFileType()` behavior compatible with MSYS-style applications, while preserving volume characteristics.

`AFSQueryFsAttributeInfo` returns filesystem attributes, maximum component length 255, and filesystem name `AFSRDRFsd`.

`AFSSetVolumeInfo` traces and completes with success without applying changes.

## Control Flow
The query dispatch path validates pointers before locking. It sets `ulLength` from the caller's output length and `pBuffer` from `Irp->AssociatedIrp.SystemBuffer`, then holds `pVolumeCB->VolumeLock` shared while formatting the requested class. At exit it sets `Irp->IoStatus.Information` to the original requested length minus the helper's remaining length, releases the volume lock, and completes the IRP.

The helper routines all zero the provided buffer for the caller-provided remaining length before checking whether the length is large enough. Fixed-size helpers return `STATUS_BUFFER_TOO_SMALL` if the fixed structure does not fit. Variable-size helpers can return success or overflow after filling the fixed header and as much string data as fits.

## State And Persistence Behavior
Volume identity and descriptive metadata come from the cached `AFSVolumeInfoCB` stored in `AFSVolumeCB`, originally populated by `AFSInitVolume` through `AFSRetrieveVolumeInformation`. Size and free-space answers are live service queries through `AFSRetrieveVolumeSizeInformation`, so quota/free-space behavior is not solely cached.

The file does not modify persistent volume state. `AFSSetVolumeInfo` is a no-op success path and does not change labels, attributes, or quotas.

## Dependencies And Integration Points
This file depends on `AFSFcb`, `AFSObjectInfoCB`, `AFSVolumeCB`, `AFSVolumeInfoCB`, Windows `FILE_FS_*` structures, service communication for size information, redirector volume locking, and common dispatch completion. It integrates with Windows APIs such as `GetVolumeInformation`, free-space queries, and file type detection.

It also complements `AFSQuota.cpp`: quota-style numbers presented to Windows callers are effectively exposed through filesystem size/full-size information, not through quota IRPs.

## Risks And Edge Cases
`AFSQueryVolumeInfo` assumes `pObjectInfo->VolumeCB` is non-null before taking `pVolumeCB->VolumeLock`; corrupt or partially initialized FCB state could fault and rely on the exception handler.

`IoStatus.Information` is computed as requested length minus remaining length even on errors. This is normal for partial fixed-header/string responses but should be verified for `STATUS_BUFFER_TOO_SMALL`, service failures, and invalid classes.

`AFSQueryFsVolumeInfo` and `AFSQueryFsAttributeInfo` can return partial string data with overflow. Callers must handle `STATUS_BUFFER_OVERFLOW` and retry with the advertised lengths. The volume label format differs between DOS-device and non-DOS-device opens, which can produce different labels for the same underlying volume.

Returning `FILE_DEVICE_DISK` intentionally trades strict network-filesystem identity for user-mode compatibility; code that expects a network device type may not see it through this query.

Set-volume-information silently succeeds without effect, similar to security and quota set stubs.

## Test Signals
Test every supported `FS_INFORMATION_CLASS`, invalid/unsupported classes, pioctl/special-share/invalid FCB rejection, null file object/Fcb/object info, DOS-device versus normal label formatting, small fixed buffers, partial string buffers, service failure for size/full-size classes, `IoStatus.Information` on success/overflow/too-small, reported device type, filesystem name length/content, and no-op set-volume behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSVolumeInfo.cpp -->
