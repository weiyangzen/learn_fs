# Group Research: group_1671_reactos_sources_windows_reactos_drivers_filesystems_cdfs_cddata_c_s_88575a68ca98

Scope: `Docs/research_subset_a.md`, source tree `sources/windows/reactos`, CDFS filesystem driver internals.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/cddata.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/cddata.c

## Purpose

`cddata.c` owns CDFS global runtime data and the top-level FSD dispatch/exception path. It defines global constants used across the driver, then implements request entry, exception normalization/retry/posting, request completion, thread top-level context tracking, fast-I/O admission, and a simple volume serial checksum helper.

## Key Contents

- Global objects:
  - `CD_DATA CdData`
  - `FAST_IO_DISPATCH CdFastIoDispatch`
  - directory pseudo-names `.` and `..`
  - ISO/HSG/XA volume identifier strings
  - audio CD label and synthetic track filename metadata
  - Joliet escape strings
  - hardcoded RIFF/CDDA/CDXA header templates for audio and XA exposure
  - optional `CDFS_TELEMETRY_DATA_CONTEXT CdTelemetryData`

- `CdFsdDispatch`
  - Main dispatch routine for `IRP_MJ_CREATE`, `CLOSE`, `READ`, `WRITE`, query/set information, volume info, directory control, FS/device/lock control, cleanup, PnP, and shutdown.
  - Enters the filesystem with `FsRtlEnterFileSystem`.
  - Creates an `IRP_CONTEXT` on first pass using `CdCreateIrpContext`.
  - Determines waitability from mount/file-object state via `CanFsdWait`.
  - Sets top-level thread context with `CdSetThreadContext`.
  - Retries while status is `STATUS_CANT_WAIT`.
  - Uses SEH and delegates exception filtering/processing to `CdExceptionFilter` and `CdProcessException`.

- `CdRaiseStatusEx`
  - Debug/sanity-only implementation that records raised status, optional normalization, source file/line encoding, and optional breakpoint behavior.
  - Release inline equivalent is declared in `cdprocs.h`.

- `CdExceptionFilter`
  - Converts `STATUS_IN_PAGE_ERROR` to the underlying I/O error when available.
  - Stores the exception in `IrpContext->ExceptionStatus` if CDFS did not already raise one.
  - Bugchecks for unexpected NTSTATUS values via `FsRtlIsNtstatusExpected`.

- `CdProcessException`
  - Handles posting, retry, verify-required, user-induced errors, hard-error popup generation, and final completion.
  - Posts `STATUS_CANT_WAIT` requests when forced.
  - Posts `STATUS_VERIFY_REQUIRED` when top-level and APCs are disabled.
  - For verify-required, finds or substitutes the real device object and calls `CdPerformVerify`.
  - For other user-induced errors, either completes immediately if popups are disabled or calls `IoRaiseHardError`.
  - Normal errors complete through `CdCompleteRequest`.

- `CdCompleteRequest`
  - Cleans up the `IRP_CONTEXT`.
  - Zeros `IoStatus.Information` for failed input operations.
  - Sets final IRP status and completes via `IoCompleteRequest`.

- `CdSetThreadContext`
  - Manages CDFS top-level request context using `IoGetTopLevelIrp` / `IoSetTopLevelIrp`.
  - Validates existing thread context by stack location, alignment, and signature.
  - ReactOS path uses `IoGetStackLimits` instead of `IoWithinStackLimits`.
  - Marks top-level CDFS ownership with `IRP_CONTEXT_FLAG_TOP_LEVEL_CDFS`.

- `CdFastIoCheckIfPossible`
  - Allows fast I/O only for user file reads.
  - Rejects writes/non-file opens with `STATUS_INVALID_PARAMETER`.
  - Checks byte-range locks with `FsRtlFastCheckLockForRead`.

- `CdSerial32`
  - Builds a 32-bit serial by summing bytes into four checksum lanes and returning them as a `ULONG`.

## Dependencies and Interactions

- Included through `cdprocs.h`, so it depends on all core CDFS structures and declarations.
- Dispatch targets are implemented in operation-specific files such as `create.c`, `read.c`, `cleanup.c`, `close.c`, `fsctrl.c`, etc.
- Exception flow is tightly coupled to `IRP_CONTEXT` fields from `cdstruc.h`.
- Fast I/O checks depend on `CdFastDecodeFileObject`, `CdIsFastIoPossible`, oplock/file-lock state, and FSRTL lock helpers.
- Verify and dismount behavior depends on VCB state and device verification helpers.

## Behavioral Notes

- `STATUS_CANT_WAIT` is an internal retry/posting signal, not a final caller status.
- Top-level context preservation is critical because recursive filesystem entry can occur during cache manager, memory manager, verify, or hard-error paths.
- The file is mostly infrastructure; actual filesystem semantics are delegated through the major-function switch.
- Audio/XA headers expose CD audio and CD-XA data as synthetic RIFF-style files without dynamically allocating these templates per request.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/cddata.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/cddata.h -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/cddata.h

## Purpose

`cddata.h` declares global CDFS data and constants exported from `cddata.c`, plus assertion and locking verification macros used throughout the driver.

## Key Contents

- Extern globals:
  - `CdData`
  - `CdFastIoDispatch`
  - directory name arrays and `CdUnicodeDirectoryNames`
  - descriptor IDs `CdHsgId`, `CdIsoId`, `CdXaId`
  - audio label/name fields and audio dirent sizing values
  - Joliet escape array
  - RIFF/audio header templates
  - optional telemetry context

- Reference-count constants:
  - `CDFS_RESIDUAL_REFERENCE` is `6`.
  - `CDFS_RESIDUAL_USER_REFERENCE` is `3`.
  - Comments explain residual references for mounted VCB, volume DASD FCB, root index/internal stream, and path table/internal stream.

- Audio filename offsets:
  - `AUDIO_NAME_ONES_OFFSET`
  - `AUDIO_NAME_TENS_OFFSET`

- `CD_SANITY` assertion layer:
  - Structure assertions for VCB, FCB, FCB nonpaged, CCB, IRP context, IRP, and file object.
  - Resource ownership assertions for global data, VCB, FCB, file resources, and mutex-style VCB/FCB locks.
  - FCB assertions accept data, index, and path-table node types.
  - In non-sanity builds, these macros compile to `NOTHING`.

## Dependencies and Interactions

- This header assumes node type constants from `nodetype.h` and structures from `cdstruc.h` are already visible through `cdprocs.h`.
- Assertions are used heavily by cleanup, close, resource, and structure-management code.
- The residual reference constants are important to dismount/teardown logic in close and verify paths.

## Behavioral Notes

- In ReactOS/current configuration, `CD_SANITY` is not forcibly enabled; debug code contains a commented-out define.
- Non-sanity builds intentionally remove almost all assertion overhead.
- The header is declarative; the only “logic” is macro validation behavior.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/cddata.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/cdinit.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/cdinit.c

## Purpose

`cdinit.c` implements driver initialization, unload, and global data setup for the ReactOS CDFS driver.

## Key Contents

- `DriverEntry`
  - Creates the primary filesystem device object named `\Cdfs` with type `FILE_DEVICE_CD_ROM_FILE_SYSTEM`.
  - ReactOS additionally creates `\CdfsHdd` with type `FILE_DEVICE_DISK_FILE_SYSTEM`.
  - Installs `CdUnload`.
  - Sets all supported `MajorFunction` entries to `CdFsdDispatch`.
  - Assigns `DriverObject->FastIoDispatch = &CdFastIoDispatch`.
  - Registers filesystem filter callbacks, currently `CdFilterCallbackAcquireForCreateSection`.
  - Calls `CdInitializeGlobalData`.
  - Marks filesystem device objects with `DO_LOW_PRIORITY_FILESYSTEM`.
  - Registers the filesystem device object(s) with `IoRegisterFileSystem`.
  - References registered device objects to keep them alive.
  - Optionally initializes telemetry.

- `CdUnload`
  - Frees cached IRP contexts from `CdData.IrpContextList`.
  - Frees `CdData.CloseItem`.
  - Deletes `CdData.DataResource`.
  - Dereferences filesystem device object(s).

- `CdInitializeGlobalData`
  - Zeros and initializes `CdFastIoDispatch`.
  - Hooks fast-I/O routines:
    - `CdFastIoCheckIfPossible`
    - `FsRtlCopyRead`
    - fast query info routines
    - fast lock/unlock routines
    - network open info
    - MDL read/write helpers
  - Initializes `CdData` node type, driver/device pointers, VCB queue, global resource, cache-manager callbacks, close queues, and mutex.
  - Allocates `CdData.CloseItem`.
  - Sets IRP-context cache depth and delayed-close thresholds based on `MmQuerySystemSize`.

## Dependencies and Interactions

- Uses `CdFsdDispatch` from `cddata.c`.
- Populates the `CdData` structure defined in `cdstruc.h`.
- Initializes delayed/async close infrastructure consumed by `close.c`.
- Cache callbacks point to routines declared in `cdprocs.h`.
- ReactOS-specific dual filesystem registration lets the same CDFS code participate for both CD-ROM and disk-style filesystem device types.

## Behavioral Notes

- Device object flags deliberately do not set direct or buffered I/O because CDFS chooses caching/direct I/O behavior per operation.
- Failure paths delete already-created device objects and abort initialization.
- `CdInitializeGlobalData` may fail only after `CloseItem` allocation failure in this file, returning `STATUS_INSUFFICIENT_RESOURCES`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/cdinit.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/cdprocs.h -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/cdprocs.h

## Purpose

`cdprocs.h` is the central internal interface header for CDFS. It includes platform headers and CDFS structure headers, defines pool tags/macros, and declares or macro-defines almost every cross-file helper used by the filesystem.

## Key Contents

- Includes:
  - NT filesystem/storage headers.
  - ReactOS SEH support via `<pseh/pseh2.h>`.
  - `nodetype.h`, `cd.h`, `cdstruc.h`, and `cddata.h`.
  - Optional telemetry headers.

- ReactOS compatibility:
  - Downgrades newer NX pool and MDL flags to older equivalents.
  - Adds GCC/static-inline annotations for functions that would otherwise conflict.
  - Uses ReactOS SEH macros in `try_leave`.

- Pool tags:
  - Tags for CCBs, TOC buffers, dirent names, enum expressions, FCB variants, I/O buffers, IRP contexts, MCB arrays, prefix entries, path-table buffers, volume descriptors, VPBs, etc.

- Access checks:
  - `CdIllegalFcbAccess` rejects write/delete/security-modifying access for normal readonly CDFS opens, with special casing for volume opens.

- Allocation/cache/device I/O declarations:
  - Logical allocation lookup/update/truncation.
  - Internal stream creation/deletion.
  - MDL completion and purge.
  - Noncached reads including XA reads.
  - raw sector reads and device control helpers.
  - user-buffer mapping and locking macros.

- Directory/path/name support:
  - Dirent lookup, update, search, cleanup, and file enumeration helpers.
  - Path-table lookup/search/update helpers.
  - Prefix-table insert/remove/find.
  - Name conversion, endian conversion, upcasing, dissection, legal-name checks, 8.3 generation, expression matching, and full comparisons.

- File-object contract:
  - Defines `TYPE_OF_OPEN`:
    - `UnopenedFileObject`
    - `StreamFileOpen`
    - `UserVolumeOpen`
    - `UserDirectoryOpen`
    - `UserFileOpen`
  - Declares `CdSetFileObject`, `CdDecodeFileObject`, and `CdFastDecodeFileObject`.

- Synchronization:
  - Declares `CdAcquireResource`.
  - Provides macros for acquiring/releasing CdData, VCBs, all files, individual file resources, FCB resources, and cache resources.
  - Provides fast-mutex lock/unlock macros for CdData, VCB, and recursive FCB locking.
  - Defines `TYPE_OF_ACQUIRE`.

- Structure lifecycle:
  - VCB initialization/update/delete.
  - FCB creation/initialization from path entries or file contexts.
  - CCB creation/delete.
  - file-lock creation/delete.
  - IRP context create/cleanup/stack initialization.
  - teardown routines and reference/cleanup count macros.
  - FCB table lookup and TOC processing.

- Verification/work queue:
  - Verify-required handling, dismount checks, marking verify flags, VCB/Fcb operation verification.
  - FSD post/prepost and oplock completion routines.

- Dispatch/exception/fast I/O:
  - Prototypes for `CdFsdDispatch`, `CdExceptionFilter`, `CdProcessException`, `CdCompleteRequest`, and `CdSetThreadContext`.
  - Inline `CdRaiseStatusEx` for non-`CD_SANITY` builds.
  - Fast I/O entry declarations.
  - Common major-function worker declarations for create, close, read, write, info, volume info, dir control, FS control, device control, lock control, cleanup, PnP, and shutdown.

- Utility macros:
  - pointer arithmetic
  - word/long/quad alignment
  - sector/block conversions
  - unaligned copy and endian swap helpers
  - `CdIsFastIoPossible`
  - `CanFsdWait`
  - safe pool free wrapper

- Optional telemetry:
  - provider declaration, initialization/mount hooks, stack guard, and no-op macros when telemetry is disabled.

## Dependencies and Interactions

- This header binds the entire CDFS module set together; every `.c` file in this group includes it directly or indirectly.
- It depends on `cdstruc.h` for concrete structure layouts and `cddata.h` for global declarations/assertions.
- Many macros assume caller-held resources or global critical region state, as indicated by SAL annotations.
- Several macros mutate VCB/FCB counts directly and require the VCB fast mutex.

## Behavioral Notes

- The file mixes declarations and behavior-heavy macros. Changing a macro here can alter locking, exception, or memory semantics across the whole driver.
- `CdIsFastIoPossible` encodes the fast-I/O policy: mounted volume, compatible oplock state, and file-lock state.
- `CdRaiseStatus` and `CdNormalizeAndRaiseStatus` capture source file ID and line into the IRP context before raising.
- ReactOS compatibility comments identify places where upstream Windows CDFS code needed GCC or kernel-version adaptation.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/cdprocs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/cdprocssrc.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/cdprocssrc.c

## Purpose

`cdprocssrc.c` is a one-line source file that includes `cdprocs.h`.

## Key Contents

- Sole content:
  - `#include "cdprocs.h"`

## Dependencies and Interactions

- Pulls in the entire CDFS internal declaration stack.
- Likely exists as a build helper/translation unit to force header parsing or satisfy source-list conventions.

## Behavioral Notes

- Contains no functions, variables, or executable logic.
- Any compile effect comes exclusively from included headers and inline/static declarations.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/cdprocssrc.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/cdstruc.h -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/cdstruc.h

## Purpose

`cdstruc.h` defines the core in-memory CDFS data model: global filesystem state, mounted volume state, file/control blocks, per-open context, request context, enumeration contexts, RIFF/audio headers, file IDs, and optional telemetry state.

## Key Contents

- Design commentary:
  - Describes `CdData`, filesystem device objects, volume device objects, VCB queue, FCB table, root/index/file tree, prefix tables, file-object context pointers, and synchronization order.
  - Establishes normal lock ordering: CdData, VCB, FCB, with special FCB tree ordering rules.

- Allocation/name/prefix primitives:
  - `CD_MCB` and `CD_MCB_ENTRY` map file offsets to disk offsets and support interleaved/raw sector layouts.
  - `CD_NAME` stores filename and version string.
  - `NAME_LINK` and `PREFIX_ENTRY` support exact-case and ignore-case prefix splay trees.

- `CD_DATA`
  - Global filesystem record.
  - Holds driver/device pointers, VCB queue, IRP context cache, async/delayed close queues, close worker item, global mutex/resource, and cache-manager callbacks.
  - ReactOS adds `HddFileSystemDeviceObject`.

- `CDROM_TOC_LARGE`
  - Larger TOC representation supporting up to `0xAA` track entries.

- Sector cache:
  - `CD_SECTOR_CACHE_CHUNK`
  - `CD_SEC_CACHE_CHUNKS`
  - `CD_SEC_CHUNK_BLOCKS`

- `VCB`
  - Mounted volume control block with VPB, target device, volume lock file object, queue links, state/condition, cleanup/reference counts, special FCBs, session/descriptor offsets, XA sector cache, resources, mutex, notify state, logical block geometry, FCB table, TOC data, media-change count, transfer limits, swap VPB, directory sector cache, and optional telemetry correlation ID.
  - Conditions:
    - `VcbNotMounted`
    - `VcbMountInProgress`
    - `VcbMounted`
    - `VcbInvalid`
    - `VcbDismountInProgress`
  - State flags include ISO/HSG/Joliet, locked, removable, CD-XA, audio disk, notify remount, VPB detached, shutdown, and dismounted.

- `VOLUME_DEVICE_OBJECT`
  - Embeds an I/O `DEVICE_OBJECT`, overflow queue accounting/lock, and the filesystem `VCB`.

- FCB family:
  - `FCB_DATA` contains oplock state on pre-Win8 and optional file-lock pointer.
  - `FCB_INDEX` contains internal stream file object, stream offset, child FCB queue, path-table ordinal/child offsets, and prefix roots.
  - `FCB_NONPAGED` contains section object pointers, FCB resource, FCB mutex, and advanced-header mutex.
  - `FCB` embeds `FSRTL_ADVANCED_FCB_HEADER`, VCB/parent links, file ID, reference/cleanup counts, state, attributes, XA metadata, recursive lock state, nonpaged block, share access, MCB, prefix entries, creation time, and either data or index-specific payload.
  - FCB state flags identify initialized/table membership and raw-sector file types.

- `CCB`
  - Per-handle state with flags, FCB pointer, directory enumeration offset, and search expression.
  - Flags include open-by-ID, ignore-case, versioned open, dismount-on-close, extended DASD I/O, and enumeration state flags.

- `IRP_CONTEXT`
  - Per-originating-IRP state with original IRP, VCB, exception status, flags, real device, I/O or teardown context, top-level context, major/minor function, thread context, and work item.
  - Flags track waitability, posting, top-level ownership, FSP context, teardown, allocated I/O, popup disable, verify forcing, and create-name properties.

- `IRP_CONTEXT_LITE`
  - Compact delayed-close payload containing FCB, list link, user-reference count, and real device.

- `CD_IO_CONTEXT`
  - Tracks async/sync noncached I/O, master IRP, request count, status, resource release data, or sync event.

- `THREAD_CONTEXT`
  - Stack-resident top-level CDFS context with signature, saved top-level IRP, and top-level IRP context pointer.

- Enumeration structures:
  - `PATH_ENUM_CONTEXT`
  - `PATH_ENTRY`
  - `COMPOUND_PATH_ENTRY`
  - `DIRENT_ENUM_CONTEXT`
  - `DIRENT`
  - `COMPOUND_DIRENT`
  - `FILE_ENUM_CONTEXT`

- Synthetic file headers:
  - `RIFF_HEADER`
  - `AUDIO_PLAY_HEADER`

- File ID macros:
  - Encode directory bit in `LowPart` high bit.
  - Store parent/path-table offset in `HighPart`.
  - Store dirent offset in `LowPart`.
  - Provide helpers for query/set/directory marking and constructing IDs from parent+dirent.

- Optional `CDFS_TELEMETRY_DATA_CONTEXT`
  - Tracks missed telemetry points, periodic telemetry timing, volume GUID, optional debug interval, and filesystem statistics.

## Dependencies and Interactions

- Used by `cddata.h` assertions, `cdprocs.h` prototypes/macros, close/cleanup logic, create/path/name/dirent code, and VCB teardown.
- CCB/FCB/VCB count fields are directly manipulated by macros in `cdprocs.h`.
- `IRP_CONTEXT` fields are central to dispatch, exception processing, posting, cleanup, close, and verify paths.
- `VCB` sector cache and TOC fields support mount, read, XA/audio, and directory enumeration behavior.

## Behavioral Notes

- This header is the best map of CDFS lifetime rules: handles affect cleanup counts, object references affect teardown, and residual references keep core volume structures alive.
- Synchronization rules are explicitly documented and are essential because close/cleanup paths can run recursively or from worker threads.
- File IDs deliberately make directory parent lookup efficient by using a zero dirent offset plus a directory marker bit.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/cdstruc.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/cleanup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/cleanup.c

## Purpose

`cleanup.c` implements `IRP_MJ_CLEANUP` for CDFS. Cleanup runs when the last handle to a file object closes, before the file object itself necessarily loses all references.

## Key Contents

- `CdCommonCleanup`
  - Completes immediately if the request targets the filesystem device object rather than a mounted volume.
  - Decodes the file object into `TypeOfOpen`, `Fcb`, and `Ccb`.
  - Ignores unopened and stream file objects.
  - Sets `FO_CLEANUP_COMPLETE` while holding the file resource exclusively so later reads fail through FCB verification.
  - Handles volume opens:
    - If `CCB_FLAG_DISMOUNT_ON_CLOSE`, acquires global data and calls `CdCheckForDismount(..., Force=TRUE)`.
    - If file object was modified, flushes device buffers with `CdHijackIrpAndFlushDevice` and marks the device for verify.
  - Acquires the FCB exclusively for cleanup accounting and handle-state teardown.
  - For directory opens, calls `FsRtlNotifyCleanup`.
  - For file opens:
    - coordinates with oplock cleanup via `FsRtlCheckOplock`
    - unlocks all byte-range locks via `FsRtlFastUnlockAll`
    - uninitializes cache map with `CcUninitializeCacheMap`
    - recalculates fast-I/O state
  - Locks the VCB and decrements cleanup counts.
  - Unlocks the volume if this file object owns `Vcb->VolumeLockFileObject`.
  - Removes share access via `IoRemoveShareAccess`.
  - Sends `FSRTL_VOLUME_UNLOCK` notification if needed.
  - If cleanup count reaches zero on a not-mounted volume, attempts teardown by acquiring CdData, acquiring VCB exclusive, and purging the volume.

## Dependencies and Interactions

- Depends on `CdDecodeFileObject`, `CdAcquireFileExclusive`, `CdAcquireFcbExclusive`, `CdDecrementCleanupCounts`, `CdPurgeVolume`, `CdCheckForDismount`, and volume verify helpers.
- Updates VCB and FCB cleanup counts defined in `cdstruc.h`.
- Interacts with cache manager, oplock package, file-lock package, notify package, and I/O manager VPB lock state.
- Complements `close.c`: cleanup releases handle-visible state, while close releases the file-object reference and may tear down structures.

## Behavioral Notes

- Cleanup is not the final object destruction path; mapped files can keep FCBs alive after cleanup.
- Volume unlock is performed even for implicit volume locks.
- Teardown triggering is conservative: it purges to force closes, then final teardown is expected after the current IRP completes if this file object was the last hold.
- Share access removal happens during cleanup because close may be delayed.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/cleanup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/close.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/close.c

## Purpose

`close.c` implements `IRP_MJ_CLOSE` and CDFS deferred close processing. Close releases final file-object references, decrements FCB/VCB reference counts, and triggers structure teardown when possible. It supports immediate, async, and delayed close paths.

## Key Contents

- Local helpers:
  - `CdCommonClosePrivate`
  - `CdQueueClose`
  - `CdRemoveClose`
  - `CdCloseWorker`

- `CdFspClose`
  - Processes async and delayed close queues.
  - If a VCB is supplied, drains closes for that VCB; otherwise processes normal queued work.
  - Converts `IRP_CONTEXT_LITE` delayed-close entries into a stack `IRP_CONTEXT`.
  - Extracts FCB/user-reference data from full async `IRP_CONTEXT` entries.
  - Sets FSP/top-level flags and thread context.
  - Batches close processing per VCB but periodically releases/reacquires to avoid starving exclusive VCB waiters.
  - Detects possible VCB teardown when the volume is no longer mounted and cleanup count is zero, rechecking under `CdData`.
  - Calls `CdCommonClosePrivate`.
  - Completes/cleans up each IRP context and releases held VCB/global locks.

- `CdCommonClose`
  - FSD entry point for close.
  - Completes immediately for filesystem-device-object requests and unopened file objects.
  - Decodes file object, deletes CCB if present, and treats CCB presence as one user reference.
  - If mounted volume, last FCB reference, and user file/directory open, queues delayed close.
  - Otherwise checks whether VCB teardown may be needed, acquiring `CdData` for safe dismount synchronization.
  - Calls `CdCommonClosePrivate`; if resources cannot be acquired without waiting, queues async close.
  - Always completes the original IRP with `STATUS_SUCCESS`.

- `CdCommonClosePrivate`
  - Acquires VCB shared and FCB exclusive.
  - In FSD path, acquisition may be non-waiting; failure returns `FALSE` so caller queues async close.
  - Decrements VCB/FCB reference counts using `CdDecrementReferenceCounts`.
  - Calls `CdTeardownStructures`.
  - Releases FCB if teardown did not remove it, then releases VCB.
  - Returns `TRUE` when close was processed.

- `CdCloseWorker`
  - Work-item trampoline that calls `CdFspClose(NULL)`.

- `CdQueueClose`
  - Queues either delayed or async close work.
  - Delayed close allocates `IRP_CONTEXT_LITE`; allocation failure falls back to async close.
  - Cleans up top-level request state before queueing.
  - Delayed queue stores compact FCB/user-reference/real-device data.
  - Async queue reuses the existing `IRP_CONTEXT`, storing FCB in `IrpContext->Irp` and user reference in `ExceptionStatus`.
  - Starts the close worker via `IoQueueWorkItem` when needed.
  - Triggers delayed-close reduction when count exceeds `CdData.MaxDelayedCloseCount`.

- `CdRemoveClose`
  - Removes a suitable close item from async queue first.
  - If no async item is found, optionally scans delayed queue when a VCB is specified or delayed reduction is active.
  - Filters by VCB when requested.
  - Disables `FspCloseActive` and `ReduceDelayedClose` when no work remains for normal processing.

## Dependencies and Interactions

- Uses close queue fields in `CD_DATA`: `AsyncCloseQueue`, `DelayedCloseQueue`, counts, thresholds, flags, and `CloseItem`.
- Depends on `IRP_CONTEXT_LITE`, `IRP_CONTEXT`, VCB/FCB reference counts, and teardown structures from `cdstruc.h`.
- Uses synchronization macros from `cdprocs.h`.
- Works with `cleanup.c`: cleanup decrements handle counts and share state; close decrements reference counts and can remove FCB/VCB structures.
- Dismount decisions call `CdCheckForDismount` and rely on VCB condition/cleanup state.

## Behavioral Notes

- Close always returns success to the I/O manager after queueing or processing because close failure is not surfaced as normal filesystem operation failure.
- Delayed close is an optimization for recently closed user files/directories on mounted volumes.
- Async close avoids unsafe waits or lock-order problems from FSD/recursive close paths.
- `CdCommonClosePrivate` is intentionally small: acquire, decrement, teardown, release.
- Queue storage is compact for delayed closes to avoid keeping full IRP contexts alive in a long-lived queue.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/close.c -->