<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSCleanup.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSCleanup.cpp

## Purpose
`AFSCleanup.cpp` implements `AFSCleanup`, the Windows redirector dispatch handler for `IRP_MJ_CLEANUP`. Cleanup is the point where a file object's user handle is closed but the kernel `IRP_MJ_CLOSE` may occur later. This handler flushes and tears down cache-map state, releases byte-range locks and share access, sends cleanup/delete/flush notifications to the AFS service, updates parent directory data-version state, frees per-open name arrays, updates open-handle counters, and marks the file object with `FO_CLEANUP_COMPLETE`.

## Important APIs, Types, and Functions
- `AFSCleanup(PDEVICE_OBJECT, PIRP)` is the only exported function in the file.
- It works from `IO_STACK_LOCATION`, `FILE_OBJECT`, `AFSFcb` (`FsContext`), and `AFSCcb` (`FsContext2`), then branches on `pFcb->Header.NodeTypeCode`.
- Windows kernel APIs used include `IoGetCurrentIrpStackLocation`, `CcIsFileCached`, `CcFlushCache`, `CcPurgeCacheSection`, `CcUninitializeCacheMap`, `FsRtlFastUnlockAll`, `FsRtlNotifyCleanup`, `IoRemoveShareAccess`, `PsGetCurrentProcessId`, `IoGetRequestorProcess`, `KeQuerySystemTime`, and interlocked reference-count operations.
- AFS service contracts include `AFSFileCleanupCB`, `AFSFileCleanupResultCB`, `AFS_REQUEST_TYPE_CLEANUP_PROCESSING`, and flags such as `AFS_REQUEST_FLAG_FILE_DELETED`, `AFS_REQUEST_FLAG_FLUSH_FILE`, and `AFS_REQUEST_FLAG_BYTE_RANGE_UNLOCK_ALL`.
- State flags include `AFS_FCB_FLAG_FILE_MODIFIED`, `AFS_FCB_FLAG_UPDATE_*_TIME`, `AFS_FCB_FLAG_PURGE_ON_CLOSE`, `AFS_DIR_ENTRY_PENDING_DELETE`, `AFS_DIR_ENTRY_DELETED`, `AFS_DIR_ENTRY_NOT_IN_PARENT_TREE`, and `AFS_OBJECT_FLAGS_VERIFY`.

## Control Flow
The handler exits early for the library control device or a missing FCB. It resolves the object info and parent object info, allocates a page-sized result buffer, initializes `AFSFileCleanupCB` with the process id and file-object identifier, and dispatches by node type.

For `AFS_ROOT_ALL`, cleanup removes directory notifications tied to the CCB and decrements the root-all open-handle count. For `AFS_IOCTL_FCB`, it decrements the parent child-open-handle count and FCB open-handle count. For `AFS_SPECIAL_SHARE_FCB`, it performs only handle-count cleanup.

The file path (`AFS_FILE_FCB`) is the most complex. It acquires the FCB resource and section-object resource, flushes cache for write handles or last-handle cleanup, purges cache sections when this is the last handle or purge-on-close is set, uninitializes the cache map unconditionally, unlocks all local byte-range locks, and marks the service notification as unlock-all. It records time/attribute/allocation updates if the file was modified. If the last open handle is cleaning up a pending-delete directory entry, it releases the FCB resource while calling the service, marks the entry deleted on success, updates or invalidates the parent data version, removes the name entry from the parent tree unless suppressed, emits directory change notification, and deletes extents if the link count reaches zero. Otherwise it flushes dirty extents on write/last-handle cleanup, waits and tears down extents on the last handle, removes share access, frees the CCB name array, calls the service for cleanup processing, and verifies parent data-version consistency.

Directory/root, symbolic-link, mount-point, DFS-link, and invalid-FCB cases share the same pattern without cache-manager file data. They collect metadata updates, handle pending delete through the service and parent tree removal, notify modifications, call cleanup processing, remove notification/share state, free name arrays, decrement parent child-open-handle count, decrement the FCB open-handle count, and release the FCB resource.

The final `try_exit` releases any parent object-info reference, frees the result buffer, sets `FO_CLEANUP_COMPLETE`, and completes the IRP with `AFSCompleteRequest`.

## State and Persistence Behavior
Cleanup mutates in-memory FCB, CCB, object-info, parent-directory, directory-entry, extent, file-object, and notification state. It also pushes durable metadata and delete/flush intent to the user-mode AFS service through `AFSProcessRequest`. Parent directory `DataVersion` is updated when the returned service version is the expected next value; otherwise the parent is flagged `AFS_OBJECT_FLAGS_VERIFY` and its data version is set to `-1` so a later lookup/enumeration revalidates it.

Cache state is explicitly synchronized with the Windows cache manager. Dirty cached data may be flushed by `CcFlushCache`, purged by `CcPurgeCacheSection`, and disconnected by `CcUninitializeCacheMap`. Extent state is flushed/deleted/torn down through `AFSFlushExtents`, `AFSWaitOnQueuedFlushes`, `AFSTearDownFcbExtents`, and `AFSDeleteFcbExtents`. Share access and byte-range locks are removed during cleanup rather than waiting for close, which matches Windows filesystem semantics.

## Dependencies and Integration Points
`AFSCleanup` depends on the redirector globals `AFSRDRDeviceObject` and `AFSControlDeviceObject`, FCB/CCB/object-info lifetime conventions, and the service request channel implemented behind `AFSProcessRequest`. It integrates with directory-tree helpers through `AFSRemoveNameEntry`, notification helpers through `AFSFsRtlNotifyFullReportChange`, extent helpers, name-array helpers, object invalidation, and CCB/FCB reference accounting that is completed later by `AFSClose`.

The function is paired with `AFSClose.cpp`: cleanup decrements `OpenHandleCount` and releases per-handle resources, while close later removes the CCB, decrements `OpenReferenceCount`, and may delete unreferenced directory entries/object-info records.

## Risks and Edge Cases
- Correct lock ordering is critical. The code intentionally releases the FCB resource across service calls for pending delete and normal cleanup to avoid blocking and out-of-order lock acquisition; missed reacquisition or state changes while unlocked are core race risks.
- Cache-manager calls are wrapped in `__try/__except`; exceptions force purge-on-close and later invalidation. Failures in `CcPurgeCacheSection` also preserve purge-on-close for retry/invalidation.
- Several cleanup service failures are logged but converted back to success, especially delete notification failures other than `STATUS_OBJECT_NAME_NOT_FOUND`. This favors local handle cleanup over surfacing remote cleanup errors.
- Parent data-version logic assumes expected version increments. Any concurrent invalidation, re-enumeration, or service-side change forces verify; tests should expect stale entries to be removed or marked for verification rather than blindly trusted.
- Pending-delete removal depends on `pCcb->DirectoryCB` and parent object info. Missing parent object info suppresses tree removal and only logs, leaving later verification to repair state.
- The function assumes handle/reference counts are positive and uses assertions plus interlocked decrements. Counter imbalance between create, cleanup, and close can leave FCBs pinned or trigger assertions.

## Test Signals
Important signals include successful `IRP_MJ_CLEANUP` on read-only files, write handles, cached files, directories, symlinks/mount points, special shares, and PIOCtl nodes; cache flush and purge failure paths; pending delete with and without open child references; parent data-version mismatch forcing `AFS_OBJECT_FLAGS_VERIFY`; dirty extent flush and last-handle teardown; share-mode release; and byte-range unlock-all propagation to the service. Debug traces for FCB/object/dir-entry counts, cache failures, pending delete, and parent version mismatches are the best built-in instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSCleanup.cpp -->
