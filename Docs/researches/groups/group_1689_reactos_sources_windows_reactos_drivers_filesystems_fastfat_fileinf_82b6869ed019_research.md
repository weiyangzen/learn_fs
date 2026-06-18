# Group Research: group_1689_reactos_sources_windows_reactos_drivers_filesystems_fastfat_fileinf_82b6869ed019

Scope: `Docs/research_subset_a.md`

Coverage: read completely:
- `sources/windows/reactos/drivers/filesystems/fastfat/fileinfo.c`
- `sources/windows/reactos/drivers/filesystems/fastfat/filobsup.c`
- `sources/windows/reactos/drivers/filesystems/fastfat/flush.c`

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/fileinfo.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/fileinfo.c

## Purpose

`fileinfo.c` implements FastFAT file-information query and set handling for ReactOS. It backs `IRP_MJ_QUERY_INFORMATION` and `IRP_MJ_SET_INFORMATION`, including metadata queries, timestamp and attribute updates, delete-on-close state, rename and replace semantics, current position updates, allocation changes, EOF changes, valid-data-length changes, EA owner-name repair during rename, and target deletion during replace-by-rename.

This is one of the central FastFAT metadata mutation files. It coordinates FCB/DCB/VCB locking, oplock breaks, cache manager state, memory-manager section checks, directory-entry updates, tunnel-cache behavior, FAT-specific short/LFN name generation, notifications, and best-effort rollback around non-transactional on-disk changes.

## Main Entry Points

- `FatFsdQueryInformation`
  - Dispatch wrapper for `IRP_MJ_QUERY_INFORMATION`.
  - Enters the filesystem, establishes top-level IRP state, creates an IRP context, calls `FatCommonQueryInformation`, and sends exceptions through FastFAT exception handling.

- `FatFsdSetInformation`
  - Dispatch wrapper for `IRP_MJ_SET_INFORMATION`.
  - Same top-level IRP and exception pattern as query, then calls `FatCommonSetInformation`.

- `FatCommonQueryInformation`
  - Decodes the file object and serves supported query classes.
  - Rejects user volume opens.
  - Acquires the VCB exclusively for name/all-information queries because full-name construction must synchronize with deletion/rename.
  - Acquires the FCB shared for normal files/directories except most paging-file cases, then verifies the FCB.
  - Writes result length through the IRP information field; negative remaining length is normalized to `STATUS_BUFFER_OVERFLOW`.

- `FatCommonSetInformation`
  - Decodes the file object and dispatches supported set classes.
  - Rejects user volume opens and root DCB mutation, except root delete returns `STATUS_CANNOT_DELETE`.
  - Performs oplock checks for file size/allocation/VDL changes and for rename/delete cases.
  - Acquires the VCB exclusively for rename and disposition operations to serialize with create and namespace changes.
  - Acquires the FCB exclusively for mutation unless paging-file deadlock rules apply.
  - Dispatches to the specific setter and unpins repinned BCBs before completion.

## Query Support

- `FatQueryBasicInfo`
  - Returns creation/access/write times and attributes.
  - Root directory reports synthetic January 1, 1980 timestamps converted through local/system time.
  - Adds `FILE_ATTRIBUTE_TEMPORARY` from FCB state and falls back to `FILE_ATTRIBUTE_NORMAL` when no attributes are set.

- `FatQueryStandardInfo`
  - Returns link count 1, delete-pending state, directory flag, allocation size, and EOF.
  - For normal files, lazily resolves allocation size if it is still the lookup hint.

- `FatQueryInternalInfo`
  - Returns the generated FAT file ID from the FCB.

- `FatQueryEaInfo`
  - Currently zeros `FILE_EA_INFORMATION`; the richer EA length lookup is disabled under `#if 0`.
  - Still keeps BCB cleanup structure for the disabled path.

- `FatQueryPositionInfo`
  - Returns `FileObject->CurrentByteOffset`.

- `FatQueryNameInfo`
  - Builds full path information from `Fcb->FullFileName`, synthesizing it if needed.
  - For non-normalized queries opened by short name, trims the final long-name component and appends the Unicode converted short name.
  - Handles partial copy with returned full available length and overflow status signaling.

- `FatQueryShortNameInfo`
  - Converts the stored OEM 8.3 short name to Unicode and returns it as `FILE_NAME_INFORMATION`.

- `FatQueryNetworkInfo`
  - Returns network-open metadata: times, attributes, allocation size, and EOF.
  - Mirrors basic/standard behavior for root timestamps, temporary attributes, normal fallback, and lazy allocation lookup.

## Set Support

- `FatSetBasicInfo`
  - Applies timestamps and FAT-supported attribute bits.
  - Treats `-1` timestamp inputs as "do not update this field later" and records that in CCB flags.
  - Converts NT times to FAT timestamps, with special handling for local-time values between December 31, 1979 and January 1, 1980.
  - Honors `FatData.ChicagoMode` for creation/access-time and long-name era behavior.
  - Rejects directory attributes on files and temporary attributes on directories.
  - Updates FCB state, dirent fields, dirty BCB state, and notify filters.
  - Rounds or truncates in-memory timestamps to FAT granularity.
  - Breaks parent directory oplocks on newer NT targets when access/write times or attributes change.

- `FatSetDispositionInfo`
  - Sets or clears delete-on-close.
  - Rejects deletion of read-only files, root directories, image-mapped files, and non-empty directories.
  - Checks write-protection by touching media: special floppy handling writes through a FAT byte; other media dirties the object dirent BCB.
  - Sets `FCB_STATE_DELETE_ON_CLOSE` and `FileObject->DeletePending`.
  - Notifies directory-change waiters when a directory becomes delete-pending.

- `FatSetRenameInfo`
  - Implements the full FAT rename/replace path.
  - Handles simple renames using the IRP buffer and fully qualified renames using a target directory file object.
  - Rejects root renames and cross-volume target directories.
  - For directory renames, walks the subtree to reject open descendants unless breakable batch oplocks can be broken, purges referenced file objects, and clears descendant cached full names.
  - Builds upcased Unicode names, OEM short-name candidates, tunnel-cache state, LFN requirements, and case-only rename detection.
  - In non-Chicago mode, requires 8.3-valid names and disables LFN/tunnel long-name use.
  - Locates target dirents, enforces `ReplaceIfExists`, rejects replacing directories/read-only files, and checks target FCB open/image-section state.
  - Allocates new dirent space when moving directories or changing required LFN dirent count.
  - Performs rename in phases: notify source removal/old-name, capture source dirent, tunnel source name, optionally delete source dirents, optionally delete replacement target, select final short/LFN names, write dirents, handle LFN sequences crossing page boundaries, update FCB dirent offsets and parent queue, update `..` for moved directories, rebuild FCB names, report final notifications, and rename EAs.
  - If an exception occurs during a sensitive on-disk/in-memory transition, marks the FCB bad rather than pretending rollback is complete.

- `FatSetPositionInfo`
  - Updates `FileObject->CurrentByteOffset`.
  - For noncached handles, enforces device alignment before accepting the new position.

- `FatSetAllocationInfo`
  - Changes allocation size for files only.
  - Rejects directories and invalid FAT I/O ranges.
  - Resolves lazy allocation size before mutation.
  - Initializes a cache map temporarily when a data section exists without a shared cache map.
  - Marks `FCB_STATE_TRUNCATE_ON_CLOSE` and the file object modified.
  - Extends allocation via `FatAddFileAllocation`; shrinks via `FatTruncateFileAllocation`.
  - When shrinking below file size, checks purge-failure mode and `MmCanFileBeTruncated`, serializes with paging I/O, adjusts file size/VDL/valid-data-to-disk, updates cache-manager sizes, writes dirent size, and reports size notification.
  - Restores in-memory file-size state on abnormal termination before the irreversible cache/dirent point.

- `FatSetEndOfFileInfo`
  - Changes EOF for files only.
  - Rejects directories and invalid ranges.
  - Supports `AdvanceOnly`, used for lazy file-size advancement into the dirent without reducing size.
  - Extends allocation when EOF exceeds allocation size.
  - On truncation, checks purge-failure mode and `MmCanFileBeTruncated`, then serializes with paging I/O.
  - Updates FCB file size, VDL, valid-data-to-disk, cache-manager sizes, dirent size, notification state, and truncate-on-close state.
  - On abnormal termination, restores in-memory sizes and attempts no-raise dirent rollback to avoid suspend/resume corruption cases.

- `FatSetValidDataLengthInfo`
  - Allows explicit VDL changes only for handles with manage-volume access.
  - Files only; VDL can only move forward and cannot exceed file size.
  - Requires `MmCanFileBeTruncated`.
  - Flushes and purges any existing data section before advancing VDL.
  - Updates FCB VDL, valid-data-to-disk, cache sizes, and modified state.

- `FatRenameEAs`
  - For non-FAT32 rename cases with EA metadata, opens the EA file, reads the EA set by old OEM name and EA index, updates the owner file name to the FCB’s new short name, marks the EA range dirty, and flushes the EA cache.
  - Catches FastFAT-handled exceptions and treats EA rename repair as best effort.

- `FatDeleteFile`
  - Used by rename-replace to remove an existing target file.
  - Removes matching cached FCB names from the prefix table, marks unopened cached target FCBs delete-on-close, zeroes size/VDL/cluster state under paging I/O synchronization, then creates a temporary FCB to truncate allocation and delete the dirent.

## Key Dependencies and Integration

- Depends on `fatprocs.h` for FastFAT structures, locking, exception, cache, allocation, dirent, EA, notify, tunnel, and name helpers.
- Uses I/O manager file objects, IRPs, current stack locations, share/file object flags, and delete-pending state.
- Uses FSRTL oplocks, notifications, tunnel cache, and name comparison/conversion helpers.
- Uses cache manager functions including `CcSetFileSizes`, `CcFlushCache`, `CcPurgeCacheSection`, cache-map initialization, and BCB pin/dirty/repin operations.
- Uses memory manager section checks including `MmFlushImageSection` and `MmCanFileBeTruncated`.
- Coordinates with create/cleanup/close behavior through FCB state flags such as delete-on-close, temporary, truncate-on-close, paging-file, and names-in-splay-tree.

## Important Invariants

- Namespace-changing operations acquire the VCB exclusively and reject recursion while create is in progress.
- Size-changing operations must coordinate with oplocks, paging I/O, MM truncation checks, cache-manager file sizes, and dirent updates.
- FAT is not transactional; some operations intentionally switch from reversible validation to irreversible mutation, then mark the FCB bad on exceptions.
- Delete-on-close is only set after delete feasibility has been checked.
- Rename of directories must ensure no open descendants remain, except requests that can be pended to break batch oplocks.
- Short-name versus long-name identity is tracked through CCB flags, FCB final-name length, tunnel-cache lookup, and prefix-table updates.
- Root DCB mutation is mostly forbidden.

## Notable Risks

- Rename is highly stateful and has many partial-failure windows involving old dirents, new dirents, target deletion, parent queues, cached names, and `..` updates.
- Allocation and EOF truncation depend on correct MM/cache purge behavior; stale mappings are explicitly treated as corruption risks.
- Some EA handling is best effort and can silently leave repair to later disk checking.
- Query buffer overflow is signaled indirectly by negative remaining length, so helper length accounting must stay exact.
- Time conversion depends on FAT granularity, local time, and special 1979/1980 compatibility behavior.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/fileinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/filobsup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/filobsup.c

## Purpose

`filobsup.c` provides FastFAT file-object support routines. It attaches FastFAT VCB/FCB/DCB/CCB pointers to Windows file objects, decodes those pointers back into typed open kinds, and forces cache/section misses for FCB trees during operations such as volume lock, purge, rename, overwrite, or teardown.

The file is small but foundational: most dispatch paths rely on `FatDecodeFileObject` to classify handles, and several namespace/cache operations rely on `FatPurgeReferencedFileObjects` and `FatForceCacheMiss` to make cached sections disappear when possible.

## Main Functions

- `FatSetFileObject`
  - Initializes `FileObject->FsContext`, `FileObject->FsContext2`, and `FileObject->Vpb`.
  - Accepts the FastFAT open type and validates the expected object combination with assertions:
    - `UserFileOpen`: FCB plus CCB.
    - `EaFile`: FCB without CCB.
    - `UserDirectoryOpen`: DCB/root DCB plus CCB.
    - `UserVolumeOpen`: VCB plus CCB.
    - `VirtualVolumeFile`: VCB without CCB.
    - `DirectoryFile`: DCB/root DCB without CCB.
    - `UnopenedFileObject`: no backing object.
  - Copies the VCB’s VPB for volume opens or the owning FCB/DCB’s VCB VPB for file/directory opens.
  - Mirrors `FCB_STATE_TEMPORARY` into `FO_TEMPORARY_FILE`.

- `FatDecodeFileObject`
  - Reads `FsContext` and `FsContext2` and returns a `TYPE_OF_OPEN`.
  - If `FsContext` is null, returns `UnopenedFileObject`.
  - If `FsContext` is a VCB, returns `VirtualVolumeFile` or `UserVolumeOpen` depending on whether a CCB exists.
  - If `FsContext` is a DCB/root DCB, returns `DirectoryFile` or `UserDirectoryOpen`.
  - If `FsContext` is an FCB with a CCB, returns `UserFileOpen`.
  - If `FsContext` is an FCB without a CCB, returns `EaFile` only when the FCB is the volume EA FCB.
  - Bugchecks on unexpected node-type combinations because corrupted file-object context means the filesystem cannot safely continue.

- `FatPurgeReferencedFileObjects`
  - Forces delayed closes first with `FatFspClose`.
  - Walks the FCB/DCB subtree top-down using `FatGetNextFcbTopDown`.
  - Gets the next node before acting on the current node because purging can cause the current FCB and ancestors to vanish.
  - Skips volume-ID entries and calls `FatForceCacheMiss` on other nodes.
  - Requires a waitable IRP context.

- `FatForceCacheMiss`
  - Flushes and purges cache/MM sections for a single FCB/DCB.
  - Requires the VCB to be held exclusively or the volume to be locked.
  - Raises `STATUS_CANT_WAIT` if the IRP context is not waitable.
  - For directories with children, acquires child FCB resources first to avoid parent directory pinning and cache-manager deadlocks.
  - Acquires the target FCB exclusively, sets `FCB_STATE_FORCE_MISS_IN_PROGRESS`, and clears the VCB deleted-FCB marker.
  - Optionally flushes the file through `FatFlushFile`.
  - If the FCB was not deleted during the flush, flushes image sections before purging data cache sections.
  - Releases acquired child resources and releases the target FCB only if it survived the purge path.

## Key Dependencies and Integration

- All functions depend on FastFAT node type codes stored in common node headers.
- `FatSetFileObject` and `FatDecodeFileObject` are used throughout create, cleanup, close, query, set, flush, read/write, and FSCTL paths.
- `FatPurgeReferencedFileObjects` is used by higher-level operations that need cached sections closed before namespace or volume operations proceed.
- `FatForceCacheMiss` integrates with `FatFlushFile`, `MmFlushImageSection`, `CcPurgeCacheSection`, FCB resource acquisition, delayed-close processing, and VCB deleted-FCB state.

## Important Invariants

- File-object `FsContext` is the primary type discriminator for FastFAT opens.
- `FsContext2` being null or non-null distinguishes user opens from internal stream opens for the same node type.
- Cache purge can trigger final close and FCB deletion, so callers must not assume the FCB survives flush/purge.
- The next subtree node must be computed before purging the current node.
- `FatForceCacheMiss` must run only when waiting is allowed and namespace/volume synchronization prevents concurrent teardown races.

## Notable Risks

- A stale or corrupted `FsContext` causes a bugcheck rather than recoverable failure.
- Cache purge paths are sensitive to resource ordering between directories, children, cache-manager flush callbacks, and close teardown.
- Purging image sections before data sections is required because data purge can make image-section state disappear, but not the reverse.
- The implementation relies on VCB `VCB_STATE_FLAG_DELETED_FCB` to decide whether releasing the FCB is still legal after cache-manager activity.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/filobsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/flush.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/flush.c

## Purpose

`flush.c` implements FastFAT flush handling and lower-device flush propagation. It backs `IRP_MJ_FLUSH_BUFFERS`, flushes cached file data, directory metadata, FAT allocation metadata, whole volumes, selected FAT entry ranges, and selected dirent pages. It also contains helper completion routines for normal flush pass-through and for hijacking an existing IRP to send a lower-device flush.

The file is the bridge between FastFAT’s cache/metadata state and durable media state. It coordinates FCB/VCB locking, cache-manager flushes, BCB repinning, FAT page writeback, directory-entry writeback, dirty-volume cleanup, and target-device flushes.

## Main Entry Points

- `FatFsdFlushBuffers`
  - Dispatch wrapper for `IRP_MJ_FLUSH_BUFFERS`.
  - Enters the filesystem, establishes top-level IRP state, creates an IRP context, calls `FatCommonFlushBuffers`, and sends exceptions through FastFAT exception handling.

- `FatCommonFlushBuffers`
  - Common flush implementation for file, directory, root, and volume opens.
  - Posts to the FSP if the request cannot wait because `CcFlushCache` is synchronous.
  - On newer NT targets, charges disk-accounting flush activity to the originating thread or current thread.
  - Decodes the file object and dispatches by `TYPE_OF_OPEN`.

## Flush Behavior by Open Type

- `VirtualVolumeFile`, `EaFile`, `DirectoryFile`
  - Flush request is effectively a no-op at the FastFAT layer.

- `UserFileOpen`
  - Acquires the FCB exclusively and verifies it.
  - Calls `FatFlushFile` to flush the file data section.
  - On success, marks `FO_FILE_SIZE_CHANGED`, updates the dirent from the FCB, and records whether FAT flushing is required.
  - Walks parent DCBs upward, verifies each best effort, and flushes parent directory files so dirent updates reach disk.
  - Flushes FAT metadata through `FatFlushFat` when `FCB_STATE_FLUSH_FAT` is set.
  - Sets write-through on the IRP context so related metadata modifications complete with the request.

- `UserDirectoryOpen`
  - Non-root directory flushes do nothing directly.
  - Root directory flush falls through to whole-volume flushing.

- `UserVolumeOpen` and root DCB flush
  - Acquires the VCB exclusively.
  - Calls `FatFlushVolume`.
  - If the volume dirty flag is set, cancels pending clean-volume timer/DPC work.
  - Marks the volume clean when it was not mounted dirty.
  - Re-enables eject on removable media when no boot or paging file prevents it.

- Final pass-through
  - On normal termination, copies the IRP stack to the next driver and sends a flush to the target device.
  - `FatFlushCompletionRoutine` preserves pending state and maps lower `STATUS_INVALID_DEVICE_REQUEST` to success while restoring the FastFAT flush status.
  - On newer NT targets, data-only/no-sync flush minor functions skip the lower-device flush path.

## Helper Functions

- `FatFlushDirectory`
  - Non-recursively flushes a DCB tree.
  - Requires the VCB exclusively.
  - Temporarily forces write-through and wait flags if not already set.
  - First walks files, then directories, so file sizes and timestamps are reflected in directory entries before directories are flushed.
  - Skips the EA FCB and deleted files.
  - For file FCBs:
    - Acquires the FCB exclusively.
    - Verifies it best effort.
    - Applies pending truncate-on-close allocation truncation.
    - Reads the dirent and corrects `Dirent->FileSize` if it differs from the FCB.
    - Unpins the dirent BCB before flushing to avoid cache-manager/close deadlocks.
    - Calls `FatFlushFile`.
  - For DCBs:
    - Verifies best effort.
    - Calls `FatFlushFile` for good directory FCBs.
  - Aggregates flush errors but continues flushing the tree where possible.
  - Unpins repinned BCBs and restores temporarily modified IRP-context flags.

- `FatFlushFat`
  - Flushes dirty FAT pages for the whole volume.
  - Returns success immediately for write-protected volumes.
  - Verifies the VCB best effort and returns `STATUS_FILE_INVALID` if not good.
  - For FAT16/FAT32, walks FAT pages and uses `CcPinRead` with `PIN_IF_BCB` to touch only cached dirty ranges.
  - For FAT12, pins the whole FAT.
  - Marks pinned data dirty, repins, unpins, then unpins repinned BCBs with write-through and records I/O status.

- `FatFlushVolume`
  - Flushes all files/directories from the root DCB through `FatFlushDirectory`.
  - Flushes FAT metadata through `FatFlushFat`.
  - Re-enables eject for removable, non-boot, non-paging media.
  - Returns the first/last meaningful failed status while attempting both directory and FAT flush work.

- `FatFlushFile`
  - Calls `CcFlushCache` for the FCB section object pointers.
  - If the FCB was not deleted during the flush, takes the paging I/O resource exclusively to serialize with lazy writer activity.
  - If `FlushType == FlushAndInvalidate`, marks the FCB bad under paging-I/O synchronization.
  - Returns the cache flush status.

- `FatHijackIrpAndFlushDevice`
  - Reuses the current IRP by copying the stack location to the next stack, changing it to `IRP_MJ_FLUSH_BUFFERS`, installing `FatHijackCompletionRoutine`, and sending it to the target device.
  - Waits on an event if the lower driver returns pending.
  - Treats lower `STATUS_INVALID_DEVICE_REQUEST` as success.
  - Resets the IRP’s visible I/O status after the internal flush.

- `FatFlushFatEntries`
  - Flushes the cache range containing a FAT cluster run.
  - Computes byte offset/count differently for FAT12, FAT16, and FAT32.
  - Calls `CcFlushCache`, then uses `FatHijackIrpAndFlushDevice` to force the target device flush.
  - Normalizes and raises failures.

- `FatFlushDirentForFile`
  - Flushes the cache page containing an FCB’s parent-directory dirent.
  - Then hijacks the originating IRP to flush the target device.
  - Normalizes and raises failures.

- `FatFlushCompletionRoutine`
  - Completion routine for ordinary pass-through flush IRPs.
  - Marks pending when needed.
  - If lower flush succeeded or is unsupported, restores the FastFAT status supplied in the context.

- `FatHijackCompletionRoutine`
  - Signals the waiting event and returns `STATUS_MORE_PROCESSING_REQUIRED` so the hijacked IRP is not completed normally by the lower stack.

## Key Dependencies and Integration

- Uses `FatDecodeFileObject` to classify flush targets.
- Integrates with `FatVerifyFcb`, `FatVerifyVcb`, `FatUpdateDirentFromFcb`, `FatSetFileSizeInDirent` indirectly through dirent update paths, `FatTruncateFileAllocation`, `FatMarkVolume`, and media eject toggling.
- Uses cache-manager APIs: `CcFlushCache`, `CcPinRead`, `CcSetDirtyPinnedData`, `CcRepinBcb`, `CcUnpinData`, `CcUnpinRepinnedBcb`.
- Uses resource synchronization through FCB resources, VCB resources, and paging I/O resources.
- Uses lower-driver IRP forwarding for durable device flushes after filesystem cache flushes.

## Important Invariants

- Flushes that call cache manager synchronously must run in a waitable context.
- File data should be flushed before parent directories so dirent file sizes/times can be made durable.
- FAT metadata must be flushed when allocation state changed.
- Dirent BCBs are unpinned before file flushes because flush-triggered close can tear down parts of the tree.
- Lower devices that do not support flush are not treated as fatal for normal flush completion.
- Whole-volume flush requires exclusive VCB ownership.

## Notable Risks

- Flush paths deliberately continue after expected verification/corruption errors, so return status can represent a later aggregated failure while some objects were still flushed.
- Cache-manager flushes can cause FCB final close and deletion; code must check deleted-FCB state before touching or releasing FCBs.
- `FatHijackIrpAndFlushDevice` mutates an existing IRP stack for internal use and must restore visible I/O status afterward.
- FAT12 whole-FAT flushing is heavier than FAT16/FAT32 page-by-page dirty-range flushing.
- Correct durability depends on both FastFAT cache flushes and successful target-device flush propagation where supported.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/flush.c -->