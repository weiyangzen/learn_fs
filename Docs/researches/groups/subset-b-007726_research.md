# Research Group subset-b-007726

This grouped report covers the OpenAFS Windows redirector worker, write, and shared kernel-library header files assigned to `subset-b-007726`. Each file section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSWorker.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSWorker.cpp

## Purpose
`AFSWorker.cpp` implements the kernel redirector library's asynchronous worker infrastructure. It creates and tears down a general worker pool, an I/O worker pool, and a special global-root volume worker; dispatches queued work items for extent flushing, global-root enumeration, object invalidation, authentication-id lookup, cache-file I/O fanout, and deferred writes; and periodically garbage-collects idle volumes, object-info blocks, directory entries, and FCBs.

## Important APIs, Types, And Functions
The public worker lifecycle APIs are `AFSInitializeWorkerPool`, `AFSRemoveWorkerPool`, `AFSInitWorkerThread`, `AFSInitVolumeWorker`, `AFSShutdownWorkerThread`, `AFSShutdownIOWorkerThread`, and `AFSShutdownVolumeWorker`. Queue primitives include `AFSInsertWorkitem`, `AFSInsertIOWorkitem`, `AFSInsertWorkitemAtHead`, `AFSRemoveWorkItem`, `AFSRemoveIOWorkItem`, `AFSQueueWorkerRequest`, `AFSQueueIOWorkerRequest`, and `AFSQueueWorkerRequestAtHead`. Higher-level producers are `AFSQueueFlushExtents`, `AFSQueueGlobalRootEnumeration`, `AFSQueueStartIos`, `AFSQueueInvalidateObject`, and `AFSDeferWrite`; `AFSPostedDeferredWrite` is the `CcDeferWrite` callback that moves delayed writes to the I/O worker.

The important execution bodies are `AFSWorkerThread`, `AFSIOWorkerThread`, and `AFSPrimaryVolumeWorkerThread`. Static helpers `AFSExamineVolume` and `AFSExamineObjectInfo` encapsulate volume/object garbage collection. All work items use `AFSWorkItem` from `AFSStructs.h`, with request codes from `AFSDefines.h`.

## Control Flow
`AFSInitializeWorkerPool` allocates up to `AFS_WORKER_COUNT` generic workers and `AFS_IO_WORKER_COUNT` I/O workers. Initialization tolerates partial pool creation if at least one worker of each kind exists; otherwise it tears the pool down. Each worker context is zeroed, receives `AFS_WORKER_PROCESS_REQUESTS`, starts a system thread, references the thread object, and waits for the thread-ready event.

Generic workers wait on `WorkerQueueHasItems`, remove FIFO work items under the control queue lock, switch on `RequestType`, and either free asynchronous work items or signal the embedded event for synchronous requests. They flush FCB extents unless the redirector is in direct-service-I/O mode, enumerate the global root, invalidate objects, and perform auth-id lookup. I/O workers wait on `IOWorkerQueueHasItems` and handle `AFS_WORK_START_IOS` by calling `AFSStartIos` and `AFSCompleteIo`, or `AFS_WORK_DEFERRED_WRITE` by reinvoking `AFSCommonWrite` with the saved caller process and retry flag.

The primary volume worker is a timer-driven system thread attached to `AFSGlobalRoot`. Every 5 seconds it walks the redirector volume list, skips the global root, takes volume locks opportunistically where possible, removes completely idle volumes, or calls `AFSExamineVolume` to collect stale object state. Object cleanup increments worker references before examination, holds the volume object-info tree exclusive while deleting, and drops/reacquires locks around `AFSCleanupFcb` where holding the tree lock would be unsafe.

Shutdown is two-stage: pool removal first clears `AFS_WORKER_PROCESS_REQUESTS` on all contexts so workers stop accepting requests, then signals the relevant queue event while waiting for `AFS_WORKER_INITIALIZED` to clear, dereferences thread objects, and frees worker contexts.

## State And Persistence
All state is in kernel memory. Pool lists, counts, queue heads/tails, queue item counts, queue events, and queue locks live under the control device extension. Worker contexts store the thread-ready event, referenced thread object, state flags, and link pointer. Queued flushes temporarily increment `Fcb->Specific.File.QueuedFlushCount` and `Fcb->OpenReferenceCount`; completion decrements them and signals `QueuedFlushEvent` when the flush queue drains. Volume cleanup mutates volume lists, object-info trees, directory-entry lists, FCB pointers, reference counts, and directory-enumerated flags, but it does not persist data outside the redirector cache/service state.

## Dependencies And Integration Points
The file depends on Windows kernel thread, event, timer, resource, object-reference, and cache-manager APIs (`PsCreateSystemThread`, `KeWaitForSingleObject`, `KeSetEvent`, `KeSetTimerEx`, `ObReferenceObjectByHandle`, `CcDeferWrite`). It integrates with global device objects (`AFSControlDeviceObject`, `AFSRDRDeviceObject`, `AFSLibraryDeviceObject`), extent support (`AFSFlushExtents`, `AFSReleaseExtentsWithFlush`), cache I/O support (`AFSStartIos`, `AFSCompleteIo`), write dispatch (`AFSCommonWrite`), name/volume/object cleanup (`AFSDeleteDirEntry`, `AFSRemoveFcb`, `AFSCleanupFcb`, `AFSDeleteObjectInfo`, `AFSRemoveVolume`), service authentication (`AFSRetrieveValidAuthGroup`, `AFSPerformGetAuthId`), and invalidation/global-root routines.

## Risks And Edge Cases
The worker code is concurrency-sensitive. Queue counts, FCB open counts, object-info reference counts, and volume locks must remain balanced across failures and worker exits. Synchronous work waits only for the work-item event and does not automatically return the work item's `Status`, so callers must understand that contract. `AFSQueueFlushExtents` caps queued flush depth but increments and decrements the queue counter even when it decides not to allocate a work item. The object cleanup path intentionally holds the object-info tree exclusive during deletions, which can stall lookups; it yields when waiters appear. The PIOCtl cleanup branch references `pCurrentChildObject` while freeing a PIOCtl directory entry even though the visible local pointer is not assigned in that branch, which is a high-risk null/stale-pointer hazard to inspect before modifying that code. `AFSCommon.h` declares `AFSQueuePurgeObject`, but this file does not define it.

## Test Signals
Useful test signals include successful startup with full and partially allocated worker pools, shutdown with queued and empty queues, FIFO and head-insertion ordering, synchronous work-item event signaling, deferred cached writes completing through `CcDeferWrite`, I/O worker fanout completion status propagation, read/write cache I/O stress with multiple queued runs, extent flush throttling and `QueuedFlushEvent` signaling, direct-service-I/O mode suppressing local extent flushes, auth-id work under process/thread context, global-root enumeration requests, object invalidation requests, and long-running volume churn that proves idle volumes/objects are collected without deleting active or recently accessed objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSWorker.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSWrite.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSWrite.cpp

## Purpose
`AFSWrite.cpp` implements write dispatch for the OpenAFS Windows redirector library. It validates write IRPs, routes PIOCtl and special-share writes to service-specific paths, coordinates cached, noncached, paging, extending, write-through, and direct-service writes, maps user buffers and extents, updates FCB/object metadata, and completes or defers IRPs according to Windows cache-manager flow control.

## Important APIs, Types, And Functions
The public entry points are `AFSWrite`, `AFSCommonWrite`, `AFSIOCtlWrite`, `AFSShareWrite`, and `AFSDeferWrite` (declared in `AFSCommon.h`; `AFSDeferWrite` is implemented in `AFSWorker.cpp`). Static helpers are `AFSCachedWrite`, `AFSNonCachedWrite`, `AFSNonCachedWriteDirect`, and `AFSExtendingWrite`. Key data types are `AFSFcb`, `AFSCcb`, `AFSObjectInfoCB`, `AFSGatherIo`, `AFSIoRun`, `AFSExtent`, `AFSPIOCtlIORequestCB`, `AFSPipeIORequestCB`, and `AFSFileIOCB`.

## Control Flow
`AFSWrite` is a thin exception-guarded dispatch wrapper around `AFSCommonWrite`. `AFSCommonWrite` extracts the file object, FCB, CCB, byte offset, length, paging/noncached flags, synchronous state, and caller process. It rejects shutdown, invalid node types, unavailable persistent cache files, read-only volumes, zero-length writes, invalid/deleted objects, and byte-range lock conflicts. PIOCtl and special-share FCBs route to `AFSIOCtlWrite` and `AFSShareWrite`.

For ordinary file writes, noncached writes against an already cached file are promoted to cached writes with `ForceFlush` to avoid stale cache data. Cached user writes initialize a cache map on first use, set read-ahead granularity and dirty-page thresholds, and obey `CcCanIWrite`: old synchronous file-object behavior on pre-Vista spins with a 10 ms delay, while newer or asynchronous requests use `AFSDeferWrite` and return `STATUS_PENDING`. Locking separates paging I/O, extending/noncached writes, and normal writes: paging takes the paging resource; extending or noncached writes take the main FCB resource and section-object resource exclusive; nonextending cached writes take them shared and retry if the file size changes under the shared lock.

When a write extends EOF, `AFSExtendingWrite` updates allocation size and file size in the FCB/object info, sends `AFSUpdateFileInformation` to the service, marks change-time update flags, calls `CcSetFileSizes` if the file is cached, and restores old sizes on failure. After dispatch, successful nonpending nonpaging writes update synchronous current byte offset, valid-data length, and `FO_FILE_MODIFIED`. Noncached writes against cached files purge the affected cache section, setting `AFS_FCB_FLAG_PURGE_ON_CLOSE` if purge fails.

`AFSCachedWrite` handles MDL writes with `CcPrepareMdlWrite`/`CcMdlWriteComplete`, otherwise copies data into the cache with `CcCopyWrite`, walking MDL chains when present. Write-through or forced-flush writes call `CcFlushCache` and reset `LastServerFlush` so worker-driven server flushes occur promptly. `AFSNonCachedWrite` locks the user buffer, requests and waits for mapped extents, builds cache-file I/O runs, queues them through `AFSQueueStartIos`, waits for the gather event, marks extents dirty, and resets server-flush timing. In nonpersistent-cache mode it bypasses cache-file I/O and processes the extent run in memory. `AFSNonCachedWriteDirect` bypasses local extents/cache-file writes and sends `AFS_REQUEST_TYPE_PROCESS_WRITE_FILE` directly to the service with file metadata and optional cache-bypass flag.

## State And Persistence
Write operations mutate in-memory FCB and object metadata: file size, allocation size, valid data length, EOF, change time, file-modified/update flags, last-writer process id, dirty extent state, and server-flush timing. Cached writes persist first to the Windows cache manager and eventually to the OpenAFS service through dirty extent flushing. Noncached writes normally persist into the local cache file then mark extents dirty for service flush; direct-service writes persist by synchronous service request. PIOCtl and share writes are request/response service operations keyed by CCB request IDs and auth groups.

## Dependencies And Integration Points
The file depends on Windows I/O manager, cache manager, memory manager, file-lock, and section-object APIs (`IoGetCurrentIrpStackLocation`, `CcInitializeCacheMap`, `CcCanIWrite`, `CcCopyWrite`, `CcFlushCache`, `CcPurgeCacheSection`, `CcPrepareMdlWrite`, `FsRtlCheckLockForWriteAccess`, MDL mapping). It integrates with the service RPC layer (`AFSProcessRequest`, `AFSUpdateFileInformation`), extent subsystem (`AFSRequestExtentsAsync`, `AFSWaitForExtentMapping`, `AFSDoExtentsMapRegion`, `AFSGetExtents`, `AFSSetupIoRun`, `AFSMarkDirty`), cache-file reference helpers, worker I/O queueing, PIOCtl and pipe protocols, and global redirector flags such as direct-service-I/O and nonpersistent-cache mode.

## Risks And Edge Cases
Write correctness depends on lock ordering across FCB main, paging, section-object, and extent resources. Extending writes call `CcSetFileSizes` while comments note the ideal paging-resource-only constraint, so changes here require care. Promoting noncached writes to cached writes when a data section exists avoids stale data but changes the caller's expected path. Noncached writes assume extent mapping eventually completes and periodically re-request extents; bad service responses can stall or fail the IRP. Cache purge failures after noncached writes are deferred to close via `AFS_FCB_FLAG_PURGE_ON_CLOSE`, leaving a window where cached readers need scrutiny. Direct-service writes must pass the correct auth group, file id, name, cell string, MDL, and cache-bypass semantics. PIOCtl/share writes are synchronous and allocate/copy buffers in kernel memory, so length validation and cleanup are important.

## Test Signals
Test zero-length writes, invalid/deleted/read-only targets, PIOCtl writes, special-share pipe writes, cached writes with and without MDLs, first cached write cache-map initialization, `CcCanIWrite` deferral and retry, pre-Vista synchronous behavior if supported, write-to-EOF offsets, EOF/VDL/allocation extension, byte-range lock conflicts, write-through/FO no-intermediate-buffering flushes, noncached writes with stack and heap I/O run arrays, nonpersistent-cache writes, direct-service-I/O writes, extent-request retry timeouts/failures, cache-file unavailable errors, purge failure setting purge-on-close, and completion behavior for pending versus synchronous paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSWrite.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/Include/AFSCommon.h -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/Include/AFSCommon.h

## Purpose
`AFSCommon.h` is the central kernel-mode public header for the OpenAFS Windows redirector library. It defines the common include set, imports Windows kernel and OpenAFS user/service protocol headers, exposes compatibility declarations, and declares the library's cross-module APIs for create, read, write, extent, volume, object, name, security, cleanup, service communication, worker, and utility code.

## Important APIs, Types, And Functions
The header includes `ntifs.h`, `wdmsec.h`, `ntintsafe.h`, `AFSDefines.h`, user ioctl/structure headers, redirector common headers, `AFSStructs.h`, provider definitions, and usually `AFSExtern.h`. It declares compatibility APIs such as `ZwQueryInformationProcess` and `RtlAbsoluteToSelfRelativeSD` and defines `AFS_KERNEL_MODE`.

Major API families include B-tree/name lookup helpers; driver and library lifecycle (`DriverEntry`, `AFSUnload`, `AFSInitializeLibrary`, `AFSCloseLibrary`, library device creation/removal); service communication (`AFSEnumerateDirectory`, `AFSNotifyFileCreate`, `AFSUpdateFileInformation`, pipe operations, volume/file status operations); create/open paths; extent management; cache-file I/O fanout; read/write dispatch; file information and EA operations; flush, volume, directory-control, FS/device/internal-control, shutdown, lock, cleanup, security, system-control, quota, and generic helpers; object/name invalidation and validation; name-array utilities; worker pool/queue APIs; and optional MD5 generation.

## Control Flow And Integration
`AFSCommon.h` has no executable control flow, but it establishes the call graph contract for the redirector library. A typical file operation enters through dispatch prototypes (`AFSCreate`, `AFSRead`, `AFSWrite`, `AFSSetFileInfo`, etc.), uses FCB/CCB/object structures from `AFSStructs.h`, calls service-facing request helpers for server/cache-manager state, coordinates local cache extents and cache-file I/O, and may queue asynchronous worker operations. The header's ordering matters: core defines and user protocol types are included before structures/prototypes that reference them, and `AFSExtern.h` is included unless `NO_EXTERN` is set to let defining translation units avoid duplicate extern declarations.

## State And Persistence
The header itself stores no state. It exposes APIs that operate on persistent or semi-persistent surfaces: Windows cache manager state, redirector cache-file state, OpenAFS service metadata, volume/object/dir-entry trees, FCB/CCB lifetimes, extent dirty/clean state, auth groups, network-provider connection data, and security descriptors. It also declares `AFSReferenceCacheFileObject`/`AFSReleaseCacheFileObject`, signaling shared ownership of the persistent cache file object.

## Dependencies And Integration Points
The file is Windows-kernel-specific and depends on WDK headers, OpenAFS redirector user/kernel protocol headers, C++ `extern "C"` linkage around C-style kernel functions, and all major library source files. It is the integration point between files such as `AFSWrite.cpp`, `AFSWorker.cpp`, `AFSRead.cpp`, `AFSGeneric.cpp`, `AFSNameSupport.cpp`, `AFSExtentsSupport.cpp`, `AFSIoSupport.cpp`, `AFSVolume.cpp`, and service communication modules.

## Risks And Edge Cases
Because this header is broad, prototype drift can break many translation units at once. Duplicated declarations exist, including `AFSShutdownVolumeWorker` appearing twice, and `AFSQueuePurgeObject` is declared even though no definition appears in the reviewed `AFSWorker.cpp`. Changes to include order can expose missing type dependencies. The `extern "C"` block is important for linkage stability in a C++ kernel library. Pointer ownership and locking preconditions are mostly implicit in prototypes, so callers must follow implementation-specific contracts that are not enforced by the type system.

## Test Signals
Primary signals are full Windows driver/library compilation, link coverage for every declared non-inline function, static analysis for SAL/IRQL/locking assumptions, include-order tests with and without `NO_EXTERN`, and runtime coverage of all dispatch families. Targeted compile checks should catch duplicate/stale prototypes, missing definitions such as declared worker helpers, and ABI mismatches against service/user protocol structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/Include/AFSCommon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/Include/AFSDefines.h -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/Include/AFSDefines.h

## Purpose
`AFSDefines.h` centralizes compile-time switches, compatibility shims, constants, flags, request codes, timing values, extent geometry, network-provider constants, GUIDs, and small flag macros for the OpenAFS Windows redirector kernel library.

## Important APIs, Types, And Constants
The file provides an older-Windows compatibility definition for `FsRtlSetupAdvancedHeader`, function-pointer typedefs for security-descriptor routines, worker pool sizes (`AFS_WORKER_COUNT`, `AFS_IO_WORKER_COUNT`), worker state flags, worker request codes, synchronous request flags, FCB/object/volume reference flags, object lifetime and extent request timing, stack I/O run threshold, `FlagOn`/`BooleanFlagOn`/`SetFlag`/`ClearFlag`, write-to-EOF checking, CCB and directory-entry flags, network-provider status/resource constants, control/redirector instance flags, extent list geometry, dirty chunk threshold, redirector control and OpenAFS DFS reparse GUIDs, enumeration index constants, and library state flags such as `AFS_REDIR_LIB_FLAGS_NONPERSISTENT_CACHE`.

## Control Flow And Integration
There is no runtime control flow, but these definitions drive control flow across worker dispatch, write/read dispatch, object cleanup, name parsing, directory enumeration, extent mapping, invalidation, and network-provider operations. For example, `AFS_WORK_DEFERRED_WRITE` and `AFS_WORK_START_IOS` are consumed by `AFSWorker.cpp`; `AFS_MAX_STACK_IO_RUNS`, `AFS_DIRTY_CHUNK_THRESHOLD`, and `IS_BYTE_OFFSET_WRITE_TO_EOF` are consumed by I/O paths; object/volume reference reason indexes size reference accounting arrays in `AFSStructs.h`.

## State And Persistence
No state is stored here. The constants shape in-memory state layout and persistence behavior elsewhere: object lifetime determines garbage-collection eligibility, extent sizes and skip-list geometry determine cache mapping granularity, server flush/purge delays influence dirty-data retention, and flag values are persisted in memory fields such as FCB, object-info, directory-entry, connection, and process-control structures.

## Dependencies And Integration Points
The header depends on Windows kernel primitive names, interlocked operations, security descriptor types, file-offset sentinel values, and GUID macros. It is included by `AFSCommon.h` before structures and prototypes, making it foundational for `AFSStructs.h`, `AFSWorker.cpp`, `AFSWrite.cpp`, extent support, name support, and provider-support code.

## Risks And Edge Cases
Many constants are ABI-like within the driver. Changing worker request codes, reference-reason counts, flag bits, extent geometry, or special enumeration indexes can silently corrupt queues, arrays, trees, or service/kernel protocol assumptions. `SetFlag` and `ClearFlag` wrap interlocked operations and expect compatible integral lvalues. `QuadAlign` casts pointers through `ULONG`, which is risky on 64-bit if used with full pointer values. The misspelled `AFS_DIR_ENTRY_CASE_INSENSTIVE_LIST_HEAD` is part of the existing API surface. `GEN_MD5` is only defined under `DBG`, so non-debug conditional code relying on it must be guarded carefully.

## Test Signals
Compile-time tests should cover 32-bit and 64-bit builds, old-WDK compatibility, and all code paths using conditional constants. Runtime signals include worker request dispatch matching expected codes, object/volume reference reason array bounds, write-to-EOF recognition, extent mapping across list-size boundaries, directory enumeration indexes for dot/dot-dot/PIOCtl entries, nonpersistent-cache mode, DFS reparse tag behavior, and flag set/clear operations under contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/Include/AFSDefines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/Include/AFSExtern.h -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/Include/AFSExtern.h

## Purpose
`AFSExtern.h` declares the global objects, function pointers, configuration strings, control flags, cache mapping values, and security helper pointers shared by the OpenAFS Windows redirector kernel library. It is the external-state companion to `AFSCommon.h`.

## Important APIs, Types, And Globals
The header declares global driver/device objects (`AFSLibraryDriverObject`, `AFSLibraryDeviceObject`, `AFSControlDeviceObject`, `AFSRDRDeviceObject`), `AFSFastIoDispatch`, registry and name strings, debug flags and logging callbacks, the cache-manager callback table, system-process handle, global-root volume and special directory entries, the service request function pointer `AFSProcessRequest`, provider connection hook `AFSAddConnectionEx`, pool allocation/free function pointers, auth-group retrieval callback, library control/cache mapping state, security descriptor helper function pointers, `AFSDefaultSD`, `SeWorldSidAuthority`, and `AFSRtlSysVersion`.

## Control Flow And Integration
There is no executable flow, but these globals are dereferenced throughout the library after initialization. `AFSWorker.cpp` relies on control/RDR/library device objects, allocation callbacks, global root, and debug functions. `AFSWrite.cpp` relies on RDR device state, cache-manager callbacks, service request hooks, cache flags, system process identity, and OS version. Generic, create, name, volume, and provider code use the global strings, special share entries, security descriptor state, and pool callbacks.

## State And Persistence
The declarations refer to process/kernel-resident singleton state. Some values mirror persistent configuration, such as registry path, mount root, server/global-root names, library cache base/length, and default security descriptor. Others are runtime-only, including device object pointers, function pointers supplied during library initialization, debug flags, and the current global-root object tree.

## Dependencies And Integration Points
The header is wrapped in `extern "C"` for C linkage from C++ source files. It depends on types defined by Windows kernel headers and OpenAFS local headers, including `AFSVolumeCB`, `AFSDirectoryCB`, service callback typedefs, `FAST_IO_DISPATCH`, `CACHE_MANAGER_CALLBACKS`, and security descriptor/SID types. It is normally pulled in via `AFSCommon.h` unless `NO_EXTERN` is defined.

## Risks And Edge Cases
Global state initialization order is critical. Most implementation files assume these pointers are valid once dispatch paths run; null or stale callback pointers would fail in kernel mode. Function-pointer ABI drift between the library and the hosting redirector/control code is high impact. Because debug/logging/allocation hooks are globals, tests that replace them must restore them carefully. `AFSSysProcess` is compared against process IDs in write paths, so type and lifetime assumptions matter.

## Test Signals
Useful signals include initialization tests proving all required globals and callbacks are populated, negative tests for missing service/allocation/debug callbacks where possible, teardown tests clearing or invalidating globals only after workers stop, link checks with `NO_EXTERN` defining translation units, and runtime smoke tests for writes, workers, security descriptor creation, provider connection calls, and cache-manager callbacks after library initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/Include/AFSExtern.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/Include/AFSStructs.h -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/Include/AFSStructs.h

## Purpose
`AFSStructs.h` defines the core in-memory control blocks for the OpenAFS Windows redirector kernel library: directory headers, worker contexts, CCBs, object-information records, volume records, directory entries, gather I/O state, I/O run descriptors, name arrays, file-info snapshots, work items, directory snapshots, and byte ranges.

## Important APIs, Types, And Structures
Key structures include `AFSDirHdr` for directory B-tree/list coordination, `AFSWorkQueueContext` for worker thread state, `AFSNonPagedCcb` and `AFSCcb` for open-instance state, `AFSNonPagedObjectInfoCB` and `AFSObjectInfoCB` for file/dir metadata and reference tracking, `AFSNonPagedVolumeCB` and `AFSVolumeCB` for volume-level locks/object trees/root objects, `AFSNameInfoCB` and `AFSDirectoryCB` for directory-entry names and links, `AFSGatherIo` and `AFSIoRun` for scatter/gather cache-file I/O, `AFSNameArrayHdr`/`AFSNameArrayCB` for parsed path traversal, `AFSFileInfoCB` for file metadata transfer, `AFSWorkItem` for worker queues, `AFSSnapshotHdr`/`AFSSnapshotEntry` for directory enumeration snapshots, and `AFSByteRange` for extent range lists.

## Control Flow And Integration
The file is declarative, but the structures directly govern runtime flow. Dispatch paths obtain `AFSFcb`/`AFSCcb` pointers from file objects and use `AFSCcb` fields for auth groups, request IDs, full names, directory snapshots, granted access, and unwind metadata. Object and volume management uses embedded tree/list entries plus nonpaged locks. Worker queues pass `AFSWorkItem` unions to `AFSWorkerThread` and `AFSIOWorkerThread`; each `RequestType` selects a different union member. Read/write paths use `AFSGatherIo` and `AFSIoRun` to fan one master IRP into cache-file child I/O.

## State And Persistence
All structures are in-memory kernel state. `AFSObjectInfoCB` mirrors persistent file metadata from the OpenAFS service, including FIDs, target FIDs, expiration, data version, file type, timestamps, attributes, EOF/allocation, EA size, link count, directory child lists, and FCB pointer. `AFSVolumeCB` stores volume metadata and root object state. `AFSCcb` stores per-open state such as enumeration position, path, name array, request ID, granted access, auth group, and file unwind values. `AFSWorkItem` stores transient queued operations and embedded event/status fields for synchronous worker calls.

## Dependencies And Integration Points
The structures depend on b-tree/list primitives, Windows kernel `ERESOURCE`, `KEVENT`, `PIRP`, `PDEVICE_OBJECT`, `FILE_OBJECT`, `UNICODE_STRING`, `GUID`, `LARGE_INTEGER`, access-mask, and OpenAFS protocol types such as `AFSFileID` and `AFSVolumeInfoCB`. They are consumed by nearly every library module, especially worker, write/read, name, object, FCB, volume, extent, directory-control, cleanup, and service communication code.

## Risks And Edge Cases
Because these are shared control blocks, layout changes have broad blast radius. Nonpaged substructures carry resources used at elevated IRQL or while paged portions may not be safe. Reference-count arrays depend on `AFS_OBJECT_REFERENCE_MAX` and `AFS_VOLUME_REFERENCE_MAX`; mismatches corrupt accounting. The `AFSWorkItem` union relies on callers filling the correct member for each request type. Directory-entry lifetime depends on `DirOpenReferenceCount`, `NameArrayReferenceCount`, list/tree membership flags, and object references staying consistent. Many fields are manipulated under specific locks that are not documented in the struct definitions themselves.

## Test Signals
Test signals include special-pool and pool-tag leak detection for each structure tag, reference-count balance tests for object and volume reasons, worker queue union coverage for all request types, directory tree/list insertion and deletion validation, name-array traversal and free/reset paths, gather I/O completion races, directory snapshot enumeration, FCB/CCB open-close cleanup, PIOCtl/share request IDs, and metadata update propagation from service responses into `AFSObjectInfoCB` and `AFSFileInfoCB`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/Include/AFSStructs.h -->
