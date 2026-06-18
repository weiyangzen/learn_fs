# Group Research: group_1830_windows_driver_samples_sources_windows_windows_driver_samples_files_38148a531b8e

Scope confirmed against `Docs/research_subset_a.md`. All ten listed CDFS source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/allocsup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/allocsup.c

## Purpose

`allocsup.c` implements CDFS allocation mapping support around the internal `CD_MCB` structure. It maps logical file offsets to logical on-disc byte offsets and contiguous byte counts, using 2048-byte cooked CD sectors rather than raw 2352-byte XA sectors.

The file handles normal single-extent mappings, multi-extent files represented by multiple dirents, directory/path-table stream biasing, and interleaved extents.

## Main Routines

- `CdLookupAllocation`
  - Main lookup entry point.
  - Returns `DiskOffset` and `ByteCount` for a valid file offset.
  - Special-cases `VolumeDasdFcb` by returning the input `FileOffset` directly.
  - Looks in the FCB MCB first.
  - If the MCB lacks the requested mapping, acquires the parent directory, walks dirents from the file's first dirent offset, lazily loads every extent into the MCB, then retries lookup.
  - Raises `STATUS_DISK_CORRUPT_ERROR` if the second pass still cannot resolve the mapping or a multi-extent chain has no next dirent.

- `CdAddAllocationFromDirent`
  - Adds one dirent extent into an FCB MCB at a requested slot.
  - Doubles the MCB array when the embedded/small array is full.
  - Stores starting disc offset, byte count, file offset, and interleave geometry.
  - Rounds the last extent byte count to a logical block boundary.
  - Converts `FileUnitSize` and `InterleaveGapSize` from logical blocks to bytes.

- `CdAddInitialAllocation`
  - Creates the initial mapping for directory/path-table streams.
  - Biases `DiskOffset` backward by `Fcb->StreamOffset` so cached stream offsets can begin on sector boundaries.
  - Requires an empty MCB and non-data FCB.

- `CdTruncateAllocation`
  - Drops MCB entries starting at the entry containing `StartingFileOffset`.
  - Used when directory stream size or cached allocation needs to be reset.

- `CdInitializeMcb`
  - Initializes an FCB's MCB with a single embedded `Fcb->McbEntry`.

- `CdUninitializeMcb`
  - Frees an allocated MCB array when more than the embedded entry was used.

- `CdFindMcbEntry`
  - Linear search for the MCB entry containing a file offset.
  - Returns the insertion index when no current entry covers the offset.

- `CdDiskOffsetFromMcbEntry`
  - Computes the disc offset and contiguous byte count within a selected MCB entry.
  - Fast path for non-interleaved extents.
  - For interleaved extents, walks file-data blocks while skipping gap blocks on disc.
  - Caps returned byte count at `MAXULONG`.

## Key Data Model

Each `CD_MCB_ENTRY` stores:

- `FileOffset`: logical offset in the file.
- `DiskOffset`: logical cooked disc offset, already biased for XAR and directory stream alignment.
- `ByteCount`: file bytes represented by this extent.
- `DataBlockByteCount`: data bytes in each interleave unit.
- `TotalBlockByteCount`: data plus skipped gap bytes per interleave unit.

The MCB is non-sparse and append-only during loading; adding an extent always advances `CurrentEntryCount`.

## Integration

`allocsup.c` depends on dirent enumeration (`CdLookupDirent`, `CdLookupNextDirent`, `CdUpdateDirentFromRawDirent`), FCB locking (`CdLockFcb`/`CdUnlockFcb`), file acquisition on the parent directory, and block/sector conversion macros from `cdprocs.h`.

It is used by read and cache paths that need to translate logical stream offsets into disc reads.

## Risk Notes

- The MCB search is linear by design; this is acceptable for typical CD files but can scale poorly with many extents.
- Lazy population trusts multi-dirent ordering in the parent directory; malformed chains raise corruption statuses.
- Interleave math is central to correctness. Off-by-one or block-size errors would return wrong physical reads.
- The module assumes callers request valid file ranges; invalid or beyond-file offsets are not independently sanitized here.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/allocsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/cachesup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/cachesup.c

## Purpose

`cachesup.c` implements CDFS cache-manager support: creating/deleting internal stream file objects, completing MDL reads, and purging cached sections during lock/dismount paths.

## Main Routines

- `CdCreateInternalStream`
  - Creates an internal stream file object with `IoCreateStreamFileObjectLite`.
  - Attaches it to the FCB section object pointers.
  - Marks it read-only and identifies it as `StreamFileOpen`.
  - References the FCB to keep it alive while the stream object exists.
  - Initializes the cache map with `CcInitializeCacheMap` and `CdData.CacheManagerCallbacks`.
  - Stores the stream file in `Fcb->FileObject`.
  - For uninitialized directory FCBs, reads the self dirent, verifies it is `"."`, updates file/allocation/valid-data sizes, resets allocation mapping, imports hidden attribute/time fields, and marks `FCB_STATE_INITIALIZED`.
  - If sizes changed, purges stale cached pages.

- `CdDeleteInternalStream`
  - Removes `Fcb->FileObject` under the FCB lock.
  - Uninitializes the cache map when present.
  - Clears `FileName` pointers because the stream file only borrows FCB-owned name buffers.
  - Dereferences the file object.

- `CdCompleteMdl`
  - Completes MDL read cleanup via `CcMdlReadComplete`.
  - Clears `Irp->MdlAddress`.
  - Completes the IRP with `STATUS_SUCCESS`.

- `CdPurgeVolume`
  - Flushes delayed closes with `CdFspClose`.
  - Acquires the global file resource to block file operations.
  - Iterates all FCBs in the VCB FCB table, references each while processing, flushes image sections, purges data cache sections, and tears down eligible structures.
  - On dismount, deletes internal streams for directory/path-table FCBs.
  - Also purges/deletes path table and volume DASD FCB state when `DismountUnderway` is true.
  - Returns the first `STATUS_UNABLE_TO_DELETE_SECTION` if cache purge fails because a section remains mapped.

## Important Behavior

Internal stream files are central to cached reads of directories and path tables. They borrow FCB names for profiling/debugging, so teardown must null those names before object dereference.

Directory stream initialization is tied to the self entry. If the on-disc self dirent is missing, has zero aligned length, or does not parse as the expected self name, the code raises corruption.

## Integration

This module interacts with the Windows Cache Manager (`CcInitializeCacheMap`, `CcSetFileSizes`, `CcPurgeCacheSection`, `CcUninitializeCacheMap`), Memory Manager image-section flushing, FCB reference accounting, allocation support (`CdTruncateAllocation`, `CdAddInitialAllocation`), dirent support, and volume teardown.

## Risk Notes

- Stream-file lifetime depends on exact reference-count pairing. `CdCreateInternalStream` intentionally takes two references and unwinds one on failure.
- Cache purge during dismount can fail when image/data sections remain mapped, returning `STATUS_UNABLE_TO_DELETE_SECTION`.
- The self-dirent validation protects directory stream sizing; corrupted media can force cleanup through exception paths.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/cachesup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/cd.h -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/cd.h

## Purpose

`cd.h` defines CDFS on-disc constants, raw ISO/HSG/Joliet structures, directory-entry and path-table layouts, timestamp conversion, and XA system-use metadata. It is the main wire-format header for CD-ROM filesystem parsing.

## Main Contents

- Sector constants:
  - `SECTOR_SIZE`/`CD_SECTOR_SIZE`: 2048 bytes.
  - `RAW_SECTOR_SIZE` and `XA_SECTOR_SIZE`: 2352 bytes.
  - sector masks and shift constants.

- Volume descriptor constants:
  - first descriptor sector, descriptor type values, standard IDs (`CD001`, `CDROM`), version constants, volume ID lengths.

- Raw volume descriptor structures:
  - `RAW_ISO_VD`
  - `RAW_HSG_VD`
  - `RAW_JOLIET_VD`
  - These model primary/secondary descriptors with different field ordering between ISO and HSG.

- Descriptor accessor macros:
  - `CdRvdId`, `CdRvdVersion`, `CdRvdDescType`, `CdRvdEsc`, `CdRvdVolId`, `CdRvdBlkSz`, `CdRvdPtLoc`, `CdRvdPtSz`, `CdRvdDirent`, `CdRvdVolSz`.
  - Select ISO vs HSG layout based on `VCB_STATE_HSG`.

- Directory-entry layout:
  - `RAW_DIRENT` / `RAW_DIR_REC`
  - Directory flags such as hidden, directory, associated file, and multi-extent.
  - Macros for minimum record size and flag-field selection.

- Time conversion:
  - `CdConvertCdTimeToNtTime` converts 6/7-byte CD time fields to NT time.
  - Applies ISO GMT offset when present and within the ISO range `[-48, 52]` fifteen-minute units.
  - HSG media ignores GMT offset.

- Path table layouts:
  - `RAW_PATH_ISO`
  - `RAW_PATH_HSG`
  - Macros recover ID length, XAR length, and directory location despite layout differences.

- XA system-use area:
  - `SYSTEM_USE_XA`
  - Flags for form1, form2, and digital audio extents.
  - `XA_EXTENT_TYPE` enum for cooked form1 data, mode2 form2 data, and CD audio.

## Integration

This header is consumed throughout mount, path-table parsing, dirent parsing, allocation, and XA/audio file exposure. Many higher-level helpers normalize these raw structures into `DIRENT`, `PATH_ENTRY`, and FCB fields defined in `cdstruc.h`.

## Risk Notes

- Many fields are unaligned byte arrays because CD on-disc structures are packed. Callers must use the provided copy/conversion helpers rather than direct misaligned access.
- ISO/HSG differences are hidden behind macros; using raw fields directly can break HSG media.
- Timestamp conversion relies on raw byte values and only bounds-checks GMT offset, not full date validity.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/cd.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/cddata.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/cddata.c

## Purpose

`cddata.c` defines CDFS global data and constants, the common FSD dispatch entry point, exception handling/completion paths, top-level thread context handling, fast-I/O feasibility checks, and a serial checksum helper.

## Global Data and Constants

- Defines global `CdData` and `CdFastIoDispatch`.
- Defines reserved names for `"."` and `".."`.
- Defines volume descriptor IDs for HSG, ISO, and XA.
- Defines audio-disc label and pseudo audio track filename metadata.
- Defines Joliet escape sequences.
- Defines hard-coded RIFF headers:
  - `CdAudioPlayHeader`
  - `CdXAAudioPhileHeader`
  - `CdXAFileHeader`
- Optionally defines `CdTelemetryData` under `CDFS_TELEMETRY_DATA`.

## Dispatch Flow

`CdFsdDispatch` is the common driver entry for major IRP functions registered by `DriverEntry`.

It:

- Enters filesystem context with `FsRtlEnterFileSystem`.
- Determines waitability from mount context or synchronous IRP state.
- Allocates an `IRP_CONTEXT`.
- Sets CDFS top-level thread context.
- Switches on `MajorFunction` and calls:
  - `CdCommonCreate`
  - `CdCommonClose`
  - `CdCommonRead`
  - `CdCommonWrite`
  - `CdCommonQueryInfo`
  - `CdCommonSetInfo`
  - `CdCommonQueryVolInfo`
  - `CdCommonDirControl`
  - `CdCommonFsControl`
  - `CdCommonDevControl`
  - `CdCommonLockControl`
  - `CdCommonCleanup`
  - `CdCommonPnp`
  - `CdCommonShutdown`
- Routes `IRP_MJ_READ` + `IRP_MN_COMPLETE` to `CdCompleteMdl`.
- Uses `CdExceptionFilter` and `CdProcessException`.
- Retries when status is `STATUS_CANT_WAIT`.

## Exception Handling

- `CdRaiseStatusEx`
  - In sanity builds, traces/breaks on selected raised statuses.
  - Stores normalized or raw status in `IrpContext->ExceptionStatus`.
  - Records bug-check file/line into `RaisedAtLineFile`.
  - Raises via `ExRaiseStatus`.

- `CdExceptionFilter`
  - Converts `STATUS_IN_PAGE_ERROR` to underlying I/O status when available.
  - Preserves explicit CDFS-raised status.
  - Bugchecks unexpected NTSTATUS exceptions via `CdBugCheck`.
  - Returns `EXCEPTION_EXECUTE_HANDLER` for expected statuses.

- `CdProcessException`
  - Handles posting/retry decisions for `STATUS_CANT_WAIT` and verify-required cases.
  - Performs media verification through `CdPerformVerify` when possible.
  - Raises hard errors for user-induced conditions unless disabled.
  - Completes regular failures through `CdCompleteRequest`.

- `CdCompleteRequest`
  - Cleans up the IRP context.
  - Clears `IoStatus.Information` for input operations that fail.
  - Sets final IRP status and completes with `IO_CD_ROM_INCREMENT`.

## Other Routines

- `CdSetThreadContext`
  - Manages CDFS top-level IRP context stored in `IoGetTopLevelIrp`.
  - Detects whether an existing top-level context is a valid stack-resident CDFS context.
  - Records prior top-level value for later restore.

- `CdFastIoCheckIfPossible`
  - Allows fast I/O only for user file reads.
  - Rejects non-read checks with `STATUS_INVALID_PARAMETER`.
  - Uses file locks to decide if fast read can proceed.

- `CdSerial32`
  - Generates a 32-bit serial by accumulating bytes into four checksum lanes.

## Integration

This file is the bridge between I/O manager dispatch, CDFS common operation modules, exception-driven error propagation, verify/remount handling, and fast-I/O dispatch initialized in `cdinit.c`.

## Risk Notes

- Exception status stored in `IrpContext` is authoritative once CDFS raises explicitly.
- Verify-required handling carefully avoids trusting potentially invalid thread verify device pointers and falls back to `Vcb->Vpb->RealDevice`.
- Thread-context validation uses stack bounds, alignment, and a CDFS signature; misuse would corrupt top-level IRP handling.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/cddata.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/cddata.h -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/cddata.h

## Purpose

`cddata.h` declares CDFS global variables/constants and debug/sanity assertion macros for validating CDFS objects and resource ownership.

## Main Contents

- External globals:
  - `CdData`
  - `CdFastIoDispatch`
  - reserved directory-name arrays/strings
  - descriptor ID strings
  - audio label and pseudo filename metadata
  - Joliet escape sequences
  - RIFF/XA header templates
  - optional `CdTelemetryData`

- Residual reference constants:
  - `CDFS_RESIDUAL_REFERENCE`
  - `CDFS_RESIDUAL_USER_REFERENCE`
  - Account for mounted volume, DASD FCB, root index FCB/internal stream, and path table FCB/internal stream.

- Sanity assertion macros under `CD_SANITY`:
  - Node type validation for VCB, FCB, FCB nonpaged, CCB, IRP context, IRP, file object.
  - Resource ownership checks for CdData, VCB, FCB, and file resources.
  - Mutex ownership checks for VCB/FCB locks.
  - `CD_SANITY` is enabled for `DBG` builds.

- Retail/non-sanity versions:
  - Assertion macros compile to no-ops.
  - `DebugBreakOnStatus` also no-ops.

## Integration

Included through `cdprocs.h`, this header gives every CDFS module a shared view of global data and debug validation. The macros are used heavily in allocation, cache, cleanup, dispatch, resource, and structure support code.

## Risk Notes

- The assertion layer catches structural misuse only in sanity/debug builds.
- Retail builds rely on normal code paths and NTSTATUS exception handling, not these assertions.
- The `ASSERT_FCB` macro accepts data, index, and path-table node types, matching the unioned FCB layout in `cdstruc.h`.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/cddata.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/cdinit.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/cdinit.c

## Purpose

`cdinit.c` implements CDFS driver initialization, unload, and global data setup.

## Main Routines

- `DriverEntry`
  - Creates the filesystem device object named `\Cdfs` with type `FILE_DEVICE_CD_ROM_FILE_SYSTEM`.
  - Installs `CdUnload`.
  - Assigns `CdFsdDispatch` to all supported major functions:
    - create, close, read, write, query/set file info, query volume info, directory control, FS control, device control, lock control, cleanup, PNP, shutdown.
  - Sets `DriverObject->FastIoDispatch` to `CdFastIoDispatch`.
  - Registers FS filter callback `CdFilterCallbackAcquireForCreateSection`.
  - Calls `CdInitializeGlobalData`.
  - Marks the filesystem as low priority with `DO_LOW_PRIORITY_FILESYSTEM`.
  - Registers with the I/O manager via `IoRegisterFileSystem`.
  - References the filesystem device object for global lifetime.
  - Optionally initializes telemetry.

- `CdUnload`
  - Frees cached IRP contexts from `CdData.IrpContextList`.
  - Frees the close work item.
  - Deletes `CdData.DataResource`.
  - Dereferences the filesystem device object.

- `CdInitializeGlobalData`
  - Initializes the `FAST_IO_DISPATCH` table.
  - Hooks fast query, lock/unlock, fast read, network info, and MDL operations.
  - Clears and initializes `CdData`.
  - Initializes VCB queue, `DataResource`, cache manager callbacks, volume cache no-op callbacks, mutexes, async/delayed close queues, and close work item.
  - Sizes IRP context and delayed close thresholds based on `MmQuerySystemSize`.

## Integration

This file wires the exported driver object to the rest of CDFS. The initialized `CdFastIoDispatch` and `CdData.CacheManagerCallbacks` are consumed by dispatch, cache, fast-I/O, and stream-file setup paths.

## Risk Notes

- Initialization failure unwinds the filesystem device object but must occur before registration.
- `CdUnload` assumes no active mounted volumes remain and only tears down global cached objects.
- Each registered IRP major function must match a case in `CdFsdDispatch`; the comments explicitly call out that invariant.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/cdinit.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/cdprocs.h -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/cdprocs.h

## Purpose

`cdprocs.h` is the central CDFS private interface header. It includes NT/storage headers and CDFS structure/data headers, defines allocation tags and utility macros, declares cross-module routines, and supplies inline helpers for synchronization, buffer handling, exceptions, alignment, telemetry, and fast-I/O state.

## Major Areas

- Includes:
  - `ntifs.h`, CD-ROM/disk/SCSI IOCTL headers.
  - `nodetype.h`, `Cd.h`, `CdStruc.h`, `CdData.h`.
  - Optional telemetry headers.

- Pool tags:
  - Tags for CCBs, TOCs, dirent names, FCBs, file names, I/O contexts, IRP contexts, MCB arrays, prefix/path structures, volume descriptors, VPBs, and more.

- Access checks:
  - `CdIllegalFcbAccess` rejects write/delete/DAC style access on read-only CDFS objects, with a narrower rule for volume opens.

- Allocation support declarations:
  - `CdLookupAllocation`
  - `CdAddAllocationFromDirent`
  - `CdAddInitialAllocation`
  - `CdTruncateAllocation`
  - `CdInitializeMcb`
  - `CdUninitializeMcb`

- Cache support declarations/macros:
  - Internal stream create/delete.
  - MDL completion.
  - Volume purge.
  - `CdVerifyOrCreateDirStreamFile`.
  - `CdUnpinData`.

- Device I/O declarations:
  - Noncached reads, XA reads, volume DASD writes, sector reads, MDL creation, device control helpers, IRP hijack/flush.

- Dirent and file enumeration:
  - Dirent lookup/update routines.
  - File/directory find routines.
  - Initialization/cleanup macros for `FILE_ENUM_CONTEXT`, `DIRENT`, and `DIRENT_ENUM_CONTEXT`.

- File-object support:
  - `TYPE_OF_OPEN` enum.
  - `CdSetFileObject`, `CdDecodeFileObject`, `CdFastDecodeFileObject`.

- Name support:
  - CD name conversion, upcasing, dissection, legality checks, 8.3 generation, wildcard matching, full comparison.

- Filesystem control/path/prefix:
  - Volume lock/unlock internals.
  - Path table enumeration and lookup.
  - Prefix insert/remove/find.

- Synchronization:
  - Resource acquisition API and macros for CdData, VCB, file, and FCB resources.
  - Fast mutex lock/unlock macros for CdData, VCB, and recursively-lockable FCB mutexes.
  - Cache sector resource helpers.
  - Oplock location abstraction for pre/post Win8 layouts.

- Cache/section callbacks:
  - No-op volume callbacks.
  - cache acquire/release callbacks.
  - FS filter acquire callback for section creation.
  - section release callback.

- Structure lifetime:
  - VCB initialization/update/delete.
  - FCB create/initialize.
  - CCB create/delete.
  - file lock create/delete.
  - IRP context create/cleanup/stack initialization.
  - teardown.
  - reference/cleanup count macros.
  - FCB table lookup/iteration.
  - TOC processing.

- Verification:
  - verify, dismount, mark-device-for-verify, VCB/FCB operation verification.
  - raw-device status classification.

- Work queue:
  - request posting, pre-post, oplock completion, FSP dispatch, close worker.

- Utility macros:
  - pointer arithmetic, word/long/quad alignment.
  - sector/block alignment and conversion.
  - unaligned copy and endian swap helpers.
  - LBN-to-MSF declaration.
  - top-level context restore.
  - `CanFsdWait`.
  - `CdIsFastIoPossible`.
  - `try_return`/`try_leave`.
  - safe pool free.

- Dispatch/common operation declarations:
  - `CdFsdDispatch`
  - exception/filter/completion routines
  - all `CdCommon*` operation entry points.

- Telemetry:
  - Optional TraceLogging provider declarations.
  - stack-space guard before telemetry calls.
  - mount telemetry safe wrapper.

## Integration

Every CDFS implementation file includes this header. It defines the effective private ABI between modules such as allocation, cache, create, close, read, dir control, FS control, verification, path/name support, and structure management.

## Risk Notes

- Many helpers are macros with side effects, so argument evaluation and lock state must be correct.
- Locking order is embodied in macros and comments but enforced mostly by assertions.
- The header mixes declarations with inline logic; changes here have broad driver-wide blast radius.
- The FCB recursive lock macro relies on `FcbLockThread`/`FcbLockCount` consistency.
- Telemetry is guarded for stack usage because TraceLogging can consume significant kernel stack.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/cdprocs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/cdprocssrc.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/cdprocssrc.c

## Purpose

`cdprocssrc.c` is a one-line source file that only includes `cdprocs.h`.

## Contents

```c
#include "cdprocs.h"
```

## Integration

This file likely exists to force compilation or analysis of the private procedure header in a source context, or to satisfy build tooling that expects a translation unit for header-derived checks.

## Runtime Behavior

No functions, variables, or executable logic are defined here beyond whatever inline/header content is visible through `cdprocs.h`.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/cdprocssrc.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/cdstruc.h -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/cdstruc.h

## Purpose

`cdstruc.h` defines the major in-memory CDFS data structures: global filesystem state, mounted volume state, FCB/CCB/IRP context state, enumeration contexts, normalized dirent/path entries, XA/audio headers, file ID encoding, and optional telemetry state. It also documents the CDFS object graph and locking hierarchy.

## Architecture Notes

The header describes:

- `CdData` owns the filesystem device object and VCB queue.
- Each mounted or previously mounted volume has a VCB embedded in a volume device object.
- Each VCB owns an FCB table indexed by `FILE_ID`.
- Directory FCBs own child FCB lists and prefix tables.
- Open-by-ID paths may create detached subtrees.
- File objects point to FCB and optional CCB.
- Stream file objects point directly to FCBs for cached internal streams.

## Synchronization Model

The documented lock order is central:

- CdData resource protects mount/dismount and VCB queue.
- VCB resource protects open/close state.
- VCB file resource synchronizes file operations across the volume.
- FCB nonpaged resource protects open/close for an FCB.
- VCB mutex protects FCB table and reference/open counts.
- FCB mutex protects miscellaneous FCB fields and supports recursive locking.
- Multiple FCB locks are acquired leaf-to-root.
- Cleanup only holds locks long enough to adjust counts/share/lock state.

## Major Structures

- `CD_MCB` / `CD_MCB_ENTRY`
  - Logical stream-to-disc allocation mappings.
  - Stores file offset, disc offset, byte count, and interleave geometry.

- `CD_NAME`, `NAME_LINK`, `PREFIX_ENTRY`
  - Normalized CDFS names, version strings, splay-tree links, and prefix entries.

- `CD_DATA`
  - Global driver state: driver object, filesystem device object, VCB queue, IRP context cache, async/delayed close queues, global resource, cache-manager callbacks, close work item.

- `CDROM_TOC_LARGE`
  - Extended TOC container supporting up to `0xAA` track entries.

- `VCB`
  - Mounted volume state: VPB, target device, lock file object, condition/state flags, cleanup/reference counts, root/path/DASD FCBs, volume descriptor offsets, XA sector cache, synchronization resources, block geometry, FCB table, TOC data, transfer limits, swap VPB, directory pre-cache, optional telemetry correlation ID.

- `VOLUME_DEVICE_OBJECT`
  - Kernel `DEVICE_OBJECT` plus posted request accounting/overflow queue and embedded `VCB`.

- `FCB_DATA`, `FCB_INDEX`, `FCB_NONPAGED`, `FCB`
  - Data-file extension with oplock/file-lock state.
  - Index/path-table extension with stream file object, stream offset, child list, ordinals, child path-table offsets, and prefix trees.
  - Nonpaged section/resource/mutex state.
  - Common FCB stores advanced header, VCB/parent links, file ID, counts, flags, attributes, XA metadata, locks, share access, MCB, prefix entries, creation time, and type-specific union.

- `CCB`
  - Per-file-object context with flags, FCB pointer, directory enumeration offset, and search expression.

- `IRP_CONTEXT`
  - Per-originating-IRP state: IRP, VCB, exception status, flags, real device, I/O context or teardown FCB pointer, top-level context, major/minor function, thread context, work item.

- `IRP_CONTEXT_LITE`
  - Minimal delayed-close context with FCB, list link, user reference count, and real device.

- `CD_IO_CONTEXT`
  - Tracks multi-IRP or synchronous noncached I/O completion state.

- `THREAD_CONTEXT`
  - Stack-resident top-level CDFS context with signature, saved previous top-level IRP, and top-level IRP context pointer.

- `PATH_ENUM_CONTEXT`, `PATH_ENTRY`, `COMPOUND_PATH_ENTRY`
  - Path-table enumeration and normalized path entry state, including cache BCBs, spanning-view buffers, ordinals, parent ordinals, disc offsets, names, and cleanup flags.

- `DIRENT_ENUM_CONTEXT`, `DIRENT`, `COMPOUND_DIRENT`, `FILE_ENUM_CONTEXT`
  - Directory stream enumeration and normalized dirent state.
  - `FILE_ENUM_CONTEXT` keeps prior/initial/current dirents for multi-dirent file handling and short-name generation.

- `RIFF_HEADER`, `AUDIO_PLAY_HEADER`
  - In-memory layouts for headers prepended to XA and audio pseudo files.

- Optional `CDFS_TELEMETRY_DATA_CONTEXT`
  - Tracks missed telemetry due to stack limits, periodic timing, volume GUID, and filesystem statistics.

## File ID Encoding

The `FILE_ID` macros encode:

- Directories:
  - `HighPart`: path-table offset.
  - `LowPart`: directory flag bit set, dirent offset treated as zero.

- Files:
  - `HighPart`: parent directory path-table offset.
  - `LowPart`: dirent byte offset in parent directory.

Macros query/set dirent offset, path-table offset, directory bit, and derive IDs from parent/dirent pairs.

## Integration

This header is included through `cdprocs.h` and underpins all modules. Allocation uses `CD_MCB`; cache and MM use FCB nonpaged section state; create/close/cleanup use FCB/CCB/VCB counts; directory and path support use enum contexts; read paths use XA/audio metadata and I/O contexts.

## Risk Notes

- Structure field ordering is ABI-sensitive for kernel, FSRTL, cache manager, and debugging assumptions.
- The unioned FCB layout requires correct `NodeTypeCode` and size selection.
- Reference and cleanup counts are spread across FCB and VCB and protected by different locks; pairing errors cause leaks or premature teardown.
- Directory/path enumeration contexts hold pinned cache data and optional pool buffers, so cleanup macros must match initialization paths.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/cdstruc.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/cleanup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/cleanup.c

## Purpose

`cleanup.c` implements `CdCommonCleanup`, the CDFS cleanup path invoked when the last user handle for a file object is closed. Cleanup is distinct from close: the file object may still exist due to MM/cache references, but user-visible handle state must be released.

## Main Flow

`CdCommonCleanup`:

1. Completes immediately with success if the request targets the filesystem device object rather than a mounted volume.
2. Decodes the file object into `TypeOfOpen`, FCB, and CCB.
3. Completes immediately for unopened or stream file objects.
4. Acquires the file exclusively long enough to set `FO_CLEANUP_COMPLETE`, preventing future reads through this file object.
5. Handles special volume-open cases:
   - If `CCB_FLAG_DISMOUNT_ON_CLOSE` is set, acquires CdData and forces dismount check.
   - If the volume handle modified the device, flushes the lower device and marks it for verify.
6. Acquires the FCB exclusively and performs type-specific cleanup:
   - `UserDirectoryOpen`: calls `FsRtlNotifyCleanup` for pending directory notifications.
   - `UserFileOpen`: runs oplock cleanup, unlocks all byte-range locks for this file object/process, uninitializes the cache map, and refreshes fast-I/O possibility.
   - `UserVolumeOpen`: no file-specific cleanup.
7. Locks the VCB to decrement FCB/VCB cleanup counts.
8. If this file object locked the volume, clears `VPB_LOCKED`, clears `VCB_STATE_LOCKED`, clears `VolumeLockFileObject`, and later sends `FSRTL_VOLUME_UNLOCK`.
9. Removes share access from the FCB.
10. Releases the FCB and sends unlock notification if needed.
11. If cleanup count reached zero on an unmounted VCB, acquires CdData and VCB exclusively and calls `CdPurgeVolume` to spark teardown.
12. Completes the IRP with `STATUS_SUCCESS`.

## Integration

This routine is called from `CdFsdDispatch`/FSP dispatch for `IRP_MJ_CLEANUP`. It interacts with:

- file-object decoding
- file/FCB/VCB synchronization
- oplock and file-lock packages
- cache manager
- notify package
- volume lock/dismount state
- share access accounting
- volume purge/teardown

## Important Semantics

- Cleanup marks user handle closure, not object deletion.
- Share access is removed during cleanup because close may be delayed by mapped sections.
- Volume unlock notification is sent after releasing locks.
- Teardown is attempted only after counts indicate no outstanding cleanup handles and the VCB is not mounted.

## Risk Notes

- Lock ordering matters: the routine carefully limits early file acquisition, then uses FCB and VCB locks for count/share updates.
- Device flush on modified volume handles uses IRP hijacking, so control flow differs from normal completion.
- Oplock cleanup is expected to complete immediately in this path.
- Failure during the purge attempt is not propagated; the cleanup IRP still completes success after teardown stimulation.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/cleanup.c -->