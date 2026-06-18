# Group Research: group_1840_windows_driver_samples_sources_windows_windows_driver_samples_files_332e52a185df

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/windows/windows-driver-samples`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/fatprocs.h -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/fatprocs.h

## Purpose

`fatprocs.h` is the central internal procedure header for the Windows Driver Samples FastFAT filesystem driver. It pulls in NT filesystem/storage headers plus FastFAT's core local headers, defines small inline helpers/macros, and declares the cross-module routines used by allocation, cache, device I/O, dirent, EA, file-object, filesystem-control, naming, resource, structure, splay-tree, time, verification, work-queue, FSD/FSP dispatch, completion, fast I/O, and FAT scanning code.

This file is primarily an integration map rather than an implementation unit. It establishes the public internal ABI between FastFAT modules and records many lock, wait, exception, and cache-manager contracts through SAL annotations and macros.

## Major Interfaces

- String and MCB helpers, access checks, allocation support, cache/buffer support, device I/O, dirent support, EA support, file-object support, filesystem control, name support, resource/cache callbacks, structure lifecycle, splay/name trees, time conversion, verification, work queue, dispatch, flush, completion, and fast I/O declarations.
- `FAT_ENUMERATION_CONTEXT` tracks a pinned FAT page during cluster-chain enumeration.
- `FatIsIoRangeValid()` is inline and enforces FAT's 32-bit file-size addressability.
- `TYPE_OF_OPEN` classifies unopened, user file, user directory, user volume, virtual volume, directory stream, and EA stream opens.
- `FAT_FLUSH_TYPE` selects no flush, flush, flush-and-invalidate, or flush-without-purge.
- `FAT_VOLUME_STATE` models clean, dirty, and dirty-with-surface-test volume states.

## Important Macros and Contracts

- Pointer and alignment helpers: `Add2Ptr`, `PtrOffset`, `WordAlign`, `LongAlign`, `QuadAlign`, `BlockAlign`, and `BlockAlignTruncate`.
- Unaligned BPB copy helpers: `UCHAR1`, `UCHAR2`, `UCHAR4`, `CopyUchar1`, `CopyUchar2`, `CopyUchar4`, and `CopyU4char`.
- FAT type predicates: `FatIsFat32`, `FatIsFat16`, and `FatIsFat12`.
- `FatAcquireExclusiveVolume` and `FatReleaseVolume` acquire/release the VCB and all child FCB resources around whole-volume operations.
- `FatNotifyReportChange` lazily builds `FullFileName` and reports notify changes.
- Exception handling uses `FatExceptionFilter`, `FatProcessException`, `FatRaiseStatus`, `FatResetExceptionState`, and `FatNormalizeAndRaiseStatus`.
- File IDs are generated from parent dirent offsets and root/FAT32 location rules, with special handling for `.` and `..`.

## Integration

`fatprocs.h` binds together structures from `FatStruc.h`, globals from `FatData.h`, on-disk FAT structures from `Fat.h`, LFN definitions from `Lfn.h`, node type codes from `nodetype.h`, and Windows kernel interfaces from `ntifs.h` plus storage/CDROM/SCSI/DDI headers. Most FastFAT implementation files include it, so changes here affect the whole driver.

## Notable Risks and Review Points

- Many macros evaluate parameters more than once and are not expression-safe in all contexts.
- Alignment helpers cast through `ULONG`, so they are intended for FAT 32-bit offsets and not arbitrary 64-bit pointer arithmetic.
- Whole-volume locking walks all child FCBs; caller lock ordering must remain consistent.
- Exception state is stored in `IrpContext`; handlers that catch and continue must reset it.
- `FatIsIoRangeValid()` only enforces 32-bit wrap constraints. Cluster-size or volume-bound checks must be done elsewhere.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/fatprocs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/fatprocssrc.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/fatprocssrc.c

## Purpose

`fatprocssrc.c` is a one-directive source file whose entire content is:

```c
#include "fatprocs.h"
```

The file has no functions, globals, data definitions, or runtime behavior of its own. Its role is to compile the central FastFAT procedure header as a translation unit, which can expose header self-containment problems, warning issues, or build-system expectations around precompiled/header-only declarations.

## Integration

The only dependency is `fatprocs.h`, which in turn includes NT kernel filesystem/storage headers and FastFAT internal headers. Any compile failure in this file would indicate that `fatprocs.h` cannot stand alone under this build configuration.

## Notable Details

- The file contains no trailing newline in this checkout.
- There is no direct filesystem behavior to test here beyond successful compilation.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/fatprocssrc.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/fatstruc.h -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/fatstruc.h

## Purpose

`fatstruc.h` defines the major in-memory data structures for the Windows Driver Samples FastFAT filesystem driver. It describes global driver state, mounted-volume state, file/directory control blocks, per-handle context, IRP context, noncached I/O context, deferred work packets, EA ranges, volume statistics, and conditional stack-swapping callout parameters.

## Core Structures

- `FAT_DATA`: global nonpaged driver record with mounted VCB queue, filesystem device objects, global resource, deferred close state, cache manager callbacks, and feature/shutdown flags.
- `FAT_WINDOW`: per-window allocation summary for large FATs.
- `CLOSE_CONTEXT`: deferred close state embedded in a CCB.
- `VCB`: mounted-volume control block containing target device, VPB, root DCB, allocation metadata, dirty FAT/bad-block MCBs, free-cluster bitmap, resources, virtual volume/EA streams, notification, verification, statistics, tunnel cache, media, and close-queue state.
- `FILE_SYSTEM_STATISTICS`: padded per-processor filesystem/FAT statistics.
- `VOLUME_DEVICE_OBJECT`: device object plus overflow work queue state and embedded `VCB`.
- `FILE_NAME_NODE`: FCB name-tree node for OEM or Unicode names.
- `NON_PAGED_FCB`: nonpaged stream fields for section object pointers and async noncached write synchronization.
- `FCB` / `DCB`: shared file/directory control block with advanced FCB header, nonpaged FCB pointer, allocation chain, parent/VCB links, state, share/open counts, dirent offsets, timestamps, MCB, directory/file-specific union, EA modification count, names, FAT attributes, and move-file event.
- `CCB`: per-file-object context with query templates, EA enumeration state, flags, and an overlaid close context.
- `IRP_CONTEXT`: per-IRP dispatch/unwind context with worker item, originating IRP, device/VCB, function codes, flags, exception status, I/O context, and repinned BCBs.
- `FAT_IO_CONTEXT`, `IO_RUN`, `DELETE_CONTEXT`, deferred flush/volume work packets, paging overflow packet, `EA_RANGE`, and Threshold `FAT_CALLOUT_PARAMETERS`.

## State Flags and Enums

- `VCB_CONDITION`: `VcbGood`, `VcbNotMounted`, `VcbBad`.
- VCB state flags cover lock/removable/dirty/shutdown/close/create/paging-file/deferred-flush/write-protected/dismount/hotplug/mount states.
- `FCB_CONDITION`: `FcbGood`, `FcbBad`, `FcbNeedsToBeVerified`.
- FCB flags cover delete/truncate-on-close, paging files, cache miss, flush FAT, temporary/system files, name tree state, long-name type, delayed close, case preservation, defrag denial, and zero-on-deallocation.
- CCB flags cover query behavior, buffer ownership, user-set times, DASD state, delete-on-close, opened-by-short-name, dismount, privileged access, format unit, defrag denial, and first-write tracking.
- IRP context flags cover wait/write-through/recursive/deferred/verify/user/FSP/error handling and stack-swapping state.
- `CLUSTER_TYPE`: available, reserved, bad, last, or next cluster.

## Key Layout and Behavior Notes

- VCB and FAT data records must be allocated from nonpaged pool.
- VCB dirty FAT tracking uses an MCB where holes mean clean sectors and `LBO == VBO` runs mean dirty sectors.
- The free cluster bitmap uses `1` for occupied clusters and `0` for free clusters.
- DCBs keep separate OEM and Unicode splay trees because FAT can expose both short OEM and long Unicode names.
- `EaModificationCount` is intentionally fixed after the file/directory union because DCB slack-space calculations depend on its offset.
- `FCB_LOOKUP_ALLOCATIONSIZE_HINT` is the sentinel `-1` allocation size meaning the real allocation must be discovered from the FAT.
- The CCB overlays close context over query/EA enumeration state once a handle is converted into delayed/asynchronous close processing.
- Statistics are padded to a cache-line multiple to reduce false sharing.

## Integration

These structures are consumed by `fatprocs.h` declarations and by FastFAT implementation modules for allocation, cache/device I/O, create/name lookup, cleanup/close, EA handling, verification/dismount, notification, and tunneling.

## Notable Risks and Review Points

- Layout sensitivity is high. Comments explicitly warn not to move `EaModificationCount`, and several structures are tuned for pool size or cache-line behavior.
- CCB uses bitfields and a union overlay, so code must not read query/EA state after `CCB_FLAG_CLOSE_CONTEXT` conversion.
- Several counts are plain `CLONG` or `ULONG` while some are volatile; callers must use expected locks around nonvolatile fields.
- Dual OEM/Unicode splay trees are correctness-critical. Missing an open FCB during prefix lookup can create duplicate FCBs.
- VCB state flags and `VcbCondition` are distinct. `VCB_STATE_FLAG_VOLUME_DISMOUNTED` does not replace the volume validity condition.
- `FAT_IO_CONTEXT` async state stores resources/thread IDs for completion-time release; incorrect initialization can leak locks.
- Conditional build sections can produce meaningfully different layouts across OS versions.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/fatstruc.h -->