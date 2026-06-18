# Group Research: group_1672_reactos_sources_windows_reactos_drivers_filesystems_cdfs_create_c_s_957bd08815f2

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/windows/reactos`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/create.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/create.c

## Purpose
Implements the CDFS create/open path for ReactOS, including volume opens, name opens, relative opens, file-ID opens, directory traversal, FCB creation/lookup, share-access checks, oplock handling, and CCB/file-object finalization.

## Key Elements
- `CdCommonCreate` is the main create dispatcher. It rejects unsupported create modes for this read-only filesystem, normalizes names, acquires the VCB, verifies media state, handles volume and file-ID opens specially, searches prefix/path-table state, scans directories for file entries, and completes opens through helper routines.
- `CdNormalizeFileNames` builds the full file-object name from absolute or related-file-object names, strips acceptable trailing separators, rejects malformed double-leading slashes, handles retry state through `IRP_CONTEXT_FLAG_FULL_NAME`, validates 64-bit file IDs, upcases remaining parse names for case-insensitive opens, and rejects wildcards in create names.
- `CdOpenByFileId` decodes CDFS file IDs into path-table and dirent offsets, validates directory/file type, reconstructs missing parent and child FCBs through path-table or directory scans, and then completes the open as a by-ID handle.
- `CdOpenExistingFcb` validates desired access on an already known FCB, derives CCB flags from case-sensitivity and related-open state, then delegates to `CdCompleteFcbOpen`.
- `CdOpenDirectoryFromPathEntry` opens or creates directory index FCBs from path-table entries, inserts exact/case-folded names into the prefix table, optionally performs the user open, and carefully transitions from parent to child FCB locks.
- `CdOpenFileFromFileContext` creates or finds data FCBs from directory enumeration context, inserts long-name or generated short-name prefixes where valid, preserves version/open-by-ID flags, and completes user file opens.
- `CdCompleteFcbOpen` centralizes final open work: expands `MAXIMUM_ALLOWED`, supports exclusive volume lock opens, purges before locking volumes, checks batch/exclusive oplocks, applies share-access rules, creates the CCB, sets file-object type/cache flags, updates cleanup/reference counts, records volume lock state, computes fast-I/O possibility, sets `IoStatus.Information`, and attaches section-object pointers.

## Dependencies
Depends on the CDFS internal object model from `cdprocs.h`: IRP contexts, VCB/FCB/CCB structures, prefix table helpers, path-table and dirent lookup helpers, FCB table creation/lookup, allocation-name conversion, share access, oplock callbacks, teardown/close paths, and Windows kernel I/O primitives such as file-object names, VPB pointers, `IoCheckShareAccess`, and FsRtl oplock APIs.

## Behavior/Risks
- The filesystem is read-only from the create path's point of view: file creation, overwrite-like creation, paging-file opens, target-directory opens, EA creates, and most non-`FILE_OPEN` dispositions are rejected with access or parameter errors.
- Relative opens are accepted only from user file objects with compatible related-open types; related opens through by-ID handles are marked in CCB flags so later code can preserve name semantics.
- Directory opens are accelerated through path-table lookup, while file opens that are not already in the prefix/FCB table fall back to directory scans.
- File-ID validation is defensive: offsets must lie inside the path table or directory stream, directory IDs must point to self entries, and mismatched `FILE_DIRECTORY_FILE`/`FILE_NON_DIRECTORY_FILE` options fail.
- Case-insensitive opens mutate the file object name to the exact on-disk case when a match is found, and prefix entries may be inserted in both exact and upcased forms.
- The locking order is subtle: VCB locks protect FCB-table work, FCB resources protect current traversal nodes, and several paths temporarily reference FCBs while dropping locks to avoid blocking under the VCB lock.
- Oplock paths can return `STATUS_PENDING` after handing ownership to the oplock package, so callers must not assume the IRP or context remains completable in the normal path.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/create.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/devctrl.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/devctrl.c

## Purpose
Implements CDFS device-control dispatch for user volume handles, forwarding most CD-ROM IOCTLs to the lower storage stack while handling disk-type reporting directly.

## Key Elements
- `CdCommonDevControl` decodes the file object and accepts only `UserVolumeOpen` handles.
- `IOCTL_CDROM_READ_TOC` causes a VCB verify before forwarding, so media changes are detected.
- `IOCTL_CDROM_DISK_TYPE` is handled inside CDFS: it verifies the VCB, checks for a `CDROM_DISK_DATA`-sized output buffer, copies `Vcb->DiskFlags` into the system buffer, sets the information length, and completes successfully.
- Other accepted device controls are forwarded by copying the current stack location to the next stack location, installing `CdDevCtrlCompletionRoutine`, calling the target device object, and completing only the CDFS IRP context.
- `CdDevCtrlCompletionRoutine` propagates pending state by calling `IoMarkIrpPending` when `PendingReturned` is set.

## Dependencies
Uses CDFS file-object decoding and VCB verification helpers, the lower `TargetDeviceObject`, Windows CD-ROM IOCTL definitions, and standard IRP stack/completion routines.

## Behavior/Risks
- Device controls through file or directory handles are rejected with `STATUS_INVALID_PARAMETER`.
- The direct `IOCTL_CDROM_DISK_TYPE` path relies on `Vcb->DiskFlags` having been populated during mount/recognition.
- Forwarded IOCTLs preserve the caller's stack parameters and depend on the lower CD-ROM/storage driver for final completion.
- The completion routine intentionally returns `STATUS_SUCCESS`, so forwarded IRPs continue normal I/O manager completion after pending state is fixed up.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/devctrl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/deviosup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/deviosup.c

## Purpose
Provides the low-level disk I/O support used by CDFS for noncached cooked-sector reads, XA/raw-sector reads, volume DASD writes, mount/verify reads, internal device controls, directory-sector caching, async associated-IRP fanout, synchronous waits, completion routines, pseudo audio-directory generation, and IRP-based device flushing.

## Key Elements
- Defines `IO_RUN`, the per-run descriptor used to map a logical file read into disk offset/count, user buffer position, transfer buffer/MDL, and optional associated IRP. `MAX_PARALLEL_IOS` limits fanout to five runs.
- `CdNonCachedRead` locks/maps the user buffer, handles synthetic audio root/path-table reads, enables waitable operation for directory sector-cache use, prepares cooked-sector `IO_RUN`s, chooses single versus multiple async I/O, waits for synchronous requests, copies unaligned reads back, flushes I/O buffers when needed, and cleans partial allocations on exit.
- `CdNonCachedXARead` reads raw 2352-byte sectors for XA/audio files, synthesizes a leading RIFF/audio header, limits reads to file size, prepares raw-sector runs, issues `IOCTL_CDROM_RAW_READ`, retries suspicious Mode2 Form2 failures as Yellow Book Mode2, saves the final raw sector for reuse, and always flushes I/O buffers after synchronous raw reads.
- `CdPrepareBuffers` maps cooked logical reads to disk allocation runs and allocates page-sized nonpaged scratch buffers for unaligned sector starts or sub-sector tails that cannot be issued directly.
- `CdPrepareXABuffers` maps raw-file offsets past the RIFF header to cooked disk sectors, reuses `Vcb->XASector` on matching disk offsets, chooses direct user-buffer raw-sector transfers when possible, respects raw-transfer and physical-page limits, and allocates scratch buffers for partial raw sectors.
- `CdReadDirDataThroughCache`, `CdFreeDirCache`, and `CdSyncCompletionRoutine` implement a shared/exclusive directory-sector cache that reads aligned chunks into VCB cache slots, tracks LRU replacement, handles TOC-based end-of-disc clipping, and has a ReactOS fallback when `CdromToc` is absent.
- `CdMultipleAsync`, `CdMultipleXAAsync`, and `CdSingleAsync` build and issue lower-device IRPs for cooked, raw, and single-run transfers, including async resource-owner handoff and completion routine setup.
- Completion routines update aggregate status and information, free owned associated IRPs/MDLs, signal synchronous waiters, mark async master IRPs pending, release resources for async completion, and free I/O contexts.
- `CdReadAudioSystemFile` synthesizes the path table and root directory content for audio disks, including self/parent entries and per-track pseudo entries with XA system-use data.
- `CdHijackIrpAndFlushDevice` reuses an existing IRP stack location as `IRP_MJ_FLUSH_BUFFERS`, waits through `CdSyncCompletionRoutine`, treats unsupported flush as success, and restores visible IRP status fields.

## Dependencies
Depends on CDFS allocation lookup, VCB/FCB state, XA/audio constants, directory cache resources, I/O-context allocation, MDL helpers, Windows IRP construction/completion APIs, CD-ROM raw-read structures, TOC data, sector-size conversion macros, and memory-pool tags from the CDFS codebase.

## Behavior/Risks
- Cooked reads operate in 2048-byte logical sectors, while XA reads expose raw 2352-byte sectors with a synthetic RIFF-style header, so buffer sizing and offset conversion are intentionally different between paths.
- Asynchronous cooked reads are allowed only when the request can be described safely; unaligned transfers require waitable synchronous processing because scratch buffers must be copied and flushed before completion.
- The directory-sector cache changes the normal lower-driver I/O path for directory FCBs and can force nonwaitable requests into waitable mode before read preparation.
- XA partial-sector caching stores one raw sector globally in the VCB, protected by the VCB lock; later reads may avoid a lower-device raw read when the disk offset matches.
- The Mode2 Form2 fallback mutates FCB state to remember that the file should be treated as Yellow Book Mode2 after a successful retry.
- Associated-IRP completion is delicate: synchronous multi-I/O completions return `STATUS_MORE_PROCESSING_REQUIRED` and free IRPs themselves, while async completion lets the final associated IRP complete the master path after updating status and releasing resources.
- The ReactOS fallback in the directory cache when `CdromToc` is missing explicitly risks reading past partition end, as noted by the in-source comment.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/deviosup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/dirctrl.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/dirctrl.c

## Purpose
Implements CDFS directory-control handling: directory enumeration, directory-change notification registration, enumeration-state initialization, wildcard/version matching, short-name matching, and formatting directory entries into Windows query-directory information classes.

## Key Elements
- `CdCommonDirControl` decodes the file object, accepts only `UserDirectoryOpen`, and dispatches `IRP_MN_QUERY_DIRECTORY` to `CdQueryDirectory` or `IRP_MN_NOTIFY_CHANGE_DIRECTORY` to `CdNotifyChangeDirectory`.
- `CdQueryDirectory` validates supported information classes, maps the caller buffer, initializes a `FILE_ENUM_CONTEXT`, acquires/verifies the directory FCB, initializes enumeration state, loops over matching dirents, formats result records, handles buffer overflow/partial-name rules, updates CCB restart state, releases resources, sets `IoStatus.Information`, and completes the IRP.
- Supported result classes are `FileDirectoryInformation`, `FileFullDirectoryInformation`, `FileIdFullDirectoryInformation`, `FileNamesInformation`, `FileBothDirectoryInformation`, and `FileIdBothDirectoryInformation`.
- Result formatting fills timestamps from the CD dirent time, sets directory versus read-only file attributes, propagates hidden attributes, reports file sizes/allocation sizes for files, writes CDFS dirent offsets as file indexes, emits file IDs for ID-bearing classes, and includes short names for both-directory classes when applicable.
- `CdNotifyChangeDirectory` supports notify requests even though read-only CD-ROM media will not generate ordinary changes; it verifies the VCB and queues the IRP with `FsRtlNotifyFullChangeDirectory`, then completes only the CDFS IRP context and returns pending.
- `CdInitializeEnumeration` resets or initializes CCB search state, converts the caller's query pattern to a `CD_NAME`, detects wildcard use in name/version components, upcases case-insensitive expressions, treats missing/empty/single-star as match-all, suppresses root `"."` and `".."` constant entries, chooses the starting dirent from restart/index/CCB state, ensures the directory stream file exists, positions the file context, and returns flags controlling current versus next entry and single-entry behavior.
- `CdEnumerateIndex` walks dirents from the current position, skips constant root entries when requested, ignores associated files, suppresses duplicate version entries when the search has no version component, matches long names first, generates/checks 8.3 short names when needed, and expands a found file to its last dirent before returning.

## Dependencies
Depends on CDFS directory stream creation and dirent traversal helpers, name conversion/upcasing/wildcard matching, 8.3 name generation, file-ID packing, time conversion, user-buffer mapping, FsRtl directory-notification support, FCB/CCB locking, and the CDFS `FILE_ENUM_CONTEXT` lifetime helpers.

## Behavior/Risks
- Query-directory follows Windows buffer semantics: the first entry may be partially returned with `STATUS_BUFFER_OVERFLOW`, while later entries that do not fit are not copied and enumeration resumes from that entry on a later call.
- CCB enumeration state is updated only after successful or non-error progress, recording both current dirent offset and whether the next query should return the current or next entry.
- Search expressions are stored in the CCB and reused until restart with a new pattern; restart-scan handling frees the prior allocated expression unless it was the match-all sentinel.
- Root enumeration intentionally hides constant self/parent entries for consistency with Microsoft filesystem behavior.
- Version handling affects both matching and duplicate suppression; without an explicit version search, only the first version sequence entry is returned.
- User-buffer writes are exception guarded because these requests are not necessarily buffered by the I/O manager.
- Notify requests always pend through FsRtl and depend on cleanup/cancel paths elsewhere to remove queued notifications.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/dirctrl.c -->