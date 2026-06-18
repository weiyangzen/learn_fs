# Group Research: group_1845_windows_driver_samples_sources_windows_windows_driver_samples_files_260de7109947

Scope: `Docs/research_subset_a.md`, Windows filesystem samples under `sources/windows/windows-driver-samples`.

This grouped batch covers two related Windows filesystem-driver examples:

- FastFAT write handling: full `IRP_MJ_WRITE` dispatch, cached/noncached write paths, FAT metadata writes, DASD writes, valid-data/file-size extension, cache coherency, async completion, and deferred flush support.
- MetadataManager minifilter: a sample minifilter that owns per-volume metadata, releases metadata references for volume locks/dismount/removal, reacquires them afterward, and demonstrates instance lifecycle handling.

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/write.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/write.c

## Purpose

`write.c` implements the FastFAT write path for `IRP_MJ_WRITE`. It handles:

- FSD write dispatch through `FatFsdWrite`.
- Main write processing through `FatCommonWrite`.
- Special writes to paging files, FAT metadata, raw volumes, normal files, directories, and EA files.
- Cached, noncached, paging, MDL, synchronous, asynchronous, write-through, and write-to-EOF variants.
- EOF and valid-data-length extension.
- FAT allocation growth, cache-manager coherency, oplock/file-lock checks, completion, rollback, and deferred flush work.

This is a core filesystem write-path file, not just sample glue.

## Major Entry Points

### `FatFsdWrite`

`FatFsdWrite` is the dispatch entry for write IRPs.

Key behavior:

- Enters the filesystem with `FsRtlEnterFileSystem`.
- Fast-paths paging-file I/O before creating a normal IRP context:
  - If the target is not the filesystem device object and the FCB is a paging file, it marks the IRP pending and calls `FatPagingFileIo`.
- Creates an `IRP_CONTEXT` with waitability derived from the IRP.
- Handles the modified-page-writer top-level IRP case by temporarily replacing `IoGetTopLevelIrp()` with the actual IRP so write-through behavior works correctly.
- Routes `IRP_MN_COMPLETE` to `FatCompleteMdl`; all other writes go to `FatCommonWrite`.
- Uses the FastFAT exception filter/processor and restores top-level IRP state before leaving the filesystem.

### `FatCommonWrite`

`FatCommonWrite` is the main write implementation. Its inputs are the IRP context and IRP; it derives the rest from the current stack location and file object.

It initializes core state:

- `Wait` from `IRP_CONTEXT_FLAG_WAIT`.
- `PagingIo` from `IRP_PAGING_IO`.
- `NonCachedIo` from `IRP_NOCACHE`.
- `SynchronousIo` from `FO_SYNCHRONOUS_IO`.
- `WriteToEof` from `FILE_WRITE_TO_END_OF_FILE`.
- `TypeOfOpen` via `FatDecodeFileObject`.

It immediately completes zero-length writes with success.

## Cached Write Admission

Before decoding all object-specific cases, the routine throttles cached writes with `CcCanIWrite`. If the cache manager says the write should be deferred, FastFAT:

- Calls `FatPrePostIrp`.
- Sets `IRP_CONTEXT_FLAG_DEFERRED_WRITE`.
- Calls `CcDeferWrite` with `FatAddToWorkque`.
- Returns `STATUS_PENDING`.

This keeps large cached writes from overwhelming the cache manager.

## Range and Context Setup

For ordinary non-paging, non-EOF writes, FastFAT rejects ranges that would require maintaining FAT allocation sizes beyond 32 significant bits by calling `FatIsIoRangeValid`.

For noncached I/O, it creates or reuses a `FAT_IO_CONTEXT`:

- Synchronous noncached I/O can use stack storage.
- Asynchronous noncached I/O allocates nonpaged pool.
- The async context records resource ownership and requested byte count for completion/release logic.

If the volume is already shut down, the write fails with `STATUS_TOO_LATE`.

## Virtual Volume File Writes

`TypeOfOpen == VirtualVolumeFile` is the internal volume file used for FAT metadata.

Important behavior:

- Requires waitable execution; otherwise posts to the FSP.
- If not called by the lazy writer, sets write-through in the IRP context.
- Uses `Vcb->DirtyFatMcb` to find dirty FAT sectors within the requested write range.
- Skips clean runs, writes from the first dirty run through the last dirty run needed, and may include clean bytes for efficiency.
- Builds one `IO_RUN` per FAT copy, mapping the same dirty VBO region to each FAT’s LBO.
- Calls `FatMultipleAsync`, waits with `FatWaitSync`, and on success removes the written range from `DirtyFatMcb`.
- On error, normalizes/raises the status so volume verification/reset can occur.

The invariant is that the dirty FAT MCB alternates clean holes and dirty runs, and must contain an even number of runs.

## Raw Volume Writes

`TypeOfOpen == UserVolumeOpen` handles DASD/raw volume writes.

Key rules:

- Raw volume opens are forced to noncached I/O.
- For disk devices that are not volume-locked, writes are restricted to the reserved area unless:
  - `SL_FORCE_DIRECT_WRITE` is set,
  - the handle performed a complete dismount,
  - or extended DASD I/O is allowed.
- The VCB is verified unless the handle has complete-dismount or format-unit flags.
- A format-unit handle may override verify.
- On the first DASD write per CCB, FastFAT flushes/purges FAT and referenced file objects under exclusive volume synchronization.
- Unless extended DASD I/O is allowed, writes are clipped to visible volume size.
- User buffers are locked, `FO_FILE_MODIFIED` is set, and `FatSingleAsync` issues the disk write.
- Async writes detach the IRP context and return `STATUS_PENDING`.
- Sync writes wait, normalize failures, and update `CurrentByteOffset`.

## User File Writes

`TypeOfOpen == UserFileOpen` is the largest and most complex branch.

### Noncached Coherency

For noncached, non-paging writes to a file that also has a cache map:

- FastFAT acquires the FCB exclusive.
- It pre-acquires the paging I/O resource.
- On newer builds it uses `CcCoherencyFlushAndPurgeCache`; older builds use `CcFlushCache` followed by `CcPurgeCacheSection`.
- It keeps paging I/O held across the noncached write to prevent page faults from observing stale disk data.
- In purge-failure mode for user files, a purge failure returns `STATUS_PURGE_FAILED`.

This is one of the key correctness mechanisms in the file.

### Resource Acquisition

The write path selects resources according to operation type:

- Paging I/O acquires `Header.PagingIoResource` shared and waits for `MoveFileEvent` if present.
- Non-paging I/O normally acquires the FCB shared.
- Async noncached I/O may wait for exclusive waiters and records the acquired resource in the async context.
- If EOF or valid-data extension is needed, the path upgrades to exclusive FCB synchronization.

### Paging I/O Truncation

Paging writes are never allowed to extend file size.

If paging I/O starts beyond EOF:

- It completes successfully with zero bytes.

If it extends beyond EOF:

- `ByteCount` is trimmed to file size.

This prevents cache manager or memory manager page flushes from creating filesystem-visible file growth.

### Lazy Writer and Recursive Write-Through

The routine detects:

- Lazy-writer writes by comparing the current thread with `FcbOrDcb->Specific.Fcb.LazyWriteThread`.
- Recursive synchronous paging writes generated by write-through cached writes.

Lazy-writer writes are blocked from flushing mapped pages beyond safe valid-data regions and are not allowed to perform file-size/VDL extension work.

Recursive write-through writes set `IRP_CONTEXT_FLAG_WRITE_THROUGH` but are also excluded from top-level valid-data extension behavior.

### EOF and Valid Data Extension

The routine follows explicit rules:

- Paging I/O never extends file size.
- Only top-level callers extend valid data length.
- If file size or valid data must grow, the FCB is acquired exclusive.

For write-to-EOF, the actual starting VBO is recalculated after acquiring synchronization and reading current file size.

Before modifying the file, non-paging user writes check:

- Oplocks through `FsRtlCheckOplock`.
- Fast I/O possibility after oplock state changes.
- Byte-range locks through `FsRtlCheckLockForWriteAccess`.

### Allocation Growth

When a write extends file size past allocation size:

- Existing allocation size may first be looked up if it is only a hint.
- FastFAT tries allocation chunking when this is not the first allocation:
  - It computes a multiplier based on free clusters and requested growth.
  - The multiplier is capped at 32.
  - Allocation is capped at the maximum legal FAT file size.
  - If the larger allocation fails with disk full, it falls back to minimum allocation.
- Successful chunked allocation sets `FCB_STATE_TRUNCATE_ON_CLOSE`.
- The FCB file size is updated.
- If the file is cached, `CcSetFileSizes` informs the cache manager.

### Valid Data Handling

The routine decides whether `ExtendingValidData` is needed after final resource and size checks.

It uses `ValidDataToCheck = max(ValidDataToDisk, ValidDataLength)` to determine whether zeroing is needed.

For noncached writes starting beyond valid data, it zeroes the gap with `FatZeroData`, except for lazy-writer and recursive write-through cases.

After a successful write that extends valid data:

- `Header.ValidDataLength` is advanced but never past file size.
- For noncached writes to cached files, `CcSetFileSizes` updates cache-manager state so future cached I/O does not see incorrect zero-page behavior.

## Noncached File Writes

In the noncached branch:

- The write length is rounded up to sector size.
- The start must be sector-aligned.
- If the rounded length differs from requested length, the write must not overwrite valid data past the caller’s byte count; otherwise FastFAT returns `STATUS_NOT_IMPLEMENTED`.
- Gaps beyond valid data are zeroed.
- `WriteFileSizeToDirent` is set so successful extending noncached writes update on-disk directory entry size.
- `FatNonCachedIo` issues the transfer.
- Pending async I/O detaches the IRP and IRP context.
- On success, `IoStatus.Information` is restored to the caller’s original byte count and `ValidDataToDisk` is advanced.

## Cached File Writes

In the cached branch:

- Paging I/O is not expected.
- The cache map is lazily initialized with `FatInitializeCacheMap`.
- Allocation size is validated before cache initialization; if file size exceeds allocation size, FastFAT reports file corruption.
- Read-ahead granularity is set.
- On deferred-flush media:
  - Page-aligned large writes make the file object write-through.
  - Small writes schedule a one-second deferred flush via timer/DPC/work item.
- Gaps beyond valid data are zeroed with `FatZeroData`.
- `WriteFileSizeToDirent` is true only for write-through cached writes.
- Normal cached writes map the user buffer and call `CcCopyWriteEx` or `CcCopyWrite`.
- MDL writes call `CcPrepareMdlWrite`.

## Directory and EA File Writes

`DirectoryFile` and `EaFile` writes are treated as system paging/noncached writes.

Behavior:

- Verifies the FCB/DCB.
- Acquires paging I/O shared, starving exclusive waiters.
- Waits on `MoveFileEvent` if present.
- Sets write-through if not called by the lazy writer.
- Asserts sector alignment and paging/noncached mode.
- Trims writes to file size.
- Issues `FatNonCachedIo`.
- Normalizes failures.

`UserDirectoryOpen` writes are rejected with `STATUS_INVALID_PARAMETER`.

Unknown open types bugcheck because they indicate internal corruption.

## Completion and Rollback

The `try_exit` and `finally` logic is as important as the write branches.

On successful, non-posted completion:

- Updates synchronous current byte offset.
- Sets `FO_FILE_MODIFIED` for non-paging writes.
- If file size was extended and `WriteFileSizeToDirent` is true:
  - Calls `FatSetFileSizeInDirent`.
  - Reports `FILE_NOTIFY_CHANGE_SIZE`.
- If file size was extended but not immediately written to the dirent:
  - Sets `FO_FILE_SIZE_CHANGED`.
- If valid data was extended:
  - Advances `Header.ValidDataLength`.
  - Updates cache manager for noncached writes to cached files.
- Unpins repinned BCBs.

When posting after tentative file-size extension:

- It rolls back `Header.FileSize`.
- Updates the cache manager’s file size pointer if a shared cache map exists.
- Posts with `FatFsdPostRequest`.

On abnormal termination:

- Restores initial file size and valid data length if they were extended.
- Pulls back the cache size pointer if needed.

Finally, it unwinds outstanding async counters, releases FCB and paging resources if still associated with the IRP, and completes non-posted requests.

## Deferred Flush Helpers

### `FatDeferredFlushDpc`

Runs from the timer DPC after a small cached write on deferred-flush media. It initializes and queues a work item to `FatDeferredFlush`.

### `FatDeferredFlush`

Runs in a worker thread and:

- Decodes the file object.
- Sets top-level IRP to `FSRTL_FSP_TOP_LEVEL_IRP`.
- Acquires the FCB exclusive and paging I/O shared.
- Calls `CcFlushCache`.
- Releases resources.
- Clears top-level IRP.
- Dereferences the file object and frees the flush context.

## Important Invariants

- `ValidDataLength <= FileSize <= AllocationSize`.
- Paging I/O must not extend file size.
- Only top-level writes extend valid data length.
- Noncached writes against cached files must force cache coherency before disk I/O.
- FAT metadata writes are tracked and cleaned through `DirtyFatMcb`.
- File-size/VDL changes are rolled back if the path posts or aborts before completion.
- Async noncached writes carry resource-release information in `FAT_IO_CONTEXT`.

## Dependencies

This file depends heavily on FastFAT infrastructure declared elsewhere, including:

- FCB/VCB/CCB structures and open decoding.
- Allocation helpers such as `FatAddFileAllocation`, `FatLookupFileAllocationSize`, and `FatTruncate...`-style close cleanup elsewhere.
- Cache helpers such as `FatInitializeCacheMap`, `FatZeroData`, and `FatUnpinRepinnedBcbs`.
- Device I/O helpers such as `FatSingleAsync`, `FatMultipleAsync`, `FatNonCachedIo`, and `FatWaitSync`.
- Error handling through `FatNormalizeAndRaiseStatus`, `FatRaiseStatus`, and exception filters.
- Notification and dirent update helpers.

## Research Notes

This file is a dense reference for Windows filesystem write-path design. The most reusable patterns are:

- Split dispatch wrapper from common write engine.
- Treat paging writes, cached writes, and noncached writes as separate synchronization domains.
- Keep cache coherency and VDL extension decisions explicit.
- Roll back FCB/cache-manager state when an operation is posted or aborted.
- Use separate paths for raw volume writes and internal metadata writes rather than forcing them through normal file semantics.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/write.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/DataStore.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/DataStore.c

## Purpose

`DataStore.c` implements metadata-file lifecycle support for the MetadataManager minifilter sample.

The file demonstrates how a filter can:

- Open or create a per-volume metadata file.
- Hold both a handle and referenced file object for that metadata file.
- Temporarily release those references before volume locks, dismounts, and PnP removal.
- Reacquire the references afterward when safe.
- Avoid deadlocks when issuing filesystem operations while holding instance-context synchronization.

The sample metadata file is `\System Volume Information\FilterMetadata.md` on the target volume.

## Main State Managed

The routines operate on `FMM_INSTANCE_CONTEXT`, especially:

- `MetadataResource`: protects metadata-related state.
- `MetadataHandle`: filter-owned metadata file handle.
- `MetadataFileObject`: referenced file object for the metadata file.
- `MetadataOpenTriggerFileObject`: volume file object that caused metadata references to be dropped.
- `INSTANCE_CONTEXT_F_METADATA_OPENED`: metadata file is open.
- `INSTANCE_CONTEXT_F_TRANSITION`: the context resource was dropped around a filter-issued filesystem operation.

## `FmmOpenMetadata`

`FmmOpenMetadata` opens or creates the metadata file for an instance.

Preconditions:

- The caller holds the instance metadata resource exclusive.
- The caller is in a critical region.
- Runs at PASSIVE_LEVEL.

Behavior:

1. Builds a full metadata filename:
   - Allocates an initial Unicode buffer sized from `FMM_DEFAULT_VOLUME_NAME_LENGTH + FMM_METADATA_FILE_NAME_LENGTH`.
   - Calls `FltGetVolumeName`.
   - If the buffer is too small, frees it, grows the length, and retries.
   - Appends `FMM_METADATA_FILE_NAME`.

2. Calls `FltCreateFile`:
   - Uses `FILE_ALL_ACCESS`.
   - Creates a system/hidden file.
   - Uses `FILE_OPEN_IF` when `CreateIfNotPresent` is true, otherwise `FILE_OPEN`.
   - Shares read access.
   - Wraps the call with `FmmBeginFileSystemOperation` and `FmmEndFileSystemOperation`.

3. If creation fails with `STATUS_OBJECT_PATH_NOT_FOUND` and creation is allowed:
   - Calls `FltCreateSystemVolumeInformationFolder`.
   - Retries `FltCreateFile` if folder creation succeeds.

4. Converts the handle into a referenced file object with `ObReferenceObjectByHandle`.

5. On success:
   - Leaves `MetadataHandle` and `MetadataFileObject` stored in the instance context.
   - Sets `INSTANCE_CONTEXT_F_METADATA_OPENED`.

6. On failure:
   - Closes any handle opened so far.
   - Dereferences any metadata file object acquired.
   - Frees the Unicode filename buffer.

The function contains sample comments where a real filter would initialize or validate metadata contents.

## `FmmCloseMetadata`

`FmmCloseMetadata` closes the filter’s metadata references.

Preconditions:

- Caller holds `MetadataResource`.
- Metadata handle and file object must both be present.

Behavior:

- Dereferences `MetadataFileObject`.
- Calls `FltClose` on `MetadataHandle`, again wrapped in `FmmBeginFileSystemOperation` and `FmmEndFileSystemOperation`.
- Clears both pointers.
- Clears `INSTANCE_CONTEXT_F_METADATA_OPENED`.

## `FmmReleaseMetadataFileReferences`

This routine is called when the filter must stop holding the metadata file open, usually because the filesystem needs exclusive volume access.

Behavior:

- Gets the instance context from the target instance.
- Acquires `MetadataResource` exclusive.
- If the context is in transition, returns `STATUS_FILE_LOCK_CONFLICT`.
- If metadata is open:
  - Calls `FmmCloseMetadata`.
  - Stores the current target file object in `MetadataOpenTriggerFileObject`.
- Releases the resource and context reference.

This function is used before volume locks, dismounts, and query remove.

## `FmmReacquireMetadataFileReferences`

This routine reopens the metadata file after a prior release.

Behavior:

- Gets the instance context.
- Acquires `MetadataResource` exclusive.
- If the context is in transition, returns `STATUS_FILE_LOCK_CONFLICT`.
- Reopens metadata only when `MetadataOpenTriggerFileObject` matches the current target file object.
- Calls `FmmOpenMetadata` with `CreateIfNotPresent = FALSE`.
- Clears `MetadataOpenTriggerFileObject` after the reopen attempt.
- Releases the resource and context reference.

This trigger-file-object check prevents unrelated volume handles from causing metadata to be reopened at the wrong time.

## `FmmSetMetadataOpenTriggerFileObject`

This routine records which volume file object should later trigger metadata reacquisition.

Behavior:

- Gets the instance context.
- Acquires `MetadataResource` exclusive.
- Refuses to modify state during `INSTANCE_CONTEXT_F_TRANSITION`.
- Asserts that any existing trigger is either null or the same file object.
- Stores `Cbd->Iopb->TargetFileObject`.

This is used after successful volume locks, including cases where lower filters may have recursively issued lock operations.

## Transition Helpers

### `FmmBeginFileSystemOperation`

Called before the filter sends filesystem I/O while holding `MetadataResource` exclusive.

Behavior:

- Asserts the context is not already in transition.
- Sets `INSTANCE_CONTEXT_F_TRANSITION`.
- Releases `MetadataResource` and leaves the critical region.

The purpose is to avoid deadlock if a lower filter reenters the top of the filter stack while this filter is holding the instance resource.

### `FmmEndFileSystemOperation`

Called after the filter-issued filesystem operation completes.

Behavior:

- Reacquires `MetadataResource` exclusive.
- Asserts the transition flag is still set.
- Clears `INSTANCE_CONTEXT_F_TRANSITION`.

Other threads that acquire the resource during the transition detect the flag and avoid reading or modifying the context.

## Optional `FmmIsMetadataOpen`

Compiled only when `VERIFY_METADATA_OPENED` is enabled.

Behavior:

- Gets the instance context.
- Acquires metadata resource shared.
- If not in transition, returns whether `INSTANCE_CONTEXT_F_METADATA_OPENED` is set.
- Asserts flag/pointer consistency:
  - Open flag implies handle and file object are non-null.
  - No open flag implies both are null.

## Error and Synchronization Model

The core concurrency model is:

- Normal metadata state changes require exclusive `MetadataResource`.
- Filter-issued filesystem operations drop that resource temporarily.
- The transition flag prevents other threads from acting on half-stable state.
- `STATUS_FILE_LOCK_CONFLICT` is used as the benign “try again or ignore because transition” signal.

## Research Notes

`DataStore.c` is the key file for understanding how the MetadataManager sample avoids self-deadlocks while maintaining a metadata file. The metadata contents are intentionally left as placeholders; the sample is about safe metadata-file ownership and release/reacquire choreography, not about a concrete metadata format.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/DataStore.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/MetadataManagerInit.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/MetadataManagerInit.c

## Purpose

`MetadataManagerInit.c` is the initialization and lifecycle module for the MetadataManager minifilter sample.

It defines:

- Global filter state.
- Filter Manager operation registrations.
- Instance context registration.
- Driver entry and unload.
- Debug-level registry support for checked builds.
- Instance setup, teardown, and context cleanup.

## Global State

The file defines:

- `FMM_GLOBAL_DATA Globals`, which stores:
  - `PFLT_FILTER Filter`.
  - Debug level in checked builds.

It also defines unsupported device characteristics:

- `FILE_FLOPPY_DISKETTE`
- `FILE_READ_ONLY_DEVICE`
- `FILE_VIRTUAL_VOLUME`

The sample avoids attaching to those devices.

## Operation Registration

The `Callbacks` array registers the minifilter for:

- `IRP_MJ_CREATE`
- `IRP_MJ_CLEANUP`
- `IRP_MJ_FILE_SYSTEM_CONTROL`
- `IRP_MJ_DEVICE_CONTROL`
- `IRP_MJ_SHUTDOWN`
- `IRP_MJ_PNP`

Create registration depends on `VERIFY_METADATA_OPENED`:

- If verification is enabled, all non-paging creates are observed.
- Otherwise, non-DASD creates are skipped to avoid unnecessary overhead.

Cleanup and filesystem-control callbacks skip paging and non-DASD I/O. Device control, shutdown, and PnP skip paging I/O.

## Context Registration

The `ContextRegistration` array registers one context type:

- `FLT_INSTANCE_CONTEXT`
- Size: `FMM_INSTANCE_CONTEXT_SIZE`
- Cleanup callback: `FmmContextCleanup`
- Pool tag: `FMM_INSTANCE_CONTEXT_TAG`

The instance context stores per-volume metadata-file ownership and synchronization state.

## Filter Registration

`FilterRegistration` wires the filter to Filter Manager:

- Context registration.
- Operation callbacks.
- `FmmUnload`.
- `FmmInstanceSetup`.
- `FmmInstanceQueryTeardown`.
- `FmmInstanceTeardownStart`.
- `FmmInstanceTeardownComplete`.

Name provider callbacks are unused.

## `DriverEntry`

`DriverEntry` performs driver initialization:

- Opts into `NonPagedPoolNx` through `ExInitializeDriverRuntime`.
- Zeroes `Globals`.
- Initializes debug level in checked builds.
- Calls `FltRegisterFilter`.
- Calls `FltStartFiltering`.
- Unregisters the filter if start fails.
- Returns the final status.

## Debug Registry Helpers

Compiled only under `DBG`.

### `FmmGetIoOpenDriverRegistryKey`

Looks up `IoOpenDriverRegistryKey` dynamically with `MmGetSystemRoutineAddress`.

### `FmmOpenServiceParametersKey`

Opens the service parameters key:

- Preferably through `IoOpenDriverRegistryKey`.
- Falls back to opening the service root key and then `Parameters`.

### `FmmInitializeDebugLevel`

Reads `DebugLevel` from the service parameters key. Defaults to `DEBUG_TRACE_ERROR` when no registry value is found.

## `FmmUnload`

Unregisters the minifilter through `FltUnregisterFilter` and clears `Globals.Filter`.

It ignores unload flags and always returns `STATUS_SUCCESS`.

## `FmmContextCleanup`

Handles cleanup for registered contexts.

For `FLT_INSTANCE_CONTEXT`, it:

- Casts the context to `FMM_INSTANCE_CONTEXT`.
- Deletes `MetadataResource` with `ExDeleteResourceLite`.

Actual metadata handle/file-object closure is handled during instance teardown complete, not here.

## `FmmInstanceSetup`

`FmmInstanceSetup` decides whether the filter attaches to a volume and initializes per-instance state.

Attach criteria:

- Filesystem type must be NTFS, FAT, or ReFS.
- The underlying disk device must be `FILE_DEVICE_DISK`.
- The disk must not have unsupported characteristics such as floppy, read-only, or virtual volume.

Setup flow:

1. Validate filesystem type.
2. Get and inspect the disk device object.
3. Allocate an `FMM_INSTANCE_CONTEXT`.
4. Zero and initialize:
   - Flags.
   - Instance.
   - Filesystem type.
   - Volume.
   - Metadata resource.
5. Associate the context with the instance using `FltSetInstanceContext`.
6. Acquire the metadata resource exclusive.
7. Open metadata using `FmmOpenMetadata`.
   - Creates the metadata file only for manual attachment.
   - For automatic attachment, the metadata file must already exist.
8. Release the resource.
9. Release the local context reference in all cases.

If the failure is simply unsupported volume/device and the attach was automatic, the status is converted to `STATUS_FLT_DO_NOT_ATTACH` to avoid noisy error logging.

## `FmmInstanceQueryTeardown`

Always permits manual detach by returning `STATUS_SUCCESS`.

It is present to show where a real filter could reject detach requests.

## `FmmInstanceTeardownStart`

Logs teardown start/end and does no state mutation.

## `FmmInstanceTeardownComplete`

Completes cleanup for an instance:

- Gets the instance context.
- Acquires `MetadataResource` exclusive.
- Asserts the context is not in transition.
- If metadata is open, calls `FmmCloseMetadata`.
- Releases the resource.
- Releases the context reference.

This ensures the metadata file handle/object are closed before the context cleanup deletes the resource.

## Research Notes

This file defines the sample’s attach policy and lifecycle boundaries. The key relationship is:

- `MetadataManagerInit.c` creates and owns `FMM_INSTANCE_CONTEXT`.
- `DataStore.c` manages metadata-file state inside that context.
- `operations.c` triggers release/reacquire based on filesystem operations.

The sample intentionally attaches only when metadata exists on automatic mount, while manual attach can create the metadata file.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/MetadataManagerInit.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/MetadataManagerProc.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/MetadataManagerProc.h

## Purpose

`MetadataManagerProc.h` declares the MetadataManager minifilter’s function interfaces and inline lock helpers.

It groups prototypes by implementation file:

- `operations.c`
- `DataStore.c`
- `support.c`

It also defines a helper macro for resource ownership and inline wrappers around `ERESOURCE` acquisition/release.

## Macro

### `MAKE_RESOURCE_OWNER`

```c
#define MAKE_RESOURCE_OWNER(X) (((ERESOURCE_THREAD)(X)) | 0x3)
```

This creates an `ERESOURCE_THREAD` owner value from an input pointer/thread-like value by setting low bits. It matches the resource ownership style used in Windows filesystem code.

## Operation Callback Prototypes

The header declares minifilter callbacks implemented in `operations.c`:

- `FmmPreCreate`
- `FmmPostCreate`
- `FmmPreCleanup`
- `FmmPostCleanup`
- `FmmPreFSControl`
- `FmmPostFSControl`
- `FmmPreDeviceControl`
- `FmmPostDeviceControl`
- `FmmPreShutdown`
- `FmmPrePnp`
- `FmmPostPnp`

The signatures match Filter Manager pre/post operation callback types and include SAL annotations for callback data, related objects, completion context, and post-operation flags.

## Data Store Prototypes

The header declares metadata lifecycle routines implemented in `DataStore.c`:

- `FmmOpenMetadata`
- `FmmCloseMetadata`
- `FmmReleaseMetadataFileReferences`
- `FmmReacquireMetadataFileReferences`
- `FmmSetMetadataOpenTriggerFileObject`
- `FmmBeginFileSystemOperation`
- `FmmEndFileSystemOperation`
- Optional `FmmIsMetadataOpen` when `VERIFY_METADATA_OPENED` is enabled.

The prototypes document important lock contracts with SAL:

- `FmmOpenMetadata` and `FmmCloseMetadata` require the global critical region and `InstanceContext->MetadataResource`.
- `FmmBeginFileSystemOperation` releases both the critical region and metadata resource.
- `FmmEndFileSystemOperation` reacquires them.
- `FmmIsMetadataOpen` has its own conditional compile contract.

These annotations are part of the sample’s concurrency documentation.

## Support Routine Prototypes

The header declares utility routines from `support.c`:

- `FmmAllocateUnicodeString`
- `FmmFreeUnicodeString`
- `FmmTargetIsVolumeOpen`
- `FmmIsImplicitVolumeLock`

These support buffer allocation, target-file-object classification, and implicit volume lock detection.

## Inline Lock Helpers

### `FmmAcquireResourceExclusive`

- Requires IRQL <= APC_LEVEL.
- Enters a critical region.
- Acquires an `ERESOURCE` exclusive.
- Asserts there is no incompatible shared/exclusive acquisition.

### `FmmAcquireResourceShared`

- Requires IRQL <= APC_LEVEL.
- Enters a critical region.
- Acquires an `ERESOURCE` shared.

### `FmmReleaseResource`

- Asserts the resource is held.
- Releases the `ERESOURCE`.
- Leaves the critical region.

These helpers centralize the rule that metadata-resource acquisition pairs with `KeEnterCriticalRegion`/`KeLeaveCriticalRegion`, blocking normal kernel APC delivery while the resource is held.

## Research Notes

This header is the contract file for the sample. The most important details are the SAL lock annotations around metadata operations and the resource wrappers. Any implementation change to `DataStore.c` or `operations.c` should preserve these lock contracts.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/MetadataManagerProc.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/MetadataManagerStruc.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/MetadataManagerStruc.h

## Purpose

`MetadataManagerStruc.h` defines the MetadataManager sample’s core data structures, constants, flags, metadata filename, and debug tracing macros.

## Verification Flag

```c
#define VERIFY_METADATA_OPENED 0
```

When enabled, the filter validates that metadata is open whenever non-volume creates succeed. In the checked-in configuration it is disabled, so the create path can skip non-DASD I/O for performance.

## Pool Tags

Defined pool tags:

- `FMM_STRING_TAG`
- `FMM_INSTANCE_CONTEXT_TAG`

These tag Unicode string buffers and instance contexts.

## Global Data

`FMM_GLOBAL_DATA` contains:

- `PFLT_FILTER Filter`: handle returned by `FltRegisterFilter`.
- `ULONG DebugLevel`: checked-build-only debug trace mask.

The file declares:

```c
extern FMM_GLOBAL_DATA Globals;
```

The storage is defined in `MetadataManagerInit.c`.

## Instance Context Flags

### `INSTANCE_CONTEXT_F_TRANSITION`

Indicates the instance metadata resource was intentionally released before issuing a filesystem operation that could reenter the filter stack.

While this flag is set, other threads that acquire the resource should avoid using or modifying the instance context.

### `INSTANCE_CONTEXT_F_METADATA_OPENED`

Indicates the filter currently has an open handle and referenced file object for the volume’s metadata file.

## `FMM_INSTANCE_CONTEXT`

The per-volume instance context contains:

- `Flags`: instance flags.
- `Instance`: Filter Manager instance handle.
- `FilesystemType`: attached filesystem type.
- `Volume`: Filter Manager volume handle.
- `MetadataResource`: `ERESOURCE` protecting metadata state.
- `MetadataHandle`: metadata file handle.
- `MetadataFileObject`: referenced metadata file object.
- `MetadataOpenTriggerFileObject`: volume file object whose cleanup/unlock/cancel path should trigger metadata reopen.

This context is allocated in `FmmInstanceSetup`, associated with the instance, used by `DataStore.c`, and closed in teardown.

## Metadata File Name

The sample metadata path is:

```c
\System Volume Information\FilterMetadata.md
```

Constants:

- `FMM_METADATA_FILE_NAME`
- `FMM_METADATA_FILE_NAME_LENGTH`
- `FMM_DEFAULT_VOLUME_NAME_LENGTH`

The metadata open path appends this relative path to the volume name returned by `FltGetVolumeName`.

## Debug Trace Flags

Checked builds define trace categories:

- `DEBUG_TRACE_ERROR`
- `DEBUG_TRACE_LOAD_UNLOAD`
- `DEBUG_TRACE_INSTANCES`
- `DEBUG_TRACE_METADATA_OPERATIONS`
- `DEBUG_TRACE_ALL_IO`
- `DEBUG_TRACE_INFO`
- `DEBUG_TRACE_ALL`

`DebugTrace` expands to `DbgPrint` when the requested level is enabled in `Globals.DebugLevel`; otherwise it compiles to nothing.

## Research Notes

This header is the sample’s state model. The key design is that a minifilter can keep per-volume metadata state in an instance context, but must be prepared to drop actual file references when the filesystem needs exclusive volume access.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/MetadataManagerStruc.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/operations.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/operations.c

## Purpose

`operations.c` implements the MetadataManager minifilter’s I/O callbacks.

The callbacks demonstrate how a minifilter that keeps an on-volume metadata file open can cooperate with:

- Implicit volume locks from volume opens.
- Explicit `FSCTL_LOCK_VOLUME`, `FSCTL_DISMOUNT_VOLUME`, and `FSCTL_UNLOCK_VOLUME`.
- Volume cleanup/unlock.
- Volume snapshot flush-and-hold-writes.
- Shutdown.
- PnP query remove, cancel remove, and surprise removal.

The recurring pattern is: release metadata references before operations that need exclusive volume access, then reacquire them if the operation fails or the volume becomes usable again.

## `FmmPreCreate`

Handles create/open before the filesystem sees it.

Behavior:

- Defaults to pass-through without post callback.
- Asserts volume-open detection assumptions.
- If target is a volume open:
  - Calls `FmmIsImplicitVolumeLock`.
  - If the create implies a volume lock, calls `FmmReleaseMetadataFileReferences`.
  - On success, requests a post-create callback to determine whether the lock succeeded.
  - On failure, completes the create with the failure status.
- If `VERIFY_METADATA_OPENED` is enabled, requests a post-create callback for non-volume opens.

This is mainly for implicit locks, such as those used by auto-check tools.

## `FmmPostCreate`

Handles post-create completion.

For implicit volume locks:

- If the create/lock failed:
  - Calls `FmmReacquireMetadataFileReferences`.
  - Allows expected failures such as insufficient resources or transition conflict.
- If the create/lock succeeded:
  - Calls `FmmSetMetadataOpenTriggerFileObject` so later cleanup can identify the unlock path.

With verification enabled, successful non-volume creates validate that metadata is open.

The post callback does not fail the already-completed operation.

## `FmmPreCleanup` and `FmmPostCleanup`

`FmmPreCleanup` always returns `FLT_PREOP_SYNCHRONIZE`, forcing a same-thread, low-IRQL post-cleanup callback.

`FmmPostCleanup`:

- Checks volume opens.
- If cleanup succeeded, calls `FmmReacquireMetadataFileReferences`.
- Handles expected failures for dismounted/remounted volumes, invalid device objects, no media, insufficient resources, transition conflicts, and invalid files.

This handles the implicit unlock case where the successful volume-locking handle is cleaned up.

## `FmmPreFSControl`

Handles filesystem-control requests before the filesystem.

Interested FSCTLs:

- `FSCTL_DISMOUNT_VOLUME`
- `FSCTL_LOCK_VOLUME`
- `FSCTL_UNLOCK_VOLUME`

Behavior:

- Ignores non-`IRP_MN_USER_FS_REQUEST` minor functions.
- For lock/dismount on volume opens:
  - Releases metadata references.
  - Requests synchronized post callback if release succeeds.
  - Completes with failure if release fails.
- For unlock:
  - Requests synchronized post callback so metadata can be reacquired after the unlock.

## `FmmPostFSControl`

Handles the result of lock, dismount, and unlock.

### `FSCTL_DISMOUNT_VOLUME`

- On successful dismount:
  - Calls `FltDetachVolume` because the instance is no longer valid.
- On failed dismount:
  - Reacquires metadata references.

### `FSCTL_LOCK_VOLUME`

- On failed lock:
  - Reacquires metadata references.
- On successful lock:
  - Records the target file object as the metadata-open trigger.

### `FSCTL_UNLOCK_VOLUME`

- On successful unlock:
  - Reacquires metadata references.

Expected reacquire failures are treated as sample-tolerated states, generally because the volume may have dismounted/remounted or the instance may be in transition.

## `FmmPreDeviceControl`

Interested IOCTL:

- `IOCTL_VOLSNAP_FLUSH_AND_HOLD_WRITES`

Behavior:

- Gets the instance context.
- Comments explain where a real filter should flush pending metadata and block metadata updates while the snapshot is taking place.
- Passes the instance context as the completion context.
- Requests a post callback.

This sample does not implement real metadata flushing because the metadata contents are not modeled; it shows where that logic belongs.

## `FmmPostDeviceControl`

Handles `IOCTL_VOLSNAP_FLUSH_AND_HOLD_WRITES`.

Behavior:

- Retrieves the instance context from `CbdContext`.
- Comments explain where a real filter should unmark the context and allow metadata updates again.
- Releases the context reference.
- Runs even when draining, so the pre-op context reference is not leaked.

This callback is marked nonpaged in the pragma section.

## `FmmPreShutdown`

On shutdown:

- Calls `FltDetachVolume`.
- Logs failure but does not fail shutdown.
- Returns no post callback.

The sample detaches because the instance is no longer meaningful during shutdown.

## `FmmPrePnp`

Handles selected PnP minor functions.

### `IRP_MN_QUERY_REMOVE_DEVICE`

- Releases metadata references.
- Fails query remove if references cannot be released.

### `IRP_MN_CANCEL_REMOVE_DEVICE`

- Requests synchronized post callback so metadata can be reacquired after the filesystem resumes I/O.

### `IRP_MN_SURPRISE_REMOVAL`

- Detaches the volume instance.

Other PnP minor functions pass through.

## `FmmPostPnp`

Handles `IRP_MN_CANCEL_REMOVE_DEVICE`.

Behavior:

- Asserts the minor function and success status.
- If draining, does nothing.
- Otherwise reacquires metadata references.
- Tolerates insufficient resources and transition conflicts as expected sample cases.

## Callback Registration Implications

The callback behavior assumes the registration in `MetadataManagerInit.c`:

- Create callbacks are optimized to DASD-only unless verification is enabled.
- Cleanup and FSCTL callbacks are synchronized for DASD operations.
- Device control is not restricted to DASD because snapshot IOCTLs are device-level.
- PnP and shutdown callbacks are broad enough to detach or release metadata when volume state changes.

## Research Notes

This file is the operational state machine for metadata ownership:

1. Metadata is normally open while the filter is attached.
2. Before exclusive volume operations, metadata references are dropped.
3. If the exclusive operation fails, metadata is reopened.
4. If the exclusive operation succeeds, the triggering file object is remembered.
5. Cleanup/unlock/cancel remove uses that trigger to reopen metadata.
6. Dismount, shutdown, and surprise removal detach the instance instead.

The code is intentionally conservative: post-operation failures are logged/asserted but do not attempt to rewrite already-completed filesystem results.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/operations.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/pch.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/pch.h

## Purpose

`pch.h` is the precompiled-header include file for the MetadataManager minifilter sample.

It centralizes warning policy and common includes for all source files in the project.

## Include Guard

The file uses:

```c
#ifndef __FMM_PCH_H__
#define __FMM_PCH_H__
...
#endif __FMM_PCH_H__
```

The trailing token after `#endif` is nonstandard style but accepted by the Windows compiler environment this sample targets.

## Warning Policy

The file promotes several warnings to errors:

- `4100`: unreferenced formal parameter.
- `4101`: unreferenced local variable.
- `4061`: missing enumeration value in switch.
- `4505`: unreferenced local function.

This forces the sample to explicitly mark unused parameters and keep switch/function hygiene tight.

## Included Headers

The common include set is:

- `<fltKernel.h>`: Filter Manager and kernel APIs.
- `<dontuse.h>`: WDK header that discourages unsafe APIs.
- `<suppress.h>`: WDK suppression support.
- `"MetadataManagerStruc.h"`: structures/constants/debug macros.
- `"MetadataManagerProc.h"`: function prototypes and resource helpers.

## Research Notes

This file establishes the build environment for the minifilter sample. All project C files include it, so its warning policy and header order affect the entire MetadataManager sample.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/pch.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/support.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/support.c

## Purpose

`support.c` implements small support routines for the MetadataManager minifilter sample.

It provides:

- Unicode string allocation/free helpers.
- Volume-open detection.
- Implicit volume-lock detection.

These helpers are used by `DataStore.c` and `operations.c`.

## `FmmAllocateUnicodeString`

Allocates a paged-pool Unicode buffer using `ExAllocatePoolZero`.

Inputs and behavior:

- The caller sets `String->MaximumLength`.
- The function allocates that many bytes with `FMM_STRING_TAG`.
- On success:
  - `String->Buffer` is set.
  - `String->Length` is reset to zero.
  - Returns `STATUS_SUCCESS`.
- On allocation failure:
  - Logs a debug error.
  - Returns `STATUS_INSUFFICIENT_RESOURCES`.

This helper is used while constructing full metadata filenames.

## `FmmFreeUnicodeString`

Frees a Unicode string allocated by `FmmAllocateUnicodeString`.

Behavior:

- Calls `ExFreePoolWithTag` with `FMM_STRING_TAG`.
- Resets `Length`, `MaximumLength`, and `Buffer`.

The routine assumes the buffer is non-null and owned by this helper.

## `FmmTargetIsVolumeOpen`

Determines whether the callback target is a volume file object.

Behavior:

- Returns true when:
  - `Cbd->Iopb->TargetFileObject` is non-null, and
  - the target file object has `FO_VOLUME_OPEN`.
- Returns false otherwise.

This is used throughout operation callbacks to restrict metadata release/reacquire logic to volume opens.

## `FmmIsImplicitVolumeLock`

Determines whether a create/open on a volume implies a volume lock.

Behavior:

1. Gets the instance context from `Cbd->Iopb->TargetInstance`.
2. Reads `Cbd->Iopb->Parameters.Create.ShareAccess`.
3. Switches on the attached filesystem type.
4. For ReFS, NTFS, and FAT:
   - Treats the open as an implicit volume lock when the caller does not allow `FILE_SHARE_WRITE` or `FILE_SHARE_DELETE`.
5. For other filesystems:
   - Returns `STATUS_INVALID_PARAMETER`.
6. Releases the instance context before returning.

The operation is considered an implicit lock because denying write/delete sharing requires other writable/deletable handles on the volume to be absent, so the filter must close its own metadata file to let the open succeed.

## Supported Filesystems

The implicit-lock logic recognizes:

- `FLT_FSTYPE_REFS`
- `FLT_FSTYPE_NTFS`
- `FLT_FSTYPE_FAT`

This matches the attach policy in `FmmInstanceSetup`.

## Research Notes

`support.c` is small but important to callback correctness. `FmmTargetIsVolumeOpen` prevents ordinary file opens from triggering volume metadata release logic, and `FmmIsImplicitVolumeLock` lets the sample cooperate with tools that lock a volume by opening it with restrictive sharing rather than by issuing an explicit FSCTL.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/support.c -->