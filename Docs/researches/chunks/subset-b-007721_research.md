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
