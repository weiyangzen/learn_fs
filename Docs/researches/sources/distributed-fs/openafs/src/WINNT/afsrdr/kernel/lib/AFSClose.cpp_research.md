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
