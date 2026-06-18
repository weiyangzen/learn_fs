# subset-b-007719 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSExtentsSupport.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSExtentsSupport.cpp

## Purpose

`AFSExtentsSupport.cpp` manages the Windows OpenAFS redirector's local file-cache extents for regular file FCBs. It maps file byte ranges to cache offsets, requests missing extents from the user-mode service, accepts extent-map replies, pins extents during read/write I/O, tracks dirty extents after writes, flushes dirty data back to the service, releases cache space under pressure, and trims extent state after truncation or failure.

The module is the bridge between file I/O paths (`AFSRead.cpp`, `AFSWrite.cpp`, close/cleanup/flush code) and the redirector/service communication protocol (`AFS_REQUEST_TYPE_REQUEST_FILE_EXTENTS` and `AFS_REQUEST_TYPE_RELEASE_FILE_EXTENTS`). It is also tightly coupled to `AFSFcbSupport.cpp`, which initializes the per-file extent lists, resources, dirty-list state, and completion events that this file assumes are present on `AFS_FILE_FCB` objects.

## Important APIs, Types, And State

- `AFSExtent` stores one cached byte range: `FileOffset`, `CacheOffset`, `Size`, `Flags`, `ActiveCount`, optional `MD5`, intrusive `Lists[AFS_NUM_EXTENT_LISTS]`, and a separate `DirtyList` link.
- `AFSFcb::Specific.File` supplies the extent skip lists, file lock, `ExtentsDirtyCount`, `ExtentCount`, `QueuedFlushCount`, `ExtentLength` in KB, and file metadata used in release/flush requests.
- `AFSNonPagedFcb::Specific.File` supplies synchronization and event state: `ExtentsResource`, `DirtyExtentsListLock`, `ExtentsRequestComplete`, `FlushEvent`, `QueuedFlushEvent`, `DirtyListHead`, `DirtyListTail`, `ExtentsRequestStatus`, and `ExtentsRequestAuthGroup`.
- `ExtentsMasks` and `AFS_NUM_EXTENT_LISTS` implement a small skip-list-like index. The base list is the full extent list; upper lists contain extents whose offsets satisfy coarser alignment masks.
- Request/release wire structures include `AFSRequestExtentsCB`, `AFSSetFileExtentsCB`, `AFSReleaseExtentsCB`, `AFSReleaseFileExtentsCB`, `AFSReleaseFileExtentsResultCB`, `AFSReleaseFileExtentsResultFileCB`, `AFSFileExtentCB`, and `AFSExtentFailureCB`.
- Public helpers declared in `AFSCommon.h` include `AFSExtentForOffset`, `AFSDoExtentsMapRegion`, `AFSRequestExtentsAsync`, `AFSWaitForExtentMapping`, `AFSProcessSetFileExtents`, `AFSProcessReleaseFileExtents`, `AFSProcessExtentFailure`, `AFSFlushExtents`, `AFSReleaseExtentsWithFlush`, `AFSReleaseCleanExtents`, `AFSMarkDirty`, `AFSTearDownFcbExtents`, `AFSDeleteFcbExtents`, `AFSTrimExtents`, active reference helpers, and dirty-list/byte-range helpers.

## Control Flow

Extent lookup is based on `AFSExtentForOffsetHint`, `AFSEntryForOffset`, `ExtentForOffsetInList`, `AFSExtentContains`, `ExtentFor`, and `NextExtent`. Callers must hold `ExtentsResource`; the code asserts that and then walks upper extent lists down to the base list to find the containing extent or nearest previous extent. `AFSDoExtentsMapRegion` uses those lookups plus adjacency checks to determine whether a requested byte range is fully mapped by contiguous extents.

Read and write paths call `AFSRequestExtentsAsync` when a range is missing. That function first checks any remembered service failure for the same auth group, checks whether the range is already mapped, aligns the request to `CacheBlockSize`, suppresses duplicate queued requests via `AFSIsExtentRequestQueued`, clears `ExtentsRequestComplete`, and sends an asynchronous `AFS_REQUEST_TYPE_REQUEST_FILE_EXTENTS`. If the service denies access for the current CCB auth group, it retries using `AFSRetrieveValidAuthGroup` when that yields a different group.

The service returns extent maps through `AFSProcessSetFileExtents`. This locates the volume by high FID index under `VolumeTreeLock`, references the volume, locates the object by low FID index under the volume object tree lock, references the object, and then either records a canceled extent request on service failure or calls `AFSProcessExtentsResult`. `AFSProcessExtentsResult` holds the file extent resource exclusive, walks the incoming extents in order, inserts new `AFSExtent` records into the base and skip lists, updates per-file and global extent counts/lengths, rejects overlap or size mismatches, trims newly supplied extents on insertion failure, and signals `ExtentsRequestComplete`.

Service-reported failures enter through `AFSProcessExtentFailure`. It validates the IOCTL buffer, resolves the FID to a live FCB, writes `ExtentsRequestStatus` and `ExtentsRequestAuthGroup`, and signals `ExtentsRequestComplete`. `AFSWaitForExtentMapping` waits up to one second on that event, returns stored failures for matching auth groups or the system process, and converts timeout into success so callers can retry/request again without treating the wait as a hard I/O error.

Extent release has multiple paths. `AFSProcessReleaseFileExtents` is the user-mode initiated IOCTL path: it validates buffers, either targets a specific FID or asks `AFSFindFcbToClean` for a candidate file, locks extents, builds a result structure, obtains a valid auth group, populates file metadata, and delegates actual removal to `AFSReleaseSpecifiedExtents`. That helper reports `UNKNOWN` for absent requested extents, `IN_USE` for active requested extents, skips active extents on release-all, removes dirty-list entries when needed, emits `DIRTY` and `RELEASE` flags, and frees released extents.

Driver-initiated cleanup uses `AFSTearDownFcbExtents`, `AFSDeleteFcbExtents`, `AFSFlushExtents`, `AFSReleaseExtentsWithFlush`, and `AFSReleaseCleanExtents`. Teardown releases as many inactive extents as it can and synchronously notifies the service. Delete removes local extents without a service release request. Flush repeatedly removes non-active dirty extents from the dirty list, marks them clean before sending to make concurrent writes re-dirty them, frees their local extent records, and synchronously sends dirty release batches. The release-with-flush and clean-release variants release inactive extents for cache-pressure and close paths, optionally retaining about 1 MB when handles remain open.

Writes call `AFSReferenceActiveExtents` before I/O, optionally `AFSSetupMD5Hash`, and then `AFSMarkDirty` after successful writeback to local cache. `AFSMarkDirty` inserts extents into the ordered dirty list, increments `ExtentsDirtyCount`, sets `AFS_EXTENT_DIRTY`, and can also dereference active extents as part of the write completion path. Plain reads use the active reference/dereference helpers to prevent release while cache pages are being consumed.

Truncation and error cleanup call `AFSTrimExtents` or `AFSTrimSpecifiedExtents`. `AFSTrimExtents` aligns a file size up to the cache block boundary, removes all extents at or beyond that aligned offset, removes dirty-list entries and decrements dirty counts, asserts inactive extents, frees records, and clears `ExtentsRequestStatus`. The specified variant removes only incoming result offsets, primarily after a failed extent-map insertion.

## State And Persistence Behavior

The file maintains volatile kernel-cache state, not durable AFS metadata. The persistent effects are indirect: dirty extent release requests carry file size and timestamp metadata plus dirty/cache/file offsets to the user-mode service, which owns the actual cache backing and server updates. Local extent records are allocated from nonpaged pool, are attached to FCBs, and are discarded on FCB teardown, deletion, cleanup, truncation, cache pressure, or service-directed release.

Important local state transitions include clean extent insertion, active pinning while I/O owns a range, dirty marking after writes, dirty-list removal during flush/release/trim, extent count and KB-length updates on allocation/free, global control-device `ExtentCount` and `ExtentsHeldLength` accounting, and `ExtentsHeldEvent` clear/set when global held extents cross zero. `ExtentsRequestStatus` is used as a one-shot remembered failure keyed by auth group and reset after it is delivered to a matching caller.

The code relies on `ExtentsResource` as the main extent-map lock and `DirtyExtentsListLock` for the dirty-list overlay. Some paths release `ExtentsResource` before synchronous `AFSProcessRequest` calls to avoid holding kernel locks across service round trips; by that point local extent records have already been detached/freed or the path depends on the active/dirty protections documented in the comments.

## Dependencies And Integration Points

- `AFSCommon.h`, `AFSRedirCommonStructs.h`, `AFSUserStructs.h`, and `AFSUserDefines.h` define FCB, extent, IOCTL, request, release, and flag structures.
- `AFSFcbSupport.cpp` initializes `ExtentsResource`, `DirtyExtentsListLock`, events, extent list heads, and dirty-list pointers.
- `AFSRead.cpp` and `AFSWrite.cpp` request/wait for mappings and pin/deref active extents; write also marks dirty and may generate MD5 hashes.
- `AFSDevControl.cpp` dispatches service IOCTLs to `AFSProcessSetFileExtents` and `AFSProcessReleaseFileExtents`.
- `AFSClose.cpp`, `AFSCleanup.cpp`, `AFSFlushBuffers.cpp`, `AFSGeneric.cpp`, `AFSFileInfo.cpp`, and `AFSWorker.cpp` flush, release, or trim extents during close, cleanup, purge, truncation, cache pressure, and worker processing.
- `AFSProcessRequest`, `AFSIsExtentRequestQueued`, `AFSRetrieveValidAuthGroup`, `AFSLocateHashEntry`, `AFSVolumeIncrement/Decrement`, and `AFSObjectInfoIncrement/Decrement` provide service communication and lifetime pinning.
- Cache access for MD5 can use `AFSLibCacheBaseAddress` for nonpersistent cache or `AFSReadCacheFile` for file-backed cache.

## Risks And Edge Cases

- The skip-list implementation is manual and intrusive. Any missed list removal, duplicate insertion, incorrect mask condition, or stale cursor can corrupt the extent index.
- Several functions require callers to hold `ExtentsResource`, and some require exclusive ownership; misuse from other modules can race free/insertion against read/write pinning.
- Active extents are protected only by `ActiveCount` discipline. Missed dereferences leak cache space; missed references allow release while I/O is still using the cache range.
- `AFSFlushExtents` clears `AFS_EXTENT_DIRTY` before the synchronous service request and frees the extent regardless of service status. The comments state the extent is considered released even on request failure, but this makes error reporting and cache coherency highly dependent on service semantics.
- Buffer-size calculations mix fixed header offsets, variable arrays, and `ExtentCount`; off-by-one or integer overflow bugs would affect kernel IOCTL safety.
- `AFSFindFcbToClean` walks volume/object lists while taking and releasing locks to avoid deadlock. It depends on volume/object references to keep nodes stable and skips open handles/queued flushes.
- `AFSTrimExtents` dereferences `FileSize` after a null check path; practical callers appear to pass a size, but the local code would be unsafe if `NULL` reached the `0 == FileSize->QuadPart` branch.
- Auth-group fallback and remembered failure handling are subtle: failures are delivered only to matching auth groups or system process paths, and status is reset after delivery.
- Optional `GEN_MD5` code allocates temporary buffers and reads cache contents while holding the extents resource shared; partial writes and allocation tag mismatch during free should be reviewed if MD5 is enabled.

## Test Signals

- Read/write tests where requested byte ranges are already fully mapped, partially mapped with a gap, and completely unmapped; assert aligned service requests and eventual mapping.
- Service reply tests for ordered extents, duplicate extents, overlapping extents, mismatched lengths, empty extent lists, and failure result statuses.
- Concurrent I/O and cache-pressure tests proving active extents return `IN_USE` or are skipped, and that dereference paths eventually allow release.
- Dirty write/flush tests checking dirty-list ordering, `ExtentsDirtyCount`, release flags, metadata fields, `FlushEvent`, `QueuedFlushEvent`, and re-dirty behavior during concurrent writes.
- Truncation tests covering exact cache-block boundaries and unaligned sizes, ensuring later extents and dirty-list entries are removed without touching earlier valid ranges.
- Service IOCTL fuzz tests for too-small input/output buffers, zero `ExtentCount`, unknown FIDs, missing FCBs, release-all requests, and output `IoStatus.Information`.
- Auth tests for access-denied retry with alternate auth group and remembered failure delivery to the same CCB auth group.
- Cache accounting tests for per-FCB `ExtentCount`/`ExtentLength`, control-device global `ExtentCount`/`ExtentsHeldLength`, and `ExtentsHeldEvent`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSExtentsSupport.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSFSControl.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSFSControl.cpp

## Purpose

`AFSFSControl.cpp` handles IRP major file-system-control requests for the OpenAFS Windows redirector library device. It dispatches user FSCTLs, implements reparse-point query/set/delete behavior for OpenAFS symlinks, mount points, and DFS links, and routes special IPC share FSCTLs to the redirector notification pipe. Most generic volume and oplock FSCTLs are explicitly unsupported or invalid for this redirector layer.

## Important APIs, Types, And State

- `AFSFSControl` is the IRP entry point for `IRP_MN_USER_FS_REQUEST`, `IRP_MN_MOUNT_VOLUME`, and `IRP_MN_VERIFY_VOLUME`.
- `AFSProcessUserFsRequest` handles per-file FSCTL dispatch after extracting `AFSFcb` and `AFSCcb` from the file object contexts.
- `AFSProcessShareFsCtrl` handles FSCTLs issued against `AFS_SPECIAL_SHARE_FCB`, currently `FSCTL_PIPE_TRANSCEIVE`.
- `AFSParseMountPointTarget` parses OpenAFS mount target strings of form `<type>[<cell>:]<volume>`.
- Reparse data structures include Microsoft `REPARSE_DATA_BUFFER`, `REPARSE_GUID_DATA_BUFFER`, OpenAFS `AFSReparseTagInfo`, `GUID_AFS_REPARSE_GUID`, `IO_REPARSE_TAG_OPENAFS_DFS`, and subtags `OPENAFS_SUBTAG_MOUNTPOINT`, `OPENAFS_SUBTAG_SYMLINK`, and `OPENAFS_SUBTAG_UNC`.
- Runtime state comes from `pCcb->DirectoryCB->NameInformation`, `pFcb->ObjectInformation`, directory nonpaged locks, auth groups, object-info trees, and volume metadata.

## Control Flow

`AFSFSControl` obtains the current IRP stack location, switches on the minor function, calls `AFSProcessUserFsRequest` for `IRP_MN_USER_FS_REQUEST`, then completes the IRP with `AFSCompleteRequest`. Exceptions are caught through `AFSExceptionFilter`, traced, and dumped.

`AFSProcessUserFsRequest` validates that the file object has an FCB, CCB, and directory entry. Special share FCBs are delegated to `AFSProcessShareFsCtrl`. Normal requests then switch on `FsControlCode`. Oplock requests, volume lock/unlock/dismount/dirty/mounted queries, and CSC internal requests return not implemented or invalid. `FSCTL_IS_PATHNAME_VALID` succeeds, and `FSCTL_SET_PURGE_FAILURE_MODE` is accepted as a no-op success.

For `FSCTL_GET_REPARSE_POINT`, the code first checks `FILE_ATTRIBUTE_REPARSE_POINT`, verifies that the output buffer can hold the appropriate Microsoft or GUID reparse header, and locks the directory entry. If `TargetName` is not cached, it invalidates data version, sets object verify state, and calls `AFSVerifyEntry` to populate metadata. It then serializes by file type:

- `AFS_FILE_TYPE_SYMLINK` emits `IO_REPARSE_TAG_SYMLINK`. Relative targets use `SYMLINK_FLAG_RELATIVE` with one path string. Absolute targets generate a display name prefixed with `\` and a substitute name prefixed with `\??\UNC`.
- `AFS_FILE_TYPE_MOUNTPOINT` emits an OpenAFS GUID reparse buffer with `IO_REPARSE_TAG_SURROGATE | IO_REPARSE_TAG_OPENAFS_DFS`, copies `GUID_AFS_REPARSE_GUID`, and stores mount-point type, cell length, volume length, and packed cell/volume buffers.
- `AFS_FILE_TYPE_DFSLINK` emits a Microsoft symlink reparse buffer. It treats targets beginning with `\` as relative, drive-letter targets as `\??\` substitute paths, and other targets similarly to UNC-like absolute names.

For `FSCTL_SET_REPARSE_POINT`, the function validates either OpenAFS GUID-tagged data or Microsoft symlink data. OpenAFS symlink and UNC subtags become `uniTargetName`; mount-point setting is rejected as not handled. Microsoft mount points are traced but rejected, while Microsoft symlinks use the substitute name. After validation, the code resolves and references the parent `AFSObjectInfoCB` under the volume object-info tree, then calls `AFSCreateSymlink` with the CCB auth group, parent object, current file name, current object, and target. It decrements the parent object reference afterward.

For `FSCTL_DELETE_REPARSE_POINT`, the code validates that the object is a reparse point and that the input is an OpenAFS GUID reparse tag with the expected GUID. It then returns success without directly changing metadata because the expected caller pattern is delete-on-close after opening the reparse point.

`AFSProcessShareFsCtrl` handles `FSCTL_PIPE_TRANSCEIVE` by passing the CCB, input/output lengths, type-3 input buffer, user output buffer, and returned byte count to `AFSNotifyPipeTransceive`. Unknown share FSCTLs are printed but otherwise leave the default success status unchanged.

## State And Persistence Behavior

This file does not directly persist metadata except through delegated service/object operations. `FSCTL_GET_REPARSE_POINT` can force metadata verification and updates cached `TargetName`/object state through `AFSVerifyEntry`. `FSCTL_SET_REPARSE_POINT` creates or updates symlink metadata through `AFSCreateSymlink`, using parent object references to keep the parent alive during the call. `FSCTL_DELETE_REPARSE_POINT` intentionally does not remove the reparse metadata itself.

IRP-visible output state is written through `Irp->AssociatedIrp.SystemBuffer`, `Irp->UserBuffer` for pipe transceive, and `Irp->IoStatus.Information`. Locking is localized to directory entry locks for target-name access and object-info tree locks for parent lookup/reference.

## Dependencies And Integration Points

- IRP dispatch and completion rely on Windows kernel I/O manager structures and `AFSCompleteRequest`.
- Reparse serialization depends on Windows `REPARSE_DATA_BUFFER`, `REPARSE_GUID_DATA_BUFFER`, `IO_REPARSE_TAG_SYMLINK`, `IO_REPARSE_TAG_MOUNT_POINT`, and OpenAFS GUID/tag definitions.
- `AFSVerifyEntry`, `AFSCreateSymlink`, `AFSIsRelativeName`, `AFSCreateLowIndex`, `AFSLocateHashEntry`, `AFSObjectInfoIncrement/Decrement`, and directory/volume locks connect FSCTL handling to the redirector metadata cache and user-mode service.
- `AFSNotifyPipeTransceive` integrates special `IPC$` share file controls with the notification pipe subsystem.
- `AFSFcbSupport.cpp` provides the FCB/CCB shapes and node type codes used to dispatch normal vs special-share requests.

## Risks And Edge Cases

- Reparse buffer length accounting is security-sensitive because the code writes variable packed paths directly into caller buffers.
- `AFSParseMountPointTarget` assumes the target buffer has at least one character for the type and computes lengths in bytes; malformed short strings can stress boundary conditions.
- Absolute symlink/DFS target conversion manually constructs `\??\UNC` or `\??\` substitute names; path-prefix mistakes can change Windows reparse semantics.
- `FSCTL_SET_REPARSE_POINT` accepts Microsoft symlink substitute names but rejects mount points and OpenAFS mount-point subtags, so callers may see asymmetric get/set behavior.
- Parent object lookup uses the current object's `ParentFileId`; races with rename/delete are mitigated by object references but should be considered around `AFSCreateSymlink`.
- Unknown `AFSProcessShareFsCtrl` operations currently return success unless the callee changes status, which may hide unsupported IPC FSCTL usage.
- The top-level exception path traces and dumps but still returns the current `ntStatus`; callers depend on request completion already happening inside the protected block.

## Test Signals

- FSCTL dispatch tests for invalid FCB/CCB/directory context, special-share delegation, unsupported oplock/volume controls, `FSCTL_IS_PATHNAME_VALID`, and CSC internal behavior.
- Reparse get tests for symlink relative targets, symlink absolute targets, mount points with and without cells, DFS links beginning with slash, DFS drive-letter links, and DFS UNC-like targets.
- Buffer-size tests for all reparse variants, asserting `STATUS_BUFFER_TOO_SMALL` and `IoStatus.Information` values.
- Metadata refresh tests where `TargetName` is empty and `AFSVerifyEntry` succeeds or fails.
- Reparse set tests for OpenAFS GUID mismatch, invalid subtags, truncated variable buffers, Microsoft symlink parsing, rejected Microsoft mount points, parent volume/object lookup failure, and `AFSCreateSymlink` failure.
- Delete-reparse tests for non-reparse objects, tag mismatch, GUID conflict, short input buffer, and success without immediate metadata deletion.
- IPC pipe tests for `FSCTL_PIPE_TRANSCEIVE` input/output byte counts and error propagation from `AFSNotifyPipeTransceive`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSFSControl.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSFcbSupport.cpp -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSFcbSupport.cpp -->
