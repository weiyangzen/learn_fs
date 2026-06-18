# Group Research: group_1684_reactos_sources_windows_reactos_drivers_filesystems_fastfat_cleanup_220d68b2ab7a

Scope: `Docs/research_subset_a.md`, source tree `sources/windows/reactos`, FastFAT cleanup/close path.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/cleanup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/cleanup.c

## Purpose

`cleanup.c` implements FastFAT `IRP_MJ_CLEANUP`, the handle-close phase that runs when the last user handle for a file object is closed. This is where FastFAT releases share access, drains locks and directory notifications tied to the handle, applies delete-on-close semantics, writes final directory-entry state, tears down cache maps for the closing file object, optionally flushes deferred-flush media, and marks the file object with `FO_CLEANUP_COMPLETE`. The FCB/DCB can remain alive after cleanup because section objects, cache maps, or other references may still exist; final structure teardown is handled later by close.

## Key Entry Points

- `FatFsdCleanup`: dispatches cleanup IRPs, succeeds FSDO cleanup directly, creates a waitable `IRP_CONTEXT`, calls `FatCommonCleanup`, and routes exceptions through FastFAT exception handling.
- `FatCommonCleanup`: decodes the file object, handles all open types, performs delete/truncate-on-close work, removes share access, drains locks, decrements unclean counts, uninitializes cache maps, and flushes deferred-flush media.
- `FatAutoUnlock`: clears VPB/VCB lock state under the VPB spin lock when the closing volume handle owned the volume lock.

## Cleanup Flow

- Repeated cleanup: if `FO_CLEANUP_COMPLETE` is already set, only a needed deferred-flush modified-file flush is attempted, then the IRP completes successfully.
- Locking: user files/directories acquire the FCB exclusively; possible last-handle deletion escalates to VCB then FCB in correct lock order; user volume opens acquire the VCB exclusively.
- Delete-on-close transfer: `CCB_FLAG_DELETE_ON_CLOSE` is moved to `FCB_STATE_DELETE_ON_CLOSE` and cleared from the CCB to avoid repeated oplock-break attempts.
- Verification: `FatVerifyFcb` runs inside expected-status exception handling so cleanup can continue best-effort after ordinary verify/media failures.

## Open-Type Behavior

- `DirectoryFile` / `VirtualVolumeFile`: no user cleanup or share-access removal.
- `UserVolumeOpen`: completes pending dismount, flushes modified writable volume handles and sets verify, unlocks the volume if owned by this file object, and removes `Vcb->ShareAccess`.
- `EaFile`: no share-access cleanup.
- `UserDirectoryOpen`: cleans notify IRPs, may mark delayed close, clears deny-defrag ownership, updates the dirent, deletes empty delete-on-close directories, removes names, reports remove notifications, and decrements `UncleanCount`.
- `UserFileOpen`: removes byte-range locks, may mark delayed close, updates dirent state, handles delete-on-close truncation/deletion, zeroes VDL-to-EOF gaps, purges cached sections when cached handles give way to noncached handles, uninitializes the cache map, and decrements `UncleanCount` plus `NonCachedUncleanCount` as needed.

## Oplock, Cache, and Flush Behavior

- Windows 8+ delete-on-close cleanup uses `FsRtlCheckOplockEx` with `OPLOCK_FLAG_CLOSING_DELETE_ON_CLOSE`; pending breaks mark `IRP_CONTEXT_FLAG_CLEANUP_BREAKING_OPLOCK` and skip final IRP completion.
- Normal user-file cleanup, and user-directory cleanup on Windows 8+ paths, coordinates with oplocks and recomputes fast-I/O state.
- Parent directory oplock breaks after name removal are advisory and asserted non-pending.
- Deferred-flush writable media flush modified user files, optionally flush FAT and parent directory state, and normalize/raise flush failures.
- `CcUninitializeCacheMap` is central for user files, with truncate hints used after truncate-on-close or bad FCB state.

## Dependencies and Interactions

- Depends on `fatprocs.h` for FastFAT structures, file-object decoding, FCB/VCB locking, exception handling, dirent update/delete, allocation truncation, tunneling, notifications, oplock lookup, cache flushing, and request completion.
- Coordinates with I/O manager share access and file-object flags, FSRTL notify/oplock/lock packages, cache manager sizing/flush/purge APIs, and VPB spin-lock state.
- Produces state consumed by `close.c`, especially delayed-close flags, open/unclean counts, delete-on-close state, and cache-map teardown results.

## Important Invariants

- Cleanup is handle-oriented; close is reference-oriented.
- `UncleanCount` is decremented exactly once for user files/directories after per-handle cleanup work.
- Delete-on-close state is promoted from CCB to FCB before oplock handling.
- Name removal on delete-on-close protects in-memory namespace correctness even if on-disk deletion only partially succeeds.
- Resource release and IRP completion are centralized in the `finally` block, except pending oplock cleanup intentionally avoids completion.

## Notable Risks

- Delete/truncate-on-close is best-effort around expected disk/verify errors, so later close/dismount must tolerate partial deletion state.
- Correctness depends on careful lock escalation from FCB-only to VCB+FCB before deletion.
- Cache coherency depends on updating both FCB VDL state and cache-manager file sizes after zeroing.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/cleanup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/close.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/close.c

## Purpose

`close.c` implements FastFAT `IRP_MJ_CLOSE`, the final reference-release phase for file objects. It tears down CCBs, decrements open counters, releases internal stream references, deletes unreferenced FCB/DCB structures, checks whether a volume can dismount, and manages asynchronous/delayed close queues when close work cannot or should not run synchronously.

## Key Entry Points

- `FatFsdClose`: dispatches close IRPs, decodes the file object, records read-only CCB state, handles close-without-cleanup oplock cleanup on Windows 8+ paths, and either runs `FatCommonClose` or queues a close context.
- `FatCloseWorker`: work-item shim that enters the filesystem and calls `FatFspClose`.
- `FatFspClose`: drains queued close contexts, optionally batching same-VCB closes while avoiding holding the VCB across final volume teardown.
- `FatQueueClose`: inserts close contexts into async or delayed close queues and starts the worker when required.
- `FatRemoveClose`: removes queued closes from global or per-VCB lists, prioritizing async closes and delayed closes under pressure or shutdown.
- `FatCommonClose`: common teardown path for all open types.

## Queueing Model

- `FatFsdClose` waits only when the request is top-level and not from FastFAT’s own process.
- A close is queued if `FatCommonClose` returns `STATUS_PENDING`, or if cleanup marked a user file/directory with `FCB_STATE_DELAY_CLOSE` and shutdown has not started.
- Metadata streams allocate a pool close context while the VCB is still guaranteed alive.
- User opens reuse the CCB-embedded `CloseContext` after freeing overlapping query-template strings, avoiding allocation in the close path.
- Async closes always start the worker if inactive; delayed closes start it only when `FatData.DelayedCloseCount > FatMaxDelayedCloseCount`.

## Queue Mechanics

- Global and per-VCB queue entries are updated together under `FatCloseQueueMutex`.
- Global worker removal checks async closes first, then delayed closes above half the configured limit or during shutdown.
- Per-volume removal drains that VCB’s async list, then delayed list.
- High-water flags (`HighAsync`, `HighDelayed`) switch on above twice the delayed-close limit and off below the normal limit, allowing the worker to prefer the last VCB and reuse expensive VCB acquisitions.

## Worker Batching

- `FatFspClose` may keep a VCB resource held while draining multiple closes from the same volume.
- After about 20 same-volume closes, it releases/reacquires if waiters exist to reduce starvation.
- It drops the VCB before a close that may delete the volume (`OpenFileCount <= 1`) because `FatCommonClose` may acquire global state and tear down the VCB.
- If shutdown starts while draining, any held VCB is released.

## Open-Type Behavior in `FatCommonClose`

- `UnopenedFileObject`: returns success.
- `VirtualVolumeFile`: decrements `InternalOpenCount` and `ResidualOpenCount`.
- `UserVolumeOpen`: decrements direct-access/open/read-only counts and deletes the CCB.
- `EaFile`: decrements internal and residual open counts.
- `DirectoryFile`: decrements directory-file/internal counts, decrements residual count for root DCB streams, and returns early on recursive close.
- `UserDirectoryOpen` / `UserFileOpen`: uninitializes no-longer-needed directory stream cache maps, dereferences stream file objects, decrements FCB/VCB counts, updates read-only count, and deletes the CCB.

## FCB/DCB and VCB Teardown

- Normal FCBs are deleted when `OpenCount == 0`.
- Non-root DCBs are deleted when their child queue is empty, `OpenCount == 0`, and `DirectoryFileOpenCount == 0`.
- Deletion sets `VCB_STATE_FLAG_DELETED_FCB`.
- Parent DCBs are walked upward, uninitializing/dereferencing parent directory stream objects and deleting parents that become fully unreferenced.
- Non-recursive close adds a temporary `OpenFileCount` bias to keep the VCB alive through dismount checks.
- If only the biased open remains, the VCB is not good, dismount is not already in progress, and the top-level caller can handle deletion, the code reacquires locks in global-before-VCB order and calls `FatCheckForDismount`.

## Dependencies and Interactions

- Relies on `cleanup.c` to remove share access, locks, notifications, and set delayed-close eligibility.
- Uses `FatData` global async/delayed close lists, counts, pressure flags, shutdown state, close worker item, close mutex, and process identity.
- Coordinates with cache manager through `CcUninitializeCacheMap` and object manager through `ObDereferenceObject`, which can trigger recursive closes.
- Uses `FatDeleteCcb`, `FatDeleteFcb`, `FatCheckForDismount`, and shared FastFAT resource helpers.

## Important Invariants

- User close deferral must not allocate after the decision to queue; the CCB supplies the context.
- Global and per-VCB close-list membership must remain consistent.
- Dismount lock ordering requires dropping VCB and reacquiring global before VCB.
- Recursive directory stream closes are controlled by `VCB_STATE_FLAG_CLOSE_IN_PROGRESS`.
- The temporary VCB open-count bias prevents VCB deletion while close decides whether dismount is possible.

## Notable Risks

- Queue counter/list mismatches could strand close contexts or corrupt close queues.
- Worker batching must drop the VCB before possible final volume teardown.
- Parent DCB deletion depends on `ObDereferenceObject` side effects, including recursive close IRPs.
- Close-without-cleanup only does oplock cleanup; ordinary ordering still expects cleanup to have performed per-handle teardown.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/close.c -->