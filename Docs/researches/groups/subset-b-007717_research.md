# Research Report: subset-b-007717

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSBTreeSupport.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSBTreeSupport.cpp

## Purpose
`AFSBTreeSupport.cpp` implements the redirector's small in-memory binary-search-tree primitives for directory entries and object hash entries. The file is not a general balanced B-tree implementation despite the name; it maintains unbalanced left/right/parent pointer trees keyed by precomputed CRC or low-file-id hash values. These helpers are used by directory enumeration, lookup, create, delete, close, and object-info indexing paths to find `AFSDirectoryCB` entries by case-sensitive name hash, case-insensitive name hash, DOS short-name hash, and `AFSBTreeEntry` hash.

## Important APIs, Types, and Functions
- `AFSLocateCaseSensitiveDirEntry`, `AFSInsertCaseSensitiveDirEntry`, and `AFSRemoveCaseSensitiveDirEntry` operate on `AFSDirectoryCB::CaseSensitiveTreeEntry`, where `HashIndex` is usually `AFSGenerateCRC(name, FALSE)`.
- `AFSLocateCaseInsensitiveDirEntry`, `AFSInsertCaseInsensitiveDirEntry`, and `AFSRemoveCaseInsensitiveDirEntry` operate on `AFSDirectoryCB::CaseInsensitiveTreeEntry`. Equal case-insensitive hashes are represented as a forward/back list through `AFSDirectoryCB::CaseInsensitiveList`, with the head flagged by `AFS_DIR_ENTRY_CASE_INSENSTIVE_LIST_HEAD`.
- `AFSLocateShortNameDirEntry`, `AFSInsertShortNameDirEntry`, and `AFSRemoveShortNameDirEntry` index optional 8.3 short names through `AFSDirectoryCB::Type.Data.ShortNameTreeEntry`.
- `AFSLocateHashEntry`, `AFSInsertHashEntry`, and `AFSRemoveHashEntry` are type-agnostic tree helpers for `AFSBTreeEntry`, used by volume/object hash trees such as `VolumeCB->ObjectInfoTree.TreeHead`.
- Core structures come from `AFSStructs.h`: `AFSBTreeEntry` carries `HashIndex`, `leftLink`, `rightLink`, and `parentLink`; `AFSDirectoryCB` embeds three tree entries plus list links, name information, object backpointer, and flags.

## Control Flow
All locate functions follow the same search pattern: return `STATUS_INVALID_PARAMETER` if the root is `NULL`, check the root key first, then walk right for greater keys and left for smaller keys until a match or branch end. Case-sensitive and short-name locators initialize the output pointer to `NULL` and otherwise return `STATUS_SUCCESS` even when no entry is found; the generic hash locator starts with `STATUS_NOT_FOUND` and only switches to `STATUS_SUCCESS` on an actual match.

Insert functions require an existing root and walk until a missing child link is found. The inserted node's parent pointer is written to the current node. Duplicate hashes are rejected for case-sensitive, short-name, and generic hash trees. The case-insensitive insert path is different: an equal hash is appended to the same-hash `CaseInsensitiveList`, while only newly inserted tree children are marked as list heads.

Remove functions splice out a node without rebalancing. If the removed node has no children, the parent child pointer or root pointer is cleared. If it has a right child, the right child replaces it at the parent/root. If it also has a left child, the left child is attached to the left-most descendant of the right subtree. If it has only a left child, that child replaces it. The removed node's tree pointers are then cleared. Case-insensitive removal has two extra branches: non-head list entries are removed only from the same-hash list, and a removed list head with a following list entry promotes that following entry into the tree position with the old head's left/right/parent links.

## State and Persistence Behavior
This file mutates only in-memory kernel control blocks. It does not allocate, free, persist, or call the cache manager or service directly. The persistent effect is indirect: these pointer trees determine whether later filesystem operations can find, remove, or verify directory entries and object-info records. Removed nodes have tree/list links nulled to prevent stale parent/child references, but lifetime ownership is handled elsewhere by directory-entry/object-info teardown functions.

The helpers assume callers hold the relevant tree lock. There is no internal synchronization. `AFSCommSupport.cpp`, `AFSCleanup.cpp`, `AFSClose.cpp`, and name-management helpers acquire directory `TreeLock` or volume object-tree locks before manipulating these trees.

## Dependencies and Integration Points
The file includes `AFSCommon.h` for prototypes, flags, debug tracing, and Windows kernel status types. Direct consumers include directory enumeration and verification in `AFSCommSupport.cpp`, name insertion/removal helpers such as `AFSRemoveNameEntry`/`AFSDeleteDirEntry`, and close-time object tree cleanup in `AFSClose.cpp`. The generic hash helpers integrate with object lookup through `AFSCreateLowIndex`, `AFSFindObjectInfo`, and `VolumeCB->ObjectInfoTree`.

The directory helpers are tightly coupled to `AFSDirectoryCB` fields populated by `AFSInitDirEntry` and metadata paths: name CRCs must already be set, `AFS_DIR_ENTRY_INSERTED_SHORT_NAME` must track short-name-tree membership, and `AFS_DIR_ENTRY_NOT_IN_PARENT_TREE` controls whether cleanup/delete code calls name removal.

## Risks and Edge Cases
- The trees are unbalanced. Directory or object insertion patterns with monotonic hash order can degrade lookup, insertion, and removal to linear behavior.
- The case-sensitive and short-name locate APIs return success for "not found" with `*DirEntry == NULL`, while `AFSLocateHashEntry` returns `STATUS_NOT_FOUND`. Callers must not treat status alone as proof of a directory hit.
- Hash collisions are mostly treated as errors. Case-sensitive name CRC collisions and short-name hash collisions can cause insert failures and dropped/rebuilt entries even if the original names differ.
- `AFSRemoveCaseInsensitiveDirEntry` temporarily returns through `try_return(ntStatus)` while `ntStatus` is still initialized to `STATUS_UNSUCCESSFUL` for non-head and promoted-head paths, but `try_exit` overwrites it to `STATUS_SUCCESS`. That relies on the local `try_return` macro routing through cleanup, not a direct return.
- The helpers do not validate that `DirEntry`/`FileIDEntry` belongs to the passed root. Removing a foreign or already-unlinked node can corrupt another tree if callers violate the ownership contract.
- All pointer fields are untyped `void *` links cast back to control-block types, so structure misuse will fail at runtime rather than compile time.

## Test Signals
Useful signals are directory enumeration and lookup behavior under mixed-case names, short-name-enabled/disabled configurations, and deletes/renames that remove tree entries. Tests should exercise root removal, leaf removal, one-child and two-child removal, case-insensitive same-hash chains, short-name collisions, and object-info hash removal on final close. Kernel debug traces for insert/remove collisions and `ASSERT` coverage around tree locks are the main in-tree observability hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSBTreeSupport.cpp -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSClose.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSClose.cpp

## Purpose
`AFSClose.cpp` implements `AFSClose`, the Windows redirector dispatch handler for `IRP_MJ_CLOSE`. Close runs after cleanup when the `FILE_OBJECT` is being destroyed. It detaches `FsContext`/`FsContext2`, removes and frees CCBs, sends close notifications for PIOCtl/service-pipe handles, performs final extent teardown on file FCBs, decrements open-reference counts, and removes deleted directory entries/object-info records when their last references are gone.

## Important APIs, Types, and Functions
- `AFSClose(PDEVICE_OBJECT, PIRP)` is the file's single dispatch routine.
- It branches on `AFSFcb::Header.NodeTypeCode`: `AFS_IOCTL_FCB`, `AFS_ROOT_ALL`, normal file/root/directory/link/mount/DFS/invalid FCBs, and `AFS_SPECIAL_SHARE_FCB`.
- Service close request types include `AFS_REQUEST_TYPE_PIOCTL_CLOSE`; pipe close state is prepared in `AFSPipeOpenCloseRequestCB`, although the special-share case in this file only initializes the structure and cleans up local state.
- Core helpers include `AFSRemoveCcb`, `AFSFindObjectInfo`, `AFSReleaseObjectInfo`, `AFSFlushExtents`, `AFSWaitOnQueuedFlushes`, `AFSTearDownFcbExtents`, `AFSDeleteDirEntry`, `AFSRemoveHashEntry`, and `AFSCompleteRequest`.
- Counted state includes `AFSFcb::OpenReferenceCount`, directory `ChildOpenReferenceCount`, `AFSDirectoryCB::DirOpenReferenceCount`, `NameArrayReferenceCount`, object `ObjectReferenceCount`, and `AFS_OBJECT_INSERTED_HASH_TREE`.

## Control Flow
The handler returns early for the library control device or null FCB. In the PIOCtl path, it acquires the FCB resource, detaches the CCB, sends `AFS_REQUEST_TYPE_PIOCTL_CLOSE` with request/root/parent ids, removes the CCB, decrements the parent child-open-reference count, clears `FsContext`, decrements the FCB open-reference count, and completes the IRP.

For `AFS_ROOT_ALL`, it removes the CCB under the FCB lock, clears the file object's FCB context, and decrements the root open-reference count. For ordinary file/directory/root/link/mount/DFS/invalid nodes, it detaches the CCB, acquires the FCB resource, updates last-access tick count, and if this is the last file reference it marks `AFS_FCB_FILE_CLOSED`, flushes dirty extents, waits for queued flushes, and tears down extents unless direct service I/O changes the path. It then steals the directory-entry pointer from the CCB before removing the CCB, resolves the parent object info, and handles deleted directory entries.

When the associated `AFSDirectoryCB` is flagged `AFS_DIR_ENTRY_DELETED`, close acquires the parent directory tree lock and volume object-info tree lock, decrements `DirOpenReferenceCount`, and if both directory-open and name-array references are gone, deletes the directory entry. If the object info has no remaining object references and is still inserted in the volume hash tree, it removes the object's `TreeEntry` using `AFSRemoveHashEntry` and clears `AFS_OBJECT_INSERTED_HASH_TREE`. Non-deleted entries simply decrement `DirOpenReferenceCount`. The path finally decrements the parent child-open-reference count and the FCB open-reference count.

The special-share path detaches and removes the CCB, decrements parent child-open-reference count and FCB open-reference count, and clears the file object's FCB context. All paths complete the IRP with `AFSCompleteRequest`; exception handling logs and dumps trace files.

## State and Persistence Behavior
Close is mostly in-memory lifetime management. It does not flush cache maps or remove share access because cleanup already handled those operations. Its durable side effects are limited to service close notifications for PIOCtl handles and any extent flush/teardown that still needs to happen on final file close. The major persistent consistency impact is removal of deleted directory entries from parent structures and object-info records from the volume object tree once reference counts permit.

The file deliberately clears `FileObject->FsContext2` before CCB deletion and clears `FsContext` before dropping the FCB open-reference count. It also transfers the directory-entry reference from the CCB into a local `pDirCB` so it can decrement/delete the directory entry after `AFSRemoveCcb` has freed the CCB.

## Dependencies and Integration Points
`AFSClose` depends on cleanup having already performed per-handle resource release. It relies on CCB lists managed by `AFSRemoveCcb`, directory-entry lifetime managed by `AFSDeleteDirEntry`, object-info lifetime in the volume `ObjectInfoTree`, and extent helpers shared with read/write/cleanup paths. It uses `AFSBTreeSupport.cpp` through `AFSRemoveHashEntry` when removing unreferenced object-info records from the volume tree.

The handler is tightly coupled to create/open accounting: `OpenReferenceCount` is decremented here, while `OpenHandleCount` was decremented by cleanup. Parent `ChildOpenReferenceCount` must mirror opens for non-root entries.

## Risks and Edge Cases
- The `AFS_ROOT_ALL` case contains a statement `pIrpSp->FileObject->FsContext2;` rather than an assignment to `NULL`. If intentional, it is a no-op; if not, root-all file objects may retain a stale `FsContext2` after CCB removal.
- Final extent teardown occurs while transitioning out of the last open reference. The code releases the FCB resource before `AFSTearDownFcbExtents` in one branch, so concurrent state must be protected by reference counts and extent locks.
- Deleting a directory entry requires both `DirOpenReferenceCount == 0` and `NameArrayReferenceCount <= 0`. Leaked name-array references will leave deleted entries around until later cleanup.
- Object-info tree removal is guarded by object reference count and `AFS_OBJECT_INSERTED_HASH_TREE`; lock ordering between parent directory tree, volume object tree, and object-info lock is important.
- Special-share close prepares `AFSPipeOpenCloseRequestCB` but does not call `AFSProcessRequest` in the observed code. If service-side pipe close is expected elsewhere, tests should confirm it actually occurs.
- Several paths rely on non-null CCB and directory-entry pointers from `FsContext2`. Unexpected close without cleanup or corrupted contexts can cause exception-path handling rather than graceful failure.

## Test Signals
Close-path tests should track CCB removal, `FsContext`/`FsContext2` clearing, `OpenReferenceCount` and `ChildOpenReferenceCount` decrements, PIOCtl close requests reaching the service, final dirty-extent flush and teardown, deleted directory-entry removal after the last reference, and volume object-tree removal when object references drop to zero. Debug counters and assertions around FCB, object, and directory-entry ref counts are key signals; integration tests should pair cleanup and close under normal, deleted, and final-reference scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSClose.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSCommSupport.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSCommSupport.cpp

## Purpose
`AFSCommSupport.cpp` is the redirector's service-communication and directory-content synchronization layer. It packages kernel-side requests for the user-mode AFS service, consumes service response buffers, and updates in-memory directory, object, volume, file, link, rename, pipe, extent-request, and symlink state. The file is the bridge between Windows filesystem operations and the AFS cache/service process.

## Important APIs, Types, and Functions
- Directory population and verification: `AFSEnumerateDirectory`, `AFSEnumerateDirectoryNoResponse`, and `AFSVerifyDirectoryContent`.
- Metadata and namespace mutations: `AFSNotifyFileCreate`, `AFSUpdateFileInformation`, `AFSNotifyDelete`, `AFSNotifyHardLink`, `AFSNotifyRename`, and `AFSCreateSymlink`.
- Target and volume queries: `AFSEvaluateTargetByID`, `AFSEvaluateTargetByName`, `AFSRetrieveVolumeInformation`, and `AFSRetrieveVolumeSizeInformation`.
- Pipe and special-share operations: `AFSNotifyPipeTransceive`, `AFSNotifySetPipeInfo`, and `AFSNotifyQueryPipeInfo`.
- Miscellaneous communication helpers: `AFSReleaseFid` and `AFSIsExtentRequestQueued`.
- Central dependencies are `AFSProcessRequest`, request types such as `AFS_REQUEST_TYPE_DIR_ENUM`, `CREATE_FILE`, `UPDATE_FILE`, `DELETE_FILE`, `HARDLINK_FILE`, `RENAME_FILE`, `EVAL_TARGET_BY_ID`, `EVAL_TARGET_BY_NAME`, `GET_VOLUME_INFO`, `PIPE_TRANSCEIVE`, `PIPE_SET_INFO`, `PIPE_QUERY_INFO`, `RELEASE_FID`, and `CREATE_SYMLINK`, plus response structures such as `AFSDirEnumResp`, `AFSDirEnumEntry`, `AFSFileCreateResultCB`, `AFSFileHardLinkResultCB`, `AFSFileRenameResultCB`, and `AFSFileEvalResultCB`.

## Control Flow
Directory enumeration allocates an `AFS_DIR_ENUM_BUFFER_LEN` buffer, initializes an `AFSDirQueryCB` with `EnumHandle = 0`, and repeatedly calls `AFSProcessRequest(AFS_REQUEST_TYPE_DIR_ENUM)` until the service returns no more entries. Each response is parsed as `AFSDirEnumResp` followed by variable-length `AFSDirEnumEntry` records. For each entry, the code builds `UNICODE_STRING` views over the inline file and target names, computes the case-sensitive CRC, checks for an existing directory entry, updates metadata when FIDs match, deletes or unlinks stale same-name/different-FID entries, creates a new `AFSDirectoryCB` with `AFSInitDirEntry`, optionally initializes short-name state, inserts into case-sensitive and case-insensitive name trees, appends to the enumeration list, increments the directory node count, and inserts into the short-name tree when applicable. At completion it stores the snapshot data version, marks verify if the snapshot/current versions differ, and sets `AFS_OBJECT_FLAGS_DIRECTORY_ENUMERATED` on success. On failure it resets directory content.

`AFSVerifyDirectoryContent` is a fast synchronous re-enumeration for an already populated directory. It walks service entries, marks matching local entries `AFS_DIR_ENTRY_VALID`, updates object metadata when data versions changed, replaces same-name/different-FID entries, adds new entries, and updates or invalidates the parent directory data version. Unlike initial enumeration, it uses `AFS_REQUEST_FLAG_FAST_REQUEST` and expects the caller to hold the directory tree lock exclusively.

Create, hard-link, and rename helpers all send a synchronous service request, then reconcile returned parent data versions against the local expected version. `AFSNotifyFileCreate` sends `AFS_REQUEST_TYPE_CREATE_FILE` with `AFS_REQUEST_FLAG_HOLD_FID`, handles races with invalidation/re-enumeration by looking up an already-created entry and returning `STATUS_REPARSE` when it matches, creates a new directory entry from the returned `DirEnum`, initializes short-name state, updates the parent data version when safe, and returns the new dir entry with its open-reference count incremented. `AFSNotifyHardLink` builds a variable-length target-name request, updates source and target parent versions, handles target-side race lookup and stale-entry replacement, creates the target dir entry, and optionally returns it with a reference. `AFSNotifyRename` builds a variable-length rename request, updates source and target parent data versions, updates the directory entry's short-name fields from the returned `DirEnum`, and returns an updated FID when requested.

`AFSUpdateFileInformation` sends allocation size, attributes, EA size, and timestamps to the service and updates the object's data version from the response when the object is not already marked for verification. `AFSNotifyDelete` can run in check-only mode; it sends parent id and process id, then either validates the parent version or forces parent verification after delete because the local entry removal is deferred elsewhere.

Target evaluation by id/name allocates a page response, asks the service to resolve a FID or name, validates parent data versions, and can copy the returned `AFSDirEnumEntry` into a caller-owned page buffer. The id path additionally sanity-checks returned FID and file type against the requested object and vnode parity to avoid later type-confusion crashes.

Volume functions are thin synchronous wrappers around `GET_VOLUME_INFO` and `GET_VOLUME_SIZE_INFO`. Pipe functions package CCB request/root ids and user buffers for transceive, set-info, and query-info calls; transceive maps user input/output buffers through MDLs. `AFSReleaseFid` sends a fire-and-forget release request. `AFSIsExtentRequestQueued` scans the communication service request pool under `IrpPoolLock` for a matching `REQUEST_FILE_EXTENTS` request. `AFSCreateSymlink` creates a variable-length symlink request and, on success or `STATUS_FILE_DELETED`, marks the parent for verification and the temporary object as deleted.

## State and Persistence Behavior
The file mutates both local cache state and remote AFS service state. Remote effects include directory enumeration requests, file creation, metadata update, delete validation/notification, hard-link creation, rename, target evaluation, volume information retrieval, pipe I/O, FID release, and symlink creation. Local effects include directory tree/list membership, short-name indexes, object metadata, link/delete flags, data-version tracking, directory enumeration flags, verification flags, open-reference increments for returned directory entries, and queued extent-request introspection.

Data-version reconciliation is the dominant consistency mechanism. When a returned parent version is the expected next version, the local parent is advanced. When the version differs, the code sets `AFS_OBJECT_FLAGS_VERIFY` and usually assigns `DataVersion = -1`, forcing later verification or re-enumeration. Directory enumeration stores snapshot versions and detects changes during enumeration by comparing snapshot and current service data versions.

Memory ownership is explicit. Most service result buffers are page-sized paged-pool allocations freed on exit. Variable-length create/link/rename/symlink/pipe requests allocate enough space for trailing names or data. Target evaluation copies returned dir-enum data into a separate page allocation only when the caller requests it. User pipe buffers are locked with MDLs and unlocked/freed on exit.

## Dependencies and Integration Points
This file depends on `AFSProcessRequest` as the service RPC boundary and on common kernel helpers for pool allocation, MDLs, locks, and debug tracing. It integrates with `AFSBTreeSupport.cpp` for case-sensitive, case-insensitive, short-name, and object hash lookups/inserts; with name/object helpers such as `AFSInitDirEntry`, `AFSDeleteDirEntry`, `AFSRemoveNameEntry`, `AFSUpdateMetaData`, `AFSResetDirectoryContent`, `AFSFindObjectInfo`, and `AFSReleaseObjectInfo`; with device flags such as `AFS_DEVICE_FLAG_DISABLE_SHORTNAMES`; and with the control-device communication service request pool.

Callers are expected to obey locking contracts. Directory enumeration and verification assert or assume exclusive ownership of `ObjectInfoCB->Specific.Directory.DirectoryNodeHdr.TreeLock`. Parent/source/target directory locks are acquired around data-version and tree modifications. Volume object-tree locks are used when verification needs object-info lookup.

## Risks and Edge Cases
- The directory code indexes names primarily by CRC. A case-sensitive CRC collision can cause insert failure or stale-entry replacement behavior even when names are distinct.
- Directory response parsing is sensitive to service-provided lengths and offsets. The code advances by `QuadAlign(sizeof(AFSDirEnumEntry) + FileNameLength + TargetNameLength)`, so malformed lengths can desynchronize parsing if not validated by the service boundary.
- Enumeration and verification assume exclusive tree locks but call `AFSAcquireExcl` again in some completion/version paths; correctness depends on the redirector's resource acquisition semantics.
- Create/hard-link race handling can return `STATUS_REPARSE` when the service created an entry that local invalidation/re-enumeration already installed. Callers must treat that as "use returned existing entry" rather than a conventional reparse point.
- `AFSEvaluateTargetByID` contains explicit type/FID sanity checks because inconsistent service metadata can otherwise lead to BSOD. Similar defensive checks are less visible in the name path.
- Pipe transceive maps user buffers and copies input into a paged-pool request. Failures after locking the first buffer must unwind both MDLs and request allocations correctly; the current `try_exit` handles this but tests should stress partial-failure paths.
- Symlink creation marks the object as deleted after successful creation because the placeholder open object is replaced by the actual symlink. Callers must not continue treating that object info as a normal live node.
- Many functions convert unexpected successful-but-not-`STATUS_SUCCESS` states or service errors into generic device-not-ready or verification states; external callers may see less precise failure causes than the service reported.

## Test Signals
High-value tests include initial directory enumeration, fast verification, concurrent directory mutation during enumeration, same-name/different-FID replacement, short-name enabled/disabled behavior, create races that return `STATUS_REPARSE`, hard link across different parents, rename within and across parents, delete check-only versus real delete, target evaluation with inconsistent FID/type data, volume info retrieval, named-pipe transceive/query/set with buffer overflow and partial failures, queued extent request detection, FID release, and symlink creation/deleted-object behavior. Observable signals are service request types and flags, parent `DataVersion` transitions, `AFS_OBJECT_FLAGS_VERIFY` and `AFS_OBJECT_FLAGS_DIRECTORY_ENUMERATED`, directory node counts, tree insertion/removal traces, and returned `DirOpenReferenceCount` increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSCommSupport.cpp -->
