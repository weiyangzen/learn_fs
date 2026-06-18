# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSFcbSupport.cpp

## Purpose

`AFSFcbSupport.cpp` owns allocation, initialization, insertion, and teardown for file control blocks (`AFSFcb`) and context control blocks (`AFSCcb`) in the OpenAFS Windows redirector library. It binds cached object metadata (`AFSObjectInfoCB`/`AFSDirectoryCB`) to Windows `FSRTL_ADVANCED_FCB_HEADER` state, initializes resources and file locks, sets file-type-specific FCB node codes, prepares per-file extent state, and tracks per-open CCBs in each FCB.

## Important APIs, Types, And State

- `AFSInitFcb` creates or races to an FCB for a non-root directory/object entry and returns with the selected FCB resource held exclusive.
- `AFSInitRootFcb` creates the root volume FCB and stores it in `VolumeCB->ObjectInformation.Fcb` and `VolumeCB->RootFcb`.
- `AFSRemoveRootFcb` tears down the volume root FCB.
- `AFSRemoveFcb` tears down non-root FCBs.
- `AFSInitCcb` creates a per-open CCB, attaches it to an `AFSDirectoryCB`, records granted access/file access, and increments the directory open reference count.
- `AFSInsertCcb` appends a CCB to an FCB's CCB list and sets `CCB_FLAG_INSERTED_CCB_LIST`.
- `AFSRemoveCcb` removes a CCB from the FCB list, frees open-specific names/snapshots/masks, decrements directory open references, deletes the nonpaged CCB lock, and frees the CCB.
- Important resources include `AFSNonPagedFcb::Resource`, `PagingResource`, `SectionObjectResource`, `CcbListLock`, file `ExtentsResource`, file `DirtyExtentsListLock`, and `AFSNonPagedCcb::CcbLock`.

## Control Flow

`AFSInitFcb` first checks whether the object already has an FCB. If so, it acquires that FCB's main resource exclusive and returns success. Otherwise it allocates paged `AFSFcb` and nonpaged `AFSNonPagedFcb`, zeros them, initializes the advanced FSRTL header, initializes ERESOURCE locks, acquires the new FCB resource exclusive, and attaches the nonpaged resources to the header.

The function then maps `pObjectInfo->FileType` to an FCB node type. Directories become `AFS_DIRECTORY_FCB`; regular files become `AFS_FILE_FCB`; special share names, pioctl objects, symlinks, mount points, and DFS links become their corresponding special node codes; unknown types become `AFS_INVALID_FCB`. For regular files it initializes `FILE_LOCK`, copies allocation/file/valid-data sizes from object info, initializes extent resources/events, initializes all extent list heads, clears dirty-list head/tail, and creates flush/queued-flush events.

After initialization, `AFSInitFcb` stores `pFcb->ObjectInformation` and uses `InterlockedCompareExchangePointer` under the object-info lock to publish the FCB only if none exists. If another thread won the race, it releases the new object's locks, acquires the winner's resource exclusive, returns `STATUS_REPARSE`, and frees the losing allocation in cleanup. On allocation or setup failure it tears down any initialized FSRTL context, file lock, extents resources, generic resources, and pools.

`AFSInitRootFcb` follows the same pattern for the volume root, with node type `AFS_ROOT_FCB`, no file-specific extent state, `ObjectInformation` pointing to the volume's object info, and `VolumeCB->RootFcb` set after successful publication. Race cleanup also returns `STATUS_REPARSE` after acquiring the existing root FCB resource.

`AFSRemoveRootFcb` and `AFSRemoveFcb` use `InterlockedCompareExchangePointer` to detach the FCB pointer, then tear down resources and free pools. Non-root file FCB teardown additionally uninitializes `FILE_LOCK` and deletes extent/dirty extent resources. Both remove FSRTL per-stream contexts before freeing the nonpaged and paged FCB allocations.

`AFSInitCcb` allocates paged `AFSCcb` and nonpaged `AFSNonPagedCcb`, initializes `CcbLock`, stores the directory entry and access masks, increments `DirectoryCB->DirOpenReferenceCount`, and returns the CCB. Failure frees partially allocated memory and clears the output pointer.

`AFSInsertCcb` holds the FCB CCB-list lock and the CCB lock, appends to the doubly linked CCB list using `CcbListHead`/`CcbListTail`, and marks the CCB inserted. `AFSRemoveCcb` holds the CCB lock, unlinks from the FCB list if inserted, frees optional per-open buffers (`MaskName`, `FullFileName`, `NameArray`, `DirectorySnapshot`, `NotifyMask`), decrements the directory open reference count, releases/deletes the CCB lock, and frees both CCB allocations.

## State And Persistence Behavior

This file manages in-memory kernel object lifetime only. It does not write durable AFS metadata. Its persistent effect is to make object metadata reachable through Windows FCB/CCB structures while a file object or volume is open.

The key state transitions are object-info `Fcb` publication/removal, `VolumeCB->RootFcb` publication/removal, resource initialization/deletion, FSRTL header setup/teardown, file size initialization from cached object information, per-file extent state initialization, CCB list membership, and `DirOpenReferenceCount` increments/decrements. Successful init functions return with FCB resources held exclusive, making lock ownership part of their API contract.

## Dependencies And Integration Points

- Windows FSRTL and executive primitives: `FSRTL_ADVANCED_FCB_HEADER`, `FsRtlSetupAdvancedHeader`, `FsRtlTeardownPerStreamContexts`, `FsRtlInitializeFileLock`, `FsRtlUninitializeFileLock`, `ExInitializeResourceLite`, `ExDeleteResourceLite`, `ExInitializeFastMutex`, `KEVENT`, and interlocked pointer/count operations.
- OpenAFS allocation and tracing helpers: `AFSExAllocatePoolWithTag`, `AFSExFreePoolWithTag`, `AFSDbgTrace`, and allocation tags.
- OpenAFS metadata objects: `AFSDirectoryCB`, `AFSObjectInfoCB`, `AFSVolumeCB`, object-info locks, file type codes, file IDs, and cached size/timestamp fields.
- `AFSExtentsSupport.cpp` depends on file-FCB extent resources, events, list heads, dirty-list pointers, and counts initialized here.
- Create/open, cleanup, close, directory control, FS control, read/write, and notify paths depend on CCB allocation/listing and FCB node-type classification.

## Risks And Edge Cases

- The initialization race path returns `STATUS_REPARSE` while holding the existing FCB resource, so callers must treat that status as a usable existing FCB rather than a normal failure.
- `AFSRemoveRootFcb` and `AFSRemoveFcb` use compare-exchange on pointer fields; the exact expected pointer expression must remain correct or removal could fail or detach incorrectly.
- Successful `AFSInitFcb`/`AFSInitRootFcb` intentionally leave the FCB main resource acquired. Missing release by callers will deadlock later operations.
- File FCB teardown assumes no live extents or users remain; callers must flush/delete extents and drain I/O before removal.
- CCB list unlinking is manual. Corrupted forward/back links or missed `CCB_FLAG_INSERTED_CCB_LIST` handling can leave dangling CCB list pointers in the FCB.
- Optional CCB buffers are freed by flag/tag conventions. Ownership of `FullFileName.Buffer` depends on `CCB_FLAG_FREE_FULL_PATHNAME`; incorrect flagging can leak or double-free.
- `AFSInitCcb` initializes `CcbLock` but its failure path frees the nonpaged CCB without deleting the resource if a later failure is added after initialization; current code has no later failure, but future edits should preserve cleanup symmetry.

## Test Signals

- FCB creation tests for every `FileType` mapping, including regular files, directories, special share names, pioctl, symlink, mount point, DFS link, and invalid types.
- Race tests where two threads call `AFSInitFcb` or `AFSInitRootFcb` for the same object and only one FCB is published while the loser frees its allocation.
- Lock-contract tests proving successful init returns with the selected FCB resource held exclusive and teardown occurs only after release/drain.
- File FCB initialization tests checking FSRTL size fields, file lock initialization, extent list heads, dirty-list pointers, request-complete event initial state, flush events, and resource initialization.
- Teardown tests for root and non-root FCBs verifying object pointers are cleared, resources are deleted, per-stream contexts are torn down, file locks are uninitialized for regular files, and pools are freed once.
- CCB lifecycle tests checking directory open reference counts, granted/file access fields, list insertion/removal at head/middle/tail, optional buffer cleanup, name-array/snapshot cleanup, and notify-mask cleanup.
- Fault-injection tests for allocation failures in FCB, nonpaged FCB, CCB, and nonpaged CCB paths.
