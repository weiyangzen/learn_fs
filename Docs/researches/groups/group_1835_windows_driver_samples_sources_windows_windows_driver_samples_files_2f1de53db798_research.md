# Group Research: group_1835_windows_driver_samples_sources_windows_windows_driver_samples_files_2f1de53db798

Scope checked against `Docs/research_subset_a.md`: `sources/windows/windows-driver-samples` is included in subset A. Both listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/cleanup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/cleanup.c

## Purpose

`cleanup.c` implements FastFAT handling for `IRP_MJ_CLEANUP`, the operation issued when the last user handle to a file object is closed. The file explicitly distinguishes cleanup from close: cleanup makes the file/directory available to other users and performs user-visible teardown, while the FCB/DCB can remain alive because memory manager or cache manager references may still exist.

The implementation covers:

- FSD dispatch entry for cleanup.
- Shared cleanup logic for file, directory, volume, metadata, and unopened objects.
- Delete-on-close processing.
- Share access removal.
- Cache map uninitialization and truncation coordination.
- File-lock release.
- Deferred-flush media handling.
- Oplock cleanup and delete-on-close oplock breaks for Windows 8+.
- Volume auto-unlock on cleanup of the locking handle.

## Main Entry Points

### `FatFsdCleanup`

Lines 47-139 implement the dispatch routine for `IRP_MJ_CLEANUP`.

Control flow:

1. If the request targets the filesystem device object rather than a mounted volume device object, it completes the IRP with `STATUS_SUCCESS`.
2. Enters filesystem context with `FsRtlEnterFileSystem`.
3. Marks/checks top-level IRP state using `FatIsIrpTopLevel`.
4. Creates an IRP context with blocking allowed via `FatCreateIrpContext(Irp, TRUE)`.
5. Calls `FatCommonCleanup`.
6. Routes exceptions through `FatExceptionFilter` and `FatProcessException`.
7. Clears top-level IRP state when owned and exits filesystem context.

This routine is a thin wrapper; all substantive cleanup behavior is in `FatCommonCleanup`.

### `FatCommonCleanup`

Lines 142-1154 implement common cleanup semantics.

Inputs are decoded from the IRP stack file object using `FatDecodeFileObject`, yielding:

- `TypeOfOpen`
- `Vcb`
- `Fcb`
- `Ccb`

The routine handles all open types, updates FCB/VCB state, and completes the IRP except when an oplock break returns `STATUS_PENDING`.

### `FatAutoUnlock`

Lines 1156-1178 clears volume lock state under the VPB spin lock.

It clears `VPB_LOCKED`, `VPB_DIRECT_WRITES_ALLOWED`, `VCB_STATE_FLAG_LOCKED`, and `Vcb->FileObjectWithVcbLocked`.

## Cleanup Flow

### Unopened File Object

If `FatDecodeFileObject` returns `UnopenedFileObject`, cleanup immediately completes successfully. The comments identify this as a special case during VCB initialization and stream file object creation.

### Repeated Cleanup

If `FO_CLEANUP_COMPLETE` is already set, cleanup does not repeat full teardown. It only performs a deferred flush for modified user file opens on deferred-flush, writable media, then completes successfully.

This makes cleanup idempotent for repeated entry paths while preserving flush behavior that may still be required.

### Resource Acquisition

For `UserFileOpen` and `UserDirectoryOpen`, the FCB is acquired exclusive because cleanup may alter allocation or call `CcUninitializeCacheMap`.

If delete-on-close may become the final close-visible cleanup action, the routine drops the FCB, acquires the VCB exclusive first, then reacquires the FCB. This preserves VCB-before-FCB lock ordering for deletion paths.

For `UserVolumeOpen`, the VCB is acquired exclusive.

A `finally` block releases any acquired FCB/VCB resources, sends volume unlock notification if needed, and completes the IRP on normal non-pending termination.

## Delete-On-Close Handling

Cleanup transfers delete-on-close state from the CCB to the FCB:

- If `CCB_FLAG_DELETE_ON_CLOSE` is set, it sets `FCB_STATE_DELETE_ON_CLOSE`.
- It clears the CCB flag to avoid repeated oplock break attempts on re-entry.
- It marks `ProcessingDeleteOnClose`.

For directories, it notifies the directory change package when delete-on-close is observed.

On Windows 8+, if processing delete-on-close for an oplockable file or empty directory, `FsRtlCheckOplockEx` is called with `OPLOCK_FLAG_CLOSING_DELETE_ON_CLOSE`. If it returns `STATUS_PENDING`, the IRP context is marked with `IRP_CONTEXT_FLAG_CLEANUP_BREAKING_OPLOCK`, and cleanup exits pending.

### Directory Delete-On-Close

For `UserDirectoryOpen`, after updating the dirent from the FCB, the routine checks:

- Last unclean handle: `Fcb->UncleanCount == 1`
- Node is a DCB
- FCB is marked delete-on-close
- FCB condition is good
- Volume is not write-protected

If the directory is not empty, delete-on-close is cleared. If it is empty:

1. Save delete context fields: file size and first cluster.
2. Acquire paging I/O resource.
3. Set file size to zero.
4. Truncate allocation to zero.
5. If allocation reaches zero, tunnel the name, delete the dirent, and report `FILE_ACTION_REMOVED`.
6. Remove names from FastFAT name tables so a same-name recreate does not collide before close arrives.
7. On Windows 8+, break the parent directory oplock with parent/removal flags.

Expected filesystem exceptions in this deletion sequence are caught and converted into reset exception state rather than escaping.

### File Delete-On-Close

For `UserFileOpen`, when this is the final unclean handle and the file is good:

1. If delete-on-close is set and media is writable:
   - Save delete context fields.
   - Acquire paging I/O resource.
   - Set file size and valid data length to zero.
   - Reset `ValidDataToDisk`.
   - Persist file size in the dirent using `FatSetFileSizeInDirent`.
   - Mark `FCB_STATE_TRUNCATE_ON_CLOSE`.

2. Later, if `FCB_STATE_TRUNCATE_ON_CLOSE` is set:
   - Truncate allocation to current file size.
   - Set `TruncateSize` for cache map teardown.
   - Clear `FCB_STATE_TRUNCATE_ON_CLOSE`.

3. If delete-on-close remains set and allocation is zero:
   - Tunnel the name.
   - Delete the dirent.
   - Report file-name removal.

4. Regardless of whether truncation and dirent removal succeeded, if delete-on-close remains set:
   - Remove names from internal lookup structures.
   - On Windows 8+, issue advisory parent directory oplock break.

This code deliberately prioritizes removing the name from in-memory lookup even when on-disk deletion is incomplete, preventing immediate recreate collisions before final close.

## Non-Delete File Finalization

For non-delete final file cleanup, if valid data length is below file size, the routine zeroes the range between VDL and EOF unless the file is a paging file. It uses the greater of `Header.ValidDataLength` and `ValidDataToDisk`, rechecks against file size, calls `FatZeroData`, then advances both VDL and `ValidDataToDisk` to file size.

If the file is cached, `CcSetFileSizes` is called so cache manager state reflects the updated size/VDL relationship and avoids stale optimized zero-page behavior.

## Per-Open-Type Behavior

### `DirectoryFile` and `VirtualVolumeFile`

No share access cleanup is needed. These are internal stream-style opens.

### `UserVolumeOpen`

Handles DASD/volume open cleanup:

- If `CCB_FLAG_COMPLETE_DISMOUNT` is set, calls `FatCheckForDismount`.
- Else, if the handle had write access and modified data, flushes the target device with `FatHijackIrpAndFlushDevice` and marks the real device for verify using `DO_VERIFY_VOLUME`.
- If this file object locked the VCB, calls `FatAutoUnlock` and later sends `FSRTL_VOLUME_UNLOCK`.
- Uses `Vcb->ShareAccess` for share-access removal.

### `EaFile`

No share access cleanup is needed.

### `UserDirectoryOpen`

Major actions:

- Uses `Fcb->ShareAccess`.
- Marks `FCB_STATE_DELAY_CLOSE` when the directory has no remaining useful user or directory-file opens and is not being deleted.
- Clears `FCB_STATE_DENY_DEFRAG` if this CCB set `CCB_FLAG_DENY_DEFRAG`.
- Updates the dirent from FCB while the VCB is good and not shutdown.
- Performs directory delete-on-close logic.
- Decrements `Fcb->UncleanCount`.

### `UserFileOpen`

Major actions:

- Uses `Fcb->ShareAccess`.
- Marks `FCB_STATE_DELAY_CLOSE` for final nonmapped, nonpaging, nondelete, good file opens.
- Clears defrag-denial state owned by this CCB.
- Unlocks all outstanding byte-range locks with `FsRtlFastUnlockAll`.
- Updates dirent when mounted and good.
- Handles delete-on-close or VDL zeroing.
- Truncates allocation when required.
- Deletes dirent and removes names when required.
- Decrements `UncleanCount`; decrements `NonCachedUncleanCount` for noncached file objects.
- If the final cached handle is closing while noncached handles remain, flushes/purges cache to reduce coherency overhead.
- Sets `TruncateSize` to zero for bad FCBs to hint cache teardown should discard everything.
- Calls `CcUninitializeCacheMap`.

## Share Access and Oplocks

After open-type-specific cleanup, if `ShareAccess` is non-null, `IoRemoveShareAccess` is called. This happens during cleanup rather than close because close may be delayed by mapped-file references.

For user file opens, and for user directory opens on Windows 8+, cleanup calls `FsRtlCheckOplock` to coordinate cleanup with oplock state. Cleanup is allowed to proceed immediately. It then recomputes `Header.IsFastIoPossible`.

Delete-on-close uses stronger Windows 8+ oplock handling via `FsRtlCheckOplockEx`, including a possible pending return before actual deletion proceeds.

## Cache and Flush Behavior

Cache manager interactions include:

- `CcSetFileSizes` after explicit zeroing to EOF.
- `CcFlushCache` and `CcPurgeCacheSection` when cached handles give way to remaining noncached handles.
- `CcUninitializeCacheMap` during user file cleanup, with truncation hint if applicable.

Deferred flush media logic near the end checks `VCB_STATE_FLAG_DEFERRED_FLUSH` and writable media. It flushes modified user files with `FatFlushFile`. If needed, it flushes FAT state via `FatFlushFat` and also flushes the parent directory. Failure is normalized and raised.

Repeated cleanup also uses deferred file flush for modified user files.

## Locking and Synchronization

Important synchronization mechanisms:

- FCB exclusive acquisition for user file/directory cleanup.
- VCB exclusive acquisition for volume cleanup and final delete-on-close paths.
- Paging I/O resource around direct file-size/VDL changes.
- VPB spin lock in `FatAutoUnlock`.
- Cache manager synchronization through flush, purge, and uninitialize calls.
- `try/finally` cleanup around acquired resources.

The code is careful about lock ordering when deletion may need both VCB and FCB: it reacquires in VCB-first order.

## Error Handling

The file uses structured exception handling heavily:

- Top-level dispatch catches through `FatExceptionFilter` and `FatProcessException`.
- `FatVerifyFcb` exceptions expected by FsRtl are swallowed after `FatResetExceptionState`.
- Delete/truncate/dirent update sequences catch expected exceptions and reset exception state.
- Deferred flush failures are normalized and raised.
- `finally` ensures resources are released and IRP completion occurs unless pending.

The delete-on-close code often continues after expected errors because by cleanup time the user-visible close state cannot be fully rolled back.

## Key State Mutations

Important FCB/CCB/VCB/FileObject state touched:

- `FO_CLEANUP_COMPLETE`
- `FO_FILE_MODIFIED`
- `CCB_FLAG_DELETE_ON_CLOSE`
- `CCB_FLAG_DENY_DEFRAG`
- `FCB_STATE_DELETE_ON_CLOSE`
- `FCB_STATE_DELAY_CLOSE`
- `FCB_STATE_DENY_DEFRAG`
- `FCB_STATE_TRUNCATE_ON_CLOSE`
- `FCB_STATE_FLUSH_FAT`
- `VCB_STATE_FLAG_DEFERRED_FLUSH`
- `VCB_STATE_FLAG_WRITE_PROTECTED`
- `VCB_STATE_FLAG_LOCKED`
- `VCB_STATE_FLAG_SHUTDOWN`
- `UncleanCount`
- `NonCachedUncleanCount`
- `ValidDataToDisk`
- `Header.FileSize`
- `Header.ValidDataLength`

## Relationship to `close.c`

This file performs handle-level cleanup and can mark FCBs for delayed close with `FCB_STATE_DELAY_CLOSE`. `close.c` later observes that flag and can queue actual object teardown to the delayed close worker. Cleanup also removes share access early because the close IRP may not arrive until later due to mapped sections or cache manager references.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/cleanup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/close.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/close.c

## Purpose

`close.c` implements FastFAT handling for `IRP_MJ_CLOSE`, which runs when the final reference to a file object is deleted. Unlike cleanup, close tears down in-memory structures: CCBs, FCBs/DCBs, internal stream references, and possibly the VCB during dismount.

The file also implements FastFAT’s async and delayed close queues. This lets the FSD close path avoid blocking or expensive teardown in unsafe contexts, while still allowing deferred cleanup of unreferenced objects.

## Main Entry Points

### `FatFsdClose`

Lines 79-319 implement the FSD dispatch routine for `IRP_MJ_CLOSE`.

Main responsibilities:

1. Complete immediately for filesystem device object requests.
2. Enter filesystem context.
3. Determine top-level IRP state.
4. Decode the file object into `Vcb`, `Fcb`, `Ccb`, and `TypeOfOpen`.
5. Preserve read-only file-object state in the CCB via `CCB_FLAG_READ_ONLY`.
6. On Windows 8+, if close arrives without prior cleanup, clean oplock state with `FsRtlCheckOplockEx`.
7. Preallocate close context for metadata stream opens.
8. Call `FatCommonClose` unless the FCB is marked for delayed close.
9. Queue close work if common close returns `STATUS_PENDING` or delayed close is requested.
10. Complete the IRP with success.

The close IRP itself is completed even when actual object teardown is queued for later.

### `FatCloseWorker`

Lines 321-352 is the I/O work item shim. It enters filesystem context, calls `FatFspClose(Context)`, then exits filesystem context.

### `FatFspClose`

Lines 355-550 drains queued close contexts, optionally for a specific VCB.

It is the worker/FSP-side close processor and repeatedly removes close contexts using `FatRemoveClose`, then calls `FatCommonClose` with `Wait = TRUE`.

### `FatQueueClose`

Lines 553-622 enqueues a `CLOSE_CONTEXT` onto either:

- Global and per-VCB delayed close lists, or
- Global and per-VCB async close lists.

It starts the worker item when thresholds or active-state rules require it.

### `FatRemoveClose`

Lines 625-826 removes a queued close context from global or per-VCB queues. It prioritizes async closes, then delayed closes under threshold/shutdown rules, and has pressure logic to favor the previous VCB when queues grow too high.

### `FatCommonClose`

Lines 829-1279 performs actual in-memory close teardown.

It acquires the VCB resource, updates open counts, deletes CCBs and FCBs/DCBs when unreferenced, unwinds parent directory stream file objects, and may check for dismount.

## Close Dispatch Behavior

`FatFsdClose` first decodes the file object before creating any heap-backed close context. For read-only file objects, it records `CCB_FLAG_READ_ONLY` so common close can decrement `Vcb->ReadOnlyCount`.

The `Wait` decision is conservative:

- `Wait` is true only when this is a top-level IRP and the current process is not FastFAT’s own process.
- Otherwise, if `FatCommonClose` cannot acquire needed resources, it returns `STATUS_PENDING`, and the close is queued.

For user file or directory opens, if `FCB_STATE_DELAY_CLOSE` is set and shutdown has not started, `FatFsdClose` skips immediate `FatCommonClose` and queues the close as delayed work.

## Close Context Ownership

Close contexts have two storage modes:

- Metadata stream opens (`VirtualVolumeFile`, `DirectoryFile`, `EaFile`) allocate a `CLOSE_CONTEXT` from VCB-managed preallocated close context storage with `FatAllocateCloseContext`; `CloseContext->Free = TRUE`.
- User opens reuse `Ccb->CloseContext`; `CloseContext->Free = FALSE`, and `CCB_FLAG_CLOSE_CONTEXT` is set.

Before using the CCB union field as a close context, `FatFsdClose` calls `FatDeallocateCcbStrings` because query template string storage overlaps with close context fields.

This design avoids allocating memory in the close path for user objects.

## Close Queues

### Queue Types

`FatQueueClose` distinguishes:

- Delayed close: for unreferenced objects intentionally kept around for reuse/efficiency.
- Async close: for closes that could not complete synchronously, usually because locks/resources were unavailable or create/close coordination required deferral.

Both queue types maintain:

- A global list under `FatData`.
- A per-VCB list under the target VCB.

The shared `FatCloseQueueMutex` protects all close lists and counters. Helper macros assert APCs are disabled and use `ExAcquireFastMutexUnsafe` / `ExReleaseFastMutexUnsafe`.

### Worker Start Rules

For delayed closes:

- Increment `FatData.DelayedCloseCount`.
- Start the worker only if delayed close count exceeds `FatMaxDelayedCloseCount` and async close worker is inactive.

For async closes:

- Increment `FatData.AsyncCloseCount`.
- Start the worker whenever no async close worker is active.

### Removal Rules

`FatRemoveClose` prioritizes async close work over delayed close work.

When no specific VCB is requested:

1. Pop from global async close list if nonempty.
2. Else pop from global delayed close list only if delayed count exceeds half the maximum or shutdown has started.
3. Else mark async close worker inactive and return null.

When a specific VCB is requested:

1. Pop from VCB async close list.
2. Else pop from VCB delayed close list.
3. Else, if a last-VCB hint was supplied, fall back to any close.
4. Else return null.

When queue counts grow above twice the delayed close limit, `FatRemoveClose` enters high-pressure mode (`HighAsync` or `HighDelayed`) and may prefer the last VCB hint to amortize expensive VCB acquisitions.

## FSP Close Processing

`FatFspClose` can run globally or for one VCB.

When running globally, it sets top-level IRP to `FSRTL_FSP_TOP_LEVEL_IRP`. It tries to reuse an exclusive VCB acquisition across multiple close contexts for the same VCB. To avoid starving other users of the VCB resource, it periodically releases and reacquires after about 20 loops if waiters exist.

It also avoids holding a VCB across a close that may delete the volume. If `OpenFileCount <= 1`, it releases the VCB before calling `FatCommonClose` because the common close path may tear the VCB down.

Each queued context is closed inside exception handling; expected exceptions are ignored. Pool-backed close contexts are freed after processing.

## Common Close Flow

`FatCommonClose` handles actual teardown and always starts by constructing a stack `IRP_CONTEXT` for close.

Early exits:

- `UnopenedFileObject` returns success.
- If exclusive VCB acquisition fails with `Wait == FALSE`, returns `STATUS_PENDING`.
- If create is in progress and this is not the EA FCB, releases VCB and returns `STATUS_PENDING`.

The routine uses `VCB_STATE_FLAG_CLOSE_IN_PROGRESS` to detect recursive closes. The top close chain biases `Vcb->OpenFileCount` by one so the VCB cannot disappear before final dismount checks.

## Per-Open-Type Behavior

### `VirtualVolumeFile`

Decrements:

- `Vcb->InternalOpenCount`
- `Vcb->ResidualOpenCount`

Then returns success.

### `UserVolumeOpen`

Decrements:

- `Vcb->DirectAccessOpenCount`
- `Vcb->OpenFileCount`
- `Vcb->ReadOnlyCount` if CCB was marked read-only

Deletes the CCB with `FatDeleteCcb`.

### `EaFile`

Decrements:

- `Vcb->InternalOpenCount`
- `Vcb->ResidualOpenCount`

Then returns success.

### `DirectoryFile`

Decrements the directory file open count on the DCB and the VCB internal open count. If the FCB is the root DCB, also decrements residual open count.

If this is a recursive close, it returns success immediately. Otherwise it falls through to shared FCB/DCB deletion logic.

### `UserDirectoryOpen` and `UserFileOpen`

For DCBs, if the directory has no child DCBs, open count is one, and a stream directory file object exists, the code uninitializes that stream cache map, clears `DirectoryFile`, and dereferences the stream file object before destroying the FCB.

Then it decrements:

- `Fcb->OpenCount`
- `Vcb->OpenFileCount`
- `Vcb->ReadOnlyCount` if applicable

It deletes the CCB and proceeds to possible FCB/DCB deletion.

## FCB/DCB Deletion

After per-open-type work, `FatCommonClose` deletes in-memory file structures when no longer referenced.

Deletion conditions:

- For FCB: node type is `FAT_NTC_FCB` and `OpenCount == 0`.
- For DCB: node type is `FAT_NTC_DCB`, parent DCB queue is empty, `OpenCount == 0`, and `DirectoryFileOpenCount == 0`.

When deleting an FCB/DCB:

1. Save `ParentDcb`.
2. Set `VCB_STATE_FLAG_DELETED_FCB`.
3. Call `FatDeleteFcb`.

Then the routine may walk up parent directories. For each parent DCB that has no children, no opens, and a stream directory file object, it:

1. Uninitializes the parent stream cache map.
2. Clears `DirectoryFile`.
3. Dereferences the stream file object.
4. If the dereference caused final close of that directory file object, deletes the parent DCB and continues upward.
5. Otherwise stops and waits for memory manager/file object references to drain later.

This is the core recursive directory teardown logic.

## Dismount and VCB Lifetime

In the `finally` block, if this is the top of the close chain, the routine removes its biased open count and may check for dismount.

It can check for dismount only when:

- `Vcb->OpenFileCount == 1`, meaning only the bias remains.
- `Vcb->VcbCondition != VcbGood`.
- Dismount is not already in progress.
- Caller supplied `VcbDeleted`.
- Request is top level.

Because global lock order requires global before VCB, the code releases the VCB, sets wait mode, acquires global, reacquires VCB, removes the biased open count, and calls `FatCheckForDismount`.

If the VCB was deleted, it avoids releasing it. Otherwise it clears `VCB_STATE_FLAG_CLOSE_IN_PROGRESS` and releases the VCB.

## Oplock Handling

On Windows 8+, `FatFsdClose` accounts for close IRPs that arrive without a prior cleanup. If the file object is not marked `FO_CLEANUP_COMPLETE` and the FCB is oplockable, it calls `FsRtlCheckOplockEx` to clear oplock state immediately. Comments state this is safe only in the FSD path and relies on the oplock package’s own lock rather than FCB locking.

Normal cleanup-time oplock coordination lives in `cleanup.c`; this is a fallback for abnormal close-without-cleanup cases.

## Concurrency and Locking

Important synchronization:

- `FatCloseQueueMutex` protects global/per-VCB close lists and counters.
- VCB resource is acquired exclusive in `FatCommonClose`.
- `VCB_STATE_FLAG_CLOSE_IN_PROGRESS` prevents recursive close handling from re-entering general teardown paths.
- FSP close worker may hold a VCB across several closes but periodically yields when waiters exist.
- Dismount path reacquires locks in global-before-VCB order.

The file is structured to avoid blocking in unsafe FSD close contexts by returning `STATUS_PENDING` and queueing.

## Error Handling

`FatFsdClose` wraps the close process with `FatExceptionFilter` and `FatProcessException`, though it generally completes the IRP after either synchronous or queued handling.

`FatFspClose` catches expected exceptions around `FatCommonClose` and ignores them, allowing the worker to continue draining close contexts.

`FatCommonClose` uses `try/finally` to guarantee biased open count cleanup, close-in-progress flag clearing, VCB release, and dismount handling.

## Key State Mutations

Important state touched:

- `FatData.AsyncCloseList`
- `FatData.DelayedCloseList`
- `FatData.AsyncCloseCount`
- `FatData.DelayedCloseCount`
- `FatData.AsyncCloseActive`
- `FatData.HighAsync`
- `FatData.HighDelayed`
- `FCB_STATE_DELAY_CLOSE`
- `CCB_FLAG_READ_ONLY`
- `CCB_FLAG_CLOSE_CONTEXT`
- `VCB_STATE_FLAG_CREATE_IN_PROGRESS`
- `VCB_STATE_FLAG_CLOSE_IN_PROGRESS`
- `VCB_STATE_FLAG_DELETED_FCB`
- `VCB_STATE_FLAG_DISMOUNT_IN_PROGRESS`
- `OpenFileCount`
- `OpenCount`
- `InternalOpenCount`
- `ResidualOpenCount`
- `DirectAccessOpenCount`
- `ReadOnlyCount`
- `DirectoryFileOpenCount`

## Relationship to `cleanup.c`

`cleanup.c` handles user-visible handle cleanup and may set `FCB_STATE_DELAY_CLOSE` when a final cleaned-up file or directory should remain cached briefly. `close.c` consumes that state and decides whether to defer actual FCB/DCB/CCB destruction.

The division is important:

- Cleanup removes share access, byte-range locks, cache maps for user file objects, delete-on-close names, and visible handle state.
- Close removes references and frees in-memory filesystem structures once the object is truly no longer referenced.

Together they model the Windows filesystem distinction between handle lifetime and file object lifetime.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/close.c -->