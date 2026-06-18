# Research: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSGeneric.cpp

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007721`: lines 1-8315, `Docs/researches/chunks/subset-b-007721_research.md`
- `subset-b-007722`: lines 8316-10150, `Docs/researches/chunks/subset-b-007722_research.md`

## Chunk Research

### subset-b-007721: lines 1-8315

# `sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSGeneric.cpp` lines 1-8315

## Purpose

This chunk is the main generic support layer for the Windows AFS redirector library. It provides kernel-safe wrappers around allocation, exception logging, `ERESOURCE` locking, IRP buffer mapping, request completion, CRC/name helpers, and callback wiring. It also owns a large part of redirector runtime state management: global root/special share directory entries, directory entry and object-info allocation, metadata validation, cache invalidation, volume/network state changes, root-entry reparse resolution, FCB cache cleanup, authentication ID lookup, and library initialization/shutdown.

The chunk ends at the start of `AFSGetObjectStatus`; that function's body continues after line 8315 and should be covered by the next chunk.

## Important APIs, Types, And Functions

- Utility wrappers:
  - `AFSExceptionFilter` logs exception records/context, optionally bugchecks via `AFS_DBG_BUGCHECK_EXCEPTION`, otherwise breaks into the debugger.
  - `AFSLibExAllocatePoolWithTag` allocates library-lifetime pool and centralizes allocation failure behavior.
  - `AFSAcquireExcl`, `AFSAcquireSharedStarveExclusive`, `AFSAcquireShared`, `AFSReleaseResource`, and `AFSConvertToShared` wrap `ERESOURCE` calls with critical-region handling and trace logging.
  - `AFSCompleteRequest`, `AFSGenerateCRC`, `AFSIsEqualFID`, `AFSCreateHighIndex`, `AFSCreateLowIndex`, `AFSIsRelativeName`, `AFSIsAbsoluteAFSName`, `AFSUpdateName`, and `AFSDefaultLogMsg` are cross-cutting helpers.

- IRP and buffer helpers:
  - `AFSLockSystemBuffer` resolves an IRP buffer from an existing MDL, system buffer, or user buffer; if needed it allocates/probes/locks an MDL.
  - `AFSLockUserBuffer` locks an arbitrary caller buffer and returns its system address plus MDL.
  - `AFSMapToService` maps a locked IRP buffer into the service process address space.
  - `AFSUnmapServiceMappedBuffer` unmaps that service-process mapping.
  - `AFSReadCacheFile` builds a synchronous read IRP against the shared cache file object and waits through `AFSIrpComplete`.
  - `AFSReferenceCacheFileObject` and `AFSReleaseCacheFileObject` protect `Specific.RDR.CacheFileObject` with `CacheFileLock` and object references.

- Directory/object lifecycle:
  - `AFSInitializeGlobalDirectoryEntries` constructs fake global `.` and `..` entries.
  - `AFSInitDirEntry` creates or finds an `AFSObjectInfoCB`, copies service-provided metadata from `AFSDirEnumEntry`, allocates the `AFSDirectoryCB` plus nonpaged lock block, stores name/target strings, and computes case-sensitive/case-insensitive name hashes.
  - `AFSInitPIOCtlDirectoryCB` installs a fake hidden/system pioctl entry with `InterlockedCompareExchangePointer` to handle races.
  - `AFSAllocateObjectInfo`, `AFSObjectInfoIncrement`, `AFSObjectInfoDecrement`, `AFSFindObjectInfo`, `AFSReleaseObjectInfo`, and `AFSDeleteObjectInfo` manage `AFSObjectInfoCB` lifetimes, object trees, volume lists, parent-child references, and service-held FIDs.
  - `AFSRemoveNameEntry`, `AFSResetDirectoryContent`, `AFSUpdateDirEntryName`, `AFSIsDirectoryEmptyForDelete`, and debug-only `AFSValidateDirList` maintain directory trees/lists.

- Validation and metadata:
  - `AFSEvaluateNode`, `AFSValidateSymLink`, `AFSVerifyEntry`, `AFSValidateEntry`, and `AFSUpdateMetaData` refresh metadata through `AFSEvaluateTargetByID` and update object flags, file type, target FID/name, sizes, timestamps, attributes, EA size, links, expiration, and data version.
  - `AFSValidateDirectoryCache` revalidates enumerated directory contents by clearing valid bits, calling `AFSVerifyDirectoryContent`, rebuilding short-name trees, deleting unreferenced stale entries, and marking referenced stale entries deleted.
  - `AFSRetrieveFileAttributes` resolves a symlink/DFS/mount target path and returns attributes/sizes/timestamps from the located target entry.
  - `AFSEvaluateRootEntry` resolves a root-like reparse target into a final `AFSDirectoryCB`.

- Invalidation and cleanup:
  - `AFSInvalidateCache` dispatches file/volume invalidation requests from a file ID and reason.
  - `AFSInvalidateObject` applies object-level invalidation: deleted, flushed, data-version, credential, callback, and expiration cases.
  - `AFSInvalidateVolume` and `AFSInvalidateAllVolumes` walk volume objects and apply invalidation with temporary references.
  - `AFSCleanupFcb` flushes/purges cache-manager sections and AFS extent cache state during normal cleanup, forced cleanup, and redirector shutdown.
  - `AFSWaitOnQueuedFlushes` and `AFSWaitOnQueuedReleases` block on extent queue events.

- Global service/library integration:
  - `AFSInitializeLibraryDevice` initializes the pioctl and global-root share names.
  - `AFSGetDriverStatus` reports not-ready/no-service/ready from global root and service IRP pool state.
  - `AFSSetVolumeState` toggles a volume offline flag.
  - `AFSSetNetworkState` toggles the global root offline flag.
  - `AFSSubstituteSysName` and `AFSSubstituteNameInPath` implement `@SYS` substitution using 32-bit or 64-bit per-process sysname lists.
  - `AFSInitializeSpecialShareNameList` and `AFSGetSpecialShareNameEntry` build and search fake `PIPE` and `IPC$` share entries.
  - `AFSEnumerateGlobalRoot` enumerates global root shares and registers UNC connections with `AFSAddConnectionEx`.
  - `AFSInitializeLibrary` installs framework callbacks, initializes timing knobs, creates the global root volume/FCB, marks it `AFS_ROOT_ALL`, invalidates prior volumes, and releases startup references/locks.
  - `AFSCloseLibrary` frees global fake directory entries and special-share entries.

- Security/authentication:
  - `AFSGetAuthenticationId` queues a synchronous worker request to retrieve the caller auth ID without doing token work inline.
  - `AFSPerformGetAuthId` references an impersonation token or primary token, queries `TokenStatistics`, copies `AuthenticationId`, and dereferences/frees token resources.
  - `AFSCheckForReadOnlyAccess` and `AFSCheckAccess` implement a coarse read-only-versus-write access filter.

## Control Flow And State Behavior

- Object discovery and allocation are keyed by AFS FIDs. Volume lookup uses `Cell:Volume` (`AFSCreateHighIndex`), while per-volume objects use `Vnode:Unique` (`AFSCreateLowIndex`). Directory entries point to object-info blocks, and object-info blocks are inserted into a per-volume hash tree/list only when a nonzero hash index is supplied.
- Reference counts are reason-coded. `AFSObjectInfoIncrement` upgrades to exclusive locking when transitioning from zero references, while `AFSObjectInfoDecrement` similarly serializes the transition to zero. Deletion asserts zero references, unlinks from hash/list structures, releases the parent child-reference, deletes resources, frees paged/nonpaged blocks, and calls `AFSReleaseFid` if the service held the object.
- Directory cache validation is a two-pass state machine. First pass clears `AFS_DIR_ENTRY_VALID` on non-fake entries and removes stale short-name links. `AFSVerifyDirectoryContent` then repopulates/marks valid entries. Final pass reinserts valid short names and removes or tombstones entries still invalid, based on open/name-array references.
- Metadata validation is expiration/data-version driven. If an object is not marked `NOT_EVALUATED`, `VERIFY`, or `VERIFY_DATA`, and its expiration is still in the future, `AFSValidateEntry` returns without service I/O. Otherwise it evaluates the target, updates metadata for non-file nodes, and for files coordinates section-cache flush/purge and extent flushing before deciding whether metadata can be safely advanced.
- File cache invalidation/verification paths coordinate three caches: the Windows cache manager's section objects (`CcFlushCache`, `CcPurgeCacheSection`, `CcSetFileSizes`), the FCB header size fields, and the redirector's extent cache (`AFSFlushExtents`, `AFSTearDownFcbExtents`, `AFSReleaseExtentsWithFlush`). Failures generally leave `AFS_FCB_FLAG_PURGE_ON_CLOSE` or `AFS_OBJECT_FLAGS_VERIFY_DATA` so later close/validation can retry.
- Reparse-style target resolution normalizes `/` to `\`, supports relative targets by combining with the parent path, supports absolute `\afs\...`-style paths by stripping the server component when appropriate, builds a name array, calls `AFSLocateNameEntry`, and carefully transfers volume/directory references returned by the locator.
- Library initialization is callback-driven. `AFSInitializeLibrary` stores device objects, server/mount root names, debug flags, memory callbacks, request/log/auth callbacks, connection-registration callback, trace-dump callback, and cache-manager callbacks from `AFSLibraryInitCB`. It also supports a nonpersistent cache base/length passed from the framework.

## Dependencies And Integration Points

- Windows kernel APIs: pool allocation, MDLs, `MmProbeAndLockPages`, process attach/detach, `MmMapLockedPagesSpecifyCache`, IRP allocation/completion, `ERESOURCE`, `KeWaitForSingleObject`, security tokens, object references, cache manager APIs, Unicode string/hash helpers, and structured exception handling.
- Redirector globals and device extensions: `AFSControlDeviceObject`, `AFSRDRDeviceObject`, `AFSGlobalRoot`, `AFSServerName`, `AFSMountRootName`, `AFSDebugFlags`, `AFSLibControlFlags`, and `AFSSpecialShareNames`.
- Framework callbacks supplied at initialization: `AFSProcessRequest`, `AFSDbgLogMsg`/`AFSDebugTraceFnc`, `AFSAddConnectionEx`, `AFSExAllocatePoolWithTag`, `AFSExFreePoolWithTag`, `AFSDumpTraceFilesFnc`, `AFSRetrieveAuthGroupFnc`, and cache-manager callbacks.
- Other redirector subsystems called from this chunk: volume initialization/reference handling, root FCB initialization, directory enumeration/name lookup, name-array helpers, directory tree insertion/removal, short-name tree handling, FsRtl change notification, extent cache flushing/teardown, invalidate-object worker queueing, service target evaluation, auth group retrieval, worker queue processing, and DFS target file-info lookup.

## Risks And Edge Cases

- Lock ordering is critical. Several paths acquire object-tree, directory-tree, FCB, and section-object resources; regressions can deadlock because many calls deliberately release tree locks before invalidating or locating child entries.
- `AFSMapToService` depends on `Specific.Control.ServiceProcess` remaining valid while attaching and mapping. A missing service returns no mapping; callers must handle `NULL`.
- Buffer/target-name ownership is flag-based (`AFS_DIR_RELEASE_TARGET_NAME_BUFFER`, `AFS_DIR_RELEASE_NAME_BUFFER`). Updating names without respecting these flags can leak or double-free embedded versus separately allocated buffers.
- `AFSValidateEntry` intentionally does not always update file metadata after a data-version change. Updating too early would make future validation see consistent metadata even though cache/extent purge work is pending.
- Cache-manager calls are wrapped in SEH, and purge failures set delayed purge flags. Tests need to cover paths where `CcPurgeCacheSection` fails or cannot run because a lock was not acquired with `ForceFlush == FALSE`.
- `AFSSetVolumeState` increments the volume reference but, in the visible lines, does not decrement it after toggling state; this should be checked against later code/history or treated as a possible leak in this chunk.
- `AFSEvaluateRootEntry` passes `&VolumeReferenceReason` where the pattern elsewhere uses `&NewVolumeReferenceReason`; that may be intentional or a bug, but it is suspicious because transfer logic later reads `NewVolumeReferenceReason`.
- `AFSCheckForReadOnlyAccess` masks desired access with a set that omits some rights later included in the allowed mask, so correctness depends on the intended access vocabulary and should be tested with directory/file write-right combinations.
- `AFSGetObjectStatus` starts at line 8306 but is incomplete in this chunk; analysis of object status behavior requires the next chunk.

## Test Signals

- Initialization/shutdown: verify `AFSInitializeLibraryDevice`, `AFSInitializeGlobalDirectoryEntries`, `AFSInitializeSpecialShareNameList`, `AFSInitializeLibrary`, and `AFSCloseLibrary` create/free expected globals, resources, references, and callbacks without leaks on allocation-failure paths.
- Directory enumeration: enumerate global root and normal directories, then force data-version changes to confirm `AFSValidateDirectoryCache` preserves referenced entries as deleted, deletes unreferenced stale entries, and rebuilds case/short-name trees.
- File invalidation: trigger deleted, flushed, callback, expired, credential, and data-version invalidations and assert object flags, parent notifications, extent teardown/flush calls, and section purge behavior.
- Reparse targets: validate relative symlink targets, absolute AFS targets, DFS link reparses, invalid server names, and target-name updates/removals across data-version changes.
- Cache cleanup: test `AFSCleanupFcb` with direct service I/O enabled/disabled, force flush true/false, dirty extents, stale extents, open reference count zero/nonzero, object invalid/deleted flags, and cache-manager purge failure.
- Authentication: exercise impersonation token, primary token fallback, and token-query failure through `AFSGetAuthenticationId`/`AFSPerformGetAuthId`.
- Concurrency: race pioctl directory creation, object-info reference transitions to/from zero, directory validation during enumeration, and cache-file object replacement while `AFSReferenceCacheFileObject` is running.

### subset-b-007722: lines 8316-10150

# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSGeneric.cpp lines 8316-10150

## Purpose

This chunk contains Windows kernel redirector utility paths for object status lookup, directory-name validation, default security descriptor setup, authentication-group recovery, object invalidation, reparse policy, target-file metadata probing, and share-name detection.

The largest behavioral surfaces are:

- `AFSGetObjectStatus`, which resolves an object either by AFS FID or by `\afs`-rooted name and copies cached object metadata to an `AFSStatusInfoCB`.
- `AFSCreateDefaultSecurityDescriptor`, which builds the driver's process-wide default self-relative security descriptor.
- `AFSRetrieveValidAuthGroup`, which chooses a usable PAG/authentication GUID from open CCBs or from the current process/thread.
- `AFSPerformObjectInvalidate`, which reacts to delete and data-version invalidations by tearing down extents, purging cache sections, and setting verification/purge flags.

Smaller helpers support failed symlink access reporting, final/parent component parsing, filename character validation, reparse-point policy checks, file-info reads for reparse targets, and share-name parsing.

## Important APIs, Types, And Functions

- `AFSGetObjectStatus(AFSGetStatusInfoCB*, ULONG, AFSStatusInfoCB*, ULONG*)` maps either `GetStatusInfo->FileID` or `GetStatusInfo->FileName` to an `AFSObjectInfoCB`, then returns file id, target id, expiration, data version, type, flags, times, attributes, EOF, allocation, EA size, and link count.
- `AFSCheckSymlinkAccess(AFSDirectoryCB*, UNICODE_STRING*)` looks up a child name in case-sensitive, case-insensitive, and optional short-name indexes, then returns `STATUS_REPARSE_POINT_NOT_RESOLVED` for the unresolved symlink object.
- `AFSRetrieveFinalComponent` and `AFSRetrieveParentPath` are `UNICODE_STRING` slicing helpers based on `FsRtlDissectName` or backward slash scanning; they return views into the original buffer, not allocated copies.
- `AFSValidNameFormat` rejects `:`, `*`, `?`, `"`, `<`, and `>` in a file name.
- `AFSCreateDefaultSecurityDescriptor` allocates a World SID, optional low-integrity mandatory-label SACL, absolute security descriptor, then converts it to a page-sized self-relative descriptor stored in global `AFSDefaultSD`.
- `AFSRetrieveValidAuthGroup(AFSFcb*, AFSObjectInfoCB*, BOOLEAN, GUID*)` scans open `AFSCcb` entries for write or read access and falls back to `AFSRetrieveAuthGroupFnc(PID,TID,...)`.
- `AFSPerformObjectInvalidate(AFSObjectInfoCB*, ULONG)` handles `AFS_INVALIDATE_DELETED` and `AFS_INVALIDATE_DATA_VERSION`.
- `AFSIgnoreReparsePointToFile` reads `pDeviceExt->Specific.RDR.ReparsePointPolicy`.
- `AFSRetrieveTargetFileInfo` opens a kernel-handle target with `ZwCreateFile(FILE_READ_ATTRIBUTES)` and fills `AFSFileInfoCB` from `FILE_NETWORK_OPEN_INFORMATION`.
- `AFSIsShareName` returns true only for a path of the form `\Share` with no later slash.

Core structures and state touched here include `AFSDeviceExt`, `AFSVolumeCB`, `AFSObjectInfoCB`, `AFSDirectoryCB`, `AFSFcb`, `AFSCcb`, `AFSNameArrayHdr`, `AFSExtent`, `AFSByteRange`, global `AFSRDRDeviceObject`, `AFSGlobalRoot`, `AFSServerName`, and `AFSDefaultSD`.

## Control Flow

`AFSGetObjectStatus` has two resolution paths. When all FID fields are nonzero, it takes `VolumeTreeLock`, locates the volume by `AFSCreateHighIndex`, increments the volume with `AFS_VOLUME_REFERENCE_GET_OBJECT`, and either uses the volume object's embedded `ObjectInformation` for a volume FID or locates a child object by `AFSCreateLowIndex` in the volume `ObjectInfoTree`. Non-volume FID lookup takes the object-tree lock exclusive, increments `AFS_OBJECT_REFERENCE_STATUS`, and updates `LastAccessCount`.

When no full FID is supplied, `AFSGetObjectStatus` validates the variable input buffer, requires the first path component to match `AFSServerName`, initializes a name array from `AFSGlobalRoot`, references the root volume and directory entry, and calls `AFSLocateNameEntry` with mount-point and symlink target evaluation disabled. It transfers any returned volume and parent-directory references, rejects reparse status, then references `pDirectoryEntry->ObjectInformation`. Both paths converge on copying cached `AFSObjectInfoCB` fields into the output. The cleanup block decrements directory-entry references, object references, volume references, and frees the name array.

`AFSCheckSymlinkAccess` searches the parent directory's case-sensitive tree first, then case-insensitive tree, then short-name tree when short names are enabled and the component is legal DOS 8.3. A case-insensitive match with an ambiguous list returns `STATUS_OBJECT_NAME_COLLISION`. A found entry is temporarily open-referenced and then immediately decremented before returning `STATUS_REPARSE_POINT_NOT_RESOLVED`.

`AFSCreateDefaultSecurityDescriptor` is an initialization-time builder. It creates a World SID, optionally creates a low mandatory-label ACE/SACL if `AFSRtlSetSaclSecurityDescriptor` is available, creates an absolute descriptor, installs the SACL, group, and owner, validates the descriptor, converts it to a self-relative descriptor, and publishes it as `AFSDefaultSD`. Temporary allocations are freed on exit; the self-relative descriptor is retained only on success.

`AFSRetrieveValidAuthGroup` first normalizes a missing `Fcb` through `ObjectInfo->Fcb`. It then scans the FCB CCB list under `CcbListLock`, preferring a CCB with `FILE_WRITE_DATA` for write access and otherwise accepting a `FILE_READ_DATA` CCB. If none is found, it calls the configured auth-group callback for the current process and thread. A zero GUID is treated as no PAG and returns `STATUS_ACCESS_DENIED`.

`AFSPerformObjectInvalidate` branches by invalidation reason. Deleted file invalidation marks pending extent requests `STATUS_FILE_DELETED`, signals `ExtentsRequestComplete`, tears down FCB extents when service I/O is not direct, and sets `ObjectInfo->Links` to zero. Data-version invalidation either purges the full cache section in direct-service-I/O mode, or in cached mode reasons over extent dirtiness: no clean extents means no purge; clean extents with no open references can be torn down; clean extents with open references purge the full file; dirty extents trigger clean-range construction and range purging. Fallback code walks extents while holding the extent lock if a clean byte-range list cannot be allocated. On failure or exceptions, it sets `AFS_FCB_FLAG_PURGE_ON_CLOSE` and/or `AFS_OBJECT_FLAGS_VERIFY_DATA`. The caller's invalidation reference is always dropped at the end via `AFS_OBJECT_REFERENCE_INVALIDATION`.

## State And Persistence Behavior

This chunk mostly manipulates in-memory redirector state; it does not write durable on-disk records itself.

- Status lookup temporarily pins volumes, directory entries, and object-info blocks, then releases them in a central cleanup path.
- Object status output is a snapshot of cached object metadata already stored in `AFSObjectInfoCB`.
- `AFSCreateDefaultSecurityDescriptor` publishes process-global `AFSDefaultSD`; ownership transfers to global driver lifetime after successful self-relative conversion.
- Auth-group retrieval observes active open CCBs and current process/thread PAG mapping but does not persist credentials.
- Invalidation changes cached runtime state: FCB extent lists, extent request status/event, cache-manager section state, `Links`, `AFS_FCB_FLAG_PURGE_ON_CLOSE`, and `AFS_OBJECT_FLAGS_VERIFY_DATA`.
- Target-file info retrieval reads metadata from another file object through NT I/O manager APIs and copies it into an AFS file-info structure.

Reference accounting is central. The code uses `AFSVolumeIncrement/Decrement`, `AFSObjectInfoIncrement/Decrement`, and `DirOpenReferenceCount` increments/decrements with trace logging and assertions. Locking is done with ERESOURCE wrappers such as `AFSAcquireShared`, `AFSAcquireExcl`, and `AFSReleaseResource`.

## Dependencies And Integration Points

- Device and global redirector state: `AFSRDRDeviceObject`, `AFSDeviceExt`, `AFSGlobalRoot`, `AFSServerName`, and redirector policy flags.
- Namespace lookup: `AFSLocateHashEntry`, `AFSCreateHighIndex`, `AFSCreateLowIndex`, `AFSIsVolumeFID`, `AFSInitNameArray`, `AFSLocateNameEntry`, and `AFSFreeNameArray`.
- Directory indexes: `AFSGenerateCRC`, `AFSLocateCaseSensitiveDirEntry`, `AFSLocateCaseInsensitiveDirEntry`, `AFSLocateShortNameDirEntry`, and case-insensitive collision list flags.
- Windows kernel runtime: `FsRtlDissectName`, `RtlCompareUnicodeString`, SID/ACL/security-descriptor routines, `ZwCreateFile`, `ZwQueryInformationFile`, `ZwClose`, `CcPurgeCacheSection`, `KeSetEvent`, `KeQueryTickCount`, `PsGetCurrentProcessId`, and `PsGetCurrentThreadId`.
- Cache and extent subsystem: `AFSTearDownFcbExtents`, `AFSConstructCleanByteRangeList`, `AFSReleaseCleanExtents`, extent list heads/counts, dirty flags, and FCB section-object resources.
- Authentication: `AFSRetrieveAuthGroupFnc` and open CCB `AuthGroup`/`GrantedAccess` fields.
- Worker/cleanup integration: call sites in cleanup and worker code invoke `AFSPerformObjectInvalidate`; device-control code invokes `AFSGetObjectStatus`; initialization invokes `AFSCreateDefaultSecurityDescriptor`; extent paths invoke `AFSRetrieveValidAuthGroup`.

## Risks And Edge Cases

- The requested line range begins inside `AFSGetObjectStatus`; the full function signature and first local declarations begin just above the chunk at line 8306.
- In name-based `AFSGetObjectStatus`, after `AFSLocateNameEntry` returns failure or `STATUS_REPARSE`, the code sets `pVolumeCB = NULL` before cleanup. This relies on `AFSLocateNameEntry` and its returned-reference contract to avoid leaking or double-releasing references.
- The cleanup path decrements both `pDirectoryEntry` and `pParentDirEntry`; callers changing `AFSLocateNameEntry` reference semantics must preserve these assumptions.
- `AFSRetrieveValidAuthGroup` assigns `pFcb` from `ObjectInfo->Fcb`, but uses `Fcb->NPFcb` and `Fcb->CcbListHead` inside the later `if (pFcb != NULL)` block. If this is not guarded elsewhere, calling with `Fcb == NULL` and `ObjectInfo->Fcb != NULL` appears vulnerable to null dereference.
- `AFSCheckSymlinkAccess` manually releases the directory tree lock before `try_return` on case-insensitive collision; this is correct only because the common cleanup does not also release that lock.
- The security descriptor builder uses fixed ACE slack and a page-sized self-relative buffer. Changes to descriptor contents must keep `ulSDLength` sizing and cleanup ownership correct.
- `AFSPerformObjectInvalidate` has complex lock ordering across FCB resource, section-object resource, and extents resource. The fallback path explicitly notes possible deadlock when it cannot allocate a byte-range list and must walk extents under the extent lock.
- Cache purge calls are wrapped in SEH, but many failure paths degrade to purge-on-close or verify-data flags; tests should check that stale clean data cannot be consumed after purge failures.
- `AFSConstructCleanByteRangeList` returns a list pointer that is advanced/mutated during purge processing; ownership and release behavior must be verified in the implementation of that helper.
- `AFSValidNameFormat` rejects only a subset of Windows-invalid characters and does not reject slash, backslash, control characters, or trailing-dot/space forms in this helper alone; callers must layer additional validation where required.

## Test Signals

Useful validation for this chunk includes:

- IOCTL/status tests for FID-based lookup of volume and non-volume objects, invalid FID rejection, name-based lookup under `\afs`, invalid server component rejection, and output field parity with cached `AFSObjectInfoCB`.
- Reference-count tracing around `AFSGetObjectStatus` success, invalid-parameter, allocation-failure, and reparse paths to catch leaked volume, object, directory-entry, or name-array references.
- Directory lookup tests for unresolved symlink components covering exact case, case-insensitive unique match, case-insensitive collision, short-name lookup enabled/disabled, and missing names.
- Name helper tests for final component and parent path with root, trailing slash, single-component, and multi-component `UNICODE_STRING` inputs.
- Security descriptor initialization tests checking success when optional `AFSRtlSetSaclSecurityDescriptor`/group callbacks exist or are absent, descriptor validity, self-relative output, and cleanup on allocation/API failures.
- Auth-group tests with write CCB, read-only CCB fallback, no CCB plus valid current PAG, no CCB plus zero GUID, and the `Fcb == NULL`/`ObjectInfo->Fcb != NULL` case.
- Invalidation tests for deleted files, direct-service-I/O data-version purge, cached data-version purge with no dirty extents, all dirty extents, mixed dirty/clean extents, no open references, open references, byte-range-list allocation failure, and `CcPurgeCacheSection` failure/exception paths.
- Reparse policy tests for `AFS_REPARSE_POINT_TO_FILE_AS_FILE`, target-file-info tests for open/query failure and metadata-copy success, and share-name tests for `\share` versus `\share\child`.
