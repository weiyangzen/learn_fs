# Group Research: group_1841_windows_driver_samples_sources_windows_windows_driver_samples_files_f92d4d9e6378

Scope: `Docs/research_subset_a.md`, source tree `sources/windows/windows-driver-samples`.

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/fileinfo.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/fileinfo.c

## Role

`fileinfo.c` implements FastFAT file information query and set handling for `IRP_MJ_QUERY_INFORMATION` and `IRP_MJ_SET_INFORMATION`. It is the central metadata mutation path for file size, allocation size, delete-on-close, rename, timestamps, attributes, current byte offset, valid data length, and returned name/standard/basic/network-open metadata.

## Entry Points

- `FatFsdQueryInformation`: FSD dispatch wrapper for query information. Enters the filesystem, establishes top-level IRP state, creates an IRP context, calls `FatCommonQueryInformation`, and funnels exceptions through `FatProcessException`.
- `FatFsdSetInformation`: Same pattern for set information, calling `FatCommonSetInformation`.

Both wrappers are pageable and ignore the `VolumeDeviceObject` parameter after dispatch setup.

## Query Flow

`FatCommonQueryInformation` decodes the `FILE_OBJECT` through `FatDecodeFileObject`, rejects `UserVolumeOpen`, and supports `UserFileOpen`, `UserDirectoryOpen`, and internal `DirectoryFile`.

Important synchronization:

- Acquires the VCB exclusive for `FileNameInformation`, `FileNormalizedNameInformation`, and `FileAllInformation` because full-name construction must be synchronized with deletion.
- Acquires the FCB shared except for paging files, with a removable-media exception for ReadyBoost-style paging-file opens.
- Verifies the FCB before reading metadata.

Supported classes:

- `FileAllInformation`
- `FileBasicInformation`
- `FileStandardInformation`
- `FileInternalInformation`
- `FileEaInformation`
- `FilePositionInformation`
- `FileNameInformation`
- `FileNormalizedNameInformation`
- `FileAlternateNameInformation`
- `FileNetworkOpenInformation`

Unsupported classes return `STATUS_INVALID_PARAMETER`.

Buffer accounting is done by decrementing a local `Length`. If it becomes negative, the final status is `STATUS_BUFFER_OVERFLOW`, length is forced to zero, and `IoStatus.Information` reports bytes actually filled.

## Query Helpers

- `FatQueryBasicInfo`: Returns creation, last access, last write, and FAT attributes. Root directories synthesize `1/1/1980` via local-to-system conversion. Temporary FCB state maps to `FILE_ATTRIBUTE_TEMPORARY`; empty attributes become `FILE_ATTRIBUTE_NORMAL`.
- `FatQueryStandardInfo`: Returns one hard link, delete-pending state, allocation size, EOF, and directory flag. It resolves lazy allocation-size hints with `FatLookupFileAllocationSize`.
- `FatQueryInternalInfo`: Uses `FatGenerateFileIdFromFcb`.
- `FatQueryEaInfo`: Zeroes EA size. The older EA-length lookup block is disabled with `#if 0`.
- `FatQueryPositionInfo`: Copies `FileObject->CurrentByteOffset`.
- `FatQueryNameInfo`: Builds full names, optionally normalized. If the open was by short name and the file has an LFN, it returns the path prefix plus converted short name so callers see the name context they opened. Handles overflow by setting `*Length = -1`.
- `FatQueryShortNameInfo`: Converts the FCB short OEM name to Unicode and returns it as alternate-name information.
- `FatQueryNetworkInfo`: Combines basic and standard-style metadata for network open information, including root timestamp synthesis and allocation lookup.

## Set Flow

`FatCommonSetInformation` decodes the object, rejects volume opens, performs oplock checks for allocation/EOF/VDL changes on normal files, rejects root DCB mutations, and acquires:

- VCB exclusive for disposition and rename, preventing concurrent creates.
- FCB exclusive for most set operations, except paging-file deadlock avoidance with removable-media exception.

It verifies the FCB and does rename/delete oplock checks where needed. Supported classes:

- `FileBasicInformation`
- `FileDispositionInformation`
- `FileRenameInformation`
- `FilePositionInformation`
- `FileAllocationInformation`
- `FileEndOfFileInformation`
- `FileValidDataLengthInformation`

`FileLinkInformation` returns `STATUS_INVALID_DEVICE_REQUEST`; other unsupported classes return `STATUS_INVALID_PARAMETER`.

## Metadata Mutation Helpers

`FatSetBasicInfo` updates timestamps and attributes in the dirent and FCB.

Key behavior:

- `-1` timestamp values mean "do not update"; corresponding CCB user-set flags are recorded.
- FAT timestamp conversion validates values and special-cases local `12/31/1979` into FAT `1/1/1980`.
- Creation time is rounded to FAT precision, last access is truncated to local-day granularity, and last write is rounded to two seconds.
- Only FAT-supported attributes are persisted.
- Directory attribute consistency is enforced.
- Temporary state is mirrored to `FCB_STATE_TEMPORARY` and `FO_TEMPORARY_FILE`.
- Parent directory oplocks are broken on Windows 8+ when relevant metadata changes.

`FatSetDispositionInfo` implements delete-on-close.

It rejects deletion of:

- Read-only files.
- User-mapped image files that cannot be flushed.
- Root directories.
- Non-empty directories.

It dirties media to detect write protection. Floppy media receives special FAT-area touch/write-through handling; other media dirty the target dirent BCB. On success it sets `FCB_STATE_DELETE_ON_CLOSE` and `FileObject->DeletePending`; for directories it notifies directory-change waiters. Clearing disposition removes those flags.

`FatSetPositionInfo` updates `CurrentByteOffset`, enforcing device alignment for non-buffered file objects.

## Rename Handling

`FatSetRenameInfo` is the largest and most complex routine in the file. It performs a two-phase rename:

Phase 1 validates legality and allocates/locates required metadata:

- Rejects root rename.
- For directory renames, walks child FCBs bottom-up, rejecting active children unless batch oplocks can be broken.
- Purges referenced file objects for directories.
- Determines target DCB and new name from either simple rename buffer or target directory file object.
- Handles same-name, case-only rename, and cross-directory rename detection.
- Converts candidate names to upcased OEM 8.3 form when possible.
- Looks up tunnel cache data for restored short/long names and creation time.
- Determines whether LFN dirents are required.
- In non-Chicago mode, requires valid 8.3 names and disables LFN/case magic.
- Checks for target collisions and replacement legality. Replacement rejects directories and read-only targets, and rejects targets with active opens or image sections unless oplock handling posts the IRP.
- Allocates new dirent space when moving directories or changing required dirent count.

Phase 2 mutates on-disk and in-memory structures:

- Sends removal or old-name rename notifications.
- Copies the source dirent, tunnels source metadata, and enters a state where abnormal failure may invalidate the FCB.
- Deletes source dirents if moving allocation.
- Deletes replacement targets with `FatDeleteFile`.
- Selects final short/LFN names, constructs new dirents, and handles LFN-plus-dirent page-boundary splits.
- Restores tunneled timestamps when applicable.
- Removes old names from prefix structures and frees cached full/exact-case names.
- Updates dirent offsets, parent DCB queue membership, and parent DCB pointer.
- Breaks parent directory oplocks on Windows 8+.
- For cross-directory directory moves, updates the `..` dirent cluster pointer.
- Reconstructs FCB short/long/full names and prefix entries.
- Marks file objects modified and suppresses automatic last-write update where appropriate.
- Emits final notifications as modified, added, or renamed-new-name depending on replacement/cross-directory status.
- Renames OS/2 EA owner metadata on non-FAT32 when needed.

Failure handling is intentionally non-transactional; after certain disk mutations, abnormal termination can only mark the FCB bad.

## Size, Allocation, and VDL

`FatSetAllocationInfo` changes file allocation size.

- Directories are rejected.
- Range validity is checked with `FatIsIoRangeValid`.
- Lazy allocation-size hints are resolved.
- If a data section exists without a shared cache map, it initializes caching to coordinate with Cache Manager.
- Expansions call `FatAddFileAllocation`.
- Shrinks may truncate file size, VDL, and valid-data-to-disk after `MmCanFileBeTruncated` and purge-failure checks.
- Paging I/O is synchronized while truncating.
- Cache sizes are updated with `CcSetFileSizes`.
- Dirent file size and notifications are updated after irreversible truncation.
- Abnormal termination can unwind in-memory sizes before the irreversible point.

`FatSetEndOfFileInfo` changes EOF.

- Only regular files are allowed.
- `AdvanceOnly` lazily advances the dirent file size without reducing it, used for lazy file-size writeback.
- Expands allocation when EOF exceeds allocation.
- Shrinks coordinate with purge failure mode, `MmCanFileBeTruncated`, and paging I/O.
- Updates FCB file size, VDL, valid-data-to-disk, cache sizes, dirent size, notifications, and truncate-on-close state.
- On abnormal termination it restores in-memory sizes and attempts no-raise dirent size rollback for suspend/removable-media failure cases.

`FatSetValidDataLengthInfo` explicitly changes VDL.

- Requires `CCB_FLAG_MANAGE_VOLUME_ACCESS`.
- Only files are allowed.
- VDL may only move forward and may not exceed file size.
- Rejects mapped files that cannot be purged.
- Flushes and purges existing cache before exposing new valid data.
- Updates `ValidDataLength`, `ValidDataToDisk`, cache sizes, and modified-file state.

## EA and Replacement Deletion Helpers

`FatRenameEAs` best-effort updates the owner filename in the EA set for non-FAT32 rename cases. It catches FAT exceptions internally and suppresses failures.

`FatDeleteFile` deletes a replacement target during rename. It removes matching open-but-clean FCBs from name tables, marks them delete-on-close with zero size and cluster state under paging I/O synchronization, then creates a temporary FCB for the target dirent, truncates allocation to zero, deletes the dirent, and deletes the temporary FCB.

## Key Dependencies

- File-object decoding and type taxonomy from `FatDecodeFileObject`.
- FCB/VCB resource acquisition helpers.
- Oplock package: `FsRtlCheckOplock`, `FsRtlCheckOplockEx`.
- Cache and memory manager: `CcSetFileSizes`, `CcFlushCache`, `CcPurgeCacheSection`, `MmCanFileBeTruncated`, `MmFlushImageSection`.
- Directory/name machinery: `FatLocateDirent`, `FatCreateNewDirent`, `FatDeleteDirent`, `FatConstructDirent`, `FatConstructNamesInFcb`, `FatSetFullFileNameInFcb`, `FatRemoveNames`.
- Tunnel cache: `FsRtlFindInTunnelCache`, `FatTunnelFcbOrDcb`.
- Notifications: `FatNotifyReportChange`, `FsRtlNotifyFullChangeDirectory`.

## Implementation Notes

This file encodes many filesystem correctness constraints:

- FAT timestamp precision and local-time conversion are handled explicitly.
- Rename is not transactional; the code documents the points where recovery is impossible and uses FCB invalidation as containment.
- Paging-file operations avoid acquiring normal FCB resources to prevent Memory Manager deadlocks.
- ReadyBoost/removable-media exceptions preserve mapping validation behavior across power transitions.
- Cache Manager state must be kept coherent whenever file size, allocation size, or VDL changes.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/fileinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/filobsup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/filobsup.c

## Role

`filobsup.c` implements FastFAT file-object support. It binds Windows `FILE_OBJECT` instances to FastFAT VCB/FCB/DCB/CCB structures, decodes those bindings back into open types, and provides cache/section purge helpers used by rename, flush, teardown, and invalidation paths.

## File Object Setup

`FatSetFileObject` writes filesystem-private pointers into a `FILE_OBJECT`.

It supports these open shapes:

- `UnopenedFileObject`
- `UserFileOpen`: FCB plus CCB
- `EaFile`: FCB without CCB
- `UserDirectoryOpen`: DCB/root DCB plus CCB
- `UserVolumeOpen`: VCB plus CCB
- `VirtualVolumeFile`: VCB without CCB
- `DirectoryFile`: DCB/root DCB without CCB

The routine asserts type consistency rather than dynamically recovering from invalid combinations. When the object is attached to an FCB/DCB, it sets `FileObject->Vpb` from the owning VCB. If the FCB is temporary, it also sets `FO_TEMPORARY_FILE`. Finally it stores:

- `FileObject->FsContext = VcbOrFcbOrDcb`
- `FileObject->FsContext2 = Ccb`

## File Object Decode

`FatDecodeFileObject` reverses the binding and returns `TYPE_OF_OPEN`.

Behavior by `FsContext` node type:

- `NULL`: returns `UnopenedFileObject`; all outputs are null.
- `FAT_NTC_VCB`: returns `VirtualVolumeFile` if no CCB, otherwise `UserVolumeOpen`.
- `FAT_NTC_ROOT_DCB` or `FAT_NTC_DCB`: returns `DirectoryFile` if no CCB, otherwise `UserDirectoryOpen`.
- `FAT_NTC_FCB`: returns `UserFileOpen` when a CCB exists; otherwise returns `EaFile` only if the FCB is the VCB EA FCB.
- Unknown or inconsistent types bugcheck.

This routine is a key dependency for dispatch paths in `fileinfo.c` and `flush.c`.

## Purging Referenced File Objects

`FatPurgeReferencedFileObjects` walks a subtree non-recursively starting at an FCB/DCB and tries to force Cache Manager or Memory Manager to drop referenced file objects and sections.

Key behavior:

- Requires wait-capable IRP context.
- Forces delayed closes first with `FatFspClose`.
- Uses top-down enumeration with `FatGetNextFcbTopDown`.
- Computes the next node before acting on the current node, because purging can cause the current node and ancestors to disappear.
- Skips volume-label style entries marked `FAT_DIRENT_ATTR_VOLUME_ID`.
- Calls `FatForceCacheMiss` for each relevant FCB/DCB.

This is used by directory rename handling to make stale child FCBs disappear before moving a subtree.

## Forcing Cache Misses

`FatForceCacheMiss` flushes and purges cache/section state for an FCB.

Preconditions and locking:

- Requires the VCB to be acquired exclusive or locked.
- Requires wait-capable context; otherwise raises `STATUS_CANT_WAIT`.
- For directory FCBs with children, acquires child FCB resources first to prevent parent directory pinning conflicts.
- Acquires the target FCB exclusive.
- Sets `FCB_STATE_FORCE_MISS_IN_PROGRESS` and clears `VCB_STATE_FLAG_DELETED_FCB` before work.

Flush/purge behavior:

- If `FlushType` is nonzero, calls `FatFlushFile`.
- If the flush did not delete the FCB, inspects section object pointers.
- Flushes image sections first with `MmFlushImageSection`, because data-section purge can make image sections go away but not vice versa.
- Purges data sections with `CcPurgeCacheSection`.

Cleanup:

- Releases any acquired child FCBs.
- If the FCB was not deleted during cache purge, clears `FCB_STATE_FORCE_MISS_IN_PROGRESS` and releases the FCB.
- If close deleted the FCB, close-side logic is expected to have released the resource before freeing.

## Key Dependencies

- Node type macros and FastFAT object model: VCB, FCB, DCB, CCB.
- Cache and memory manager: `CcPurgeCacheSection`, `MmFlushImageSection`.
- Flush helper: `FatFlushFile`.
- Tree walks: `FatGetNextFcbTopDown`.
- Delayed close: `FatFspClose`.

## Implementation Notes

The file is small but foundational. Correct `FsContext`/`FsContext2` setup is what lets the rest of FastFAT distinguish user files, directories, volume opens, internal directory streams, EA streams, and the virtual volume file. The purge path is carefully ordered around Cache Manager side effects: acting on an FCB can indirectly trigger final close and subtree teardown, so enumeration and resource release are structured around disappearing nodes.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/filobsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/flush.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/flush.c

## Role

`flush.c` implements FastFAT flush handling for `IRP_MJ_FLUSH_BUFFERS` and internal helpers for flushing files, directories, FAT metadata, dirent pages, FAT-entry ranges, volumes, and target devices. It coordinates filesystem metadata, Cache Manager state, FAT dirty ranges, removable-media clean state, and pass-through device flushes.

## Dispatch Entry

`FatFsdFlushBuffers` is the FSD dispatch wrapper. It enters the filesystem, establishes top-level IRP state, creates an IRP context with `CanFsdWait`, calls `FatCommonFlushBuffers`, and handles exceptions through the FastFAT exception path.

## Common Flush Flow

`FatCommonFlushBuffers` decodes the `FILE_OBJECT` with `FatDecodeFileObject`.

Because `CcFlushCache` is synchronous, non-wait-capable requests are posted to the FSP with `FatFsdPostRequest`.

Open-type behavior:

- `VirtualVolumeFile`, `EaFile`, `DirectoryFile`: no-op flush.
- `UserFileOpen`: acquires the FCB exclusive, verifies it, flushes file data, updates the file dirent from the FCB, tracks whether FAT flushing is required, flushes parent DCB chain, optionally flushes the FAT, and sets write-through state.
- `UserDirectoryOpen`: non-root directories are no-op; root directory falls through to volume flush.
- `UserVolumeOpen`: acquires VCB exclusive and flushes the volume.

On Windows 8+, disk flush accounting charges the originating user thread or current thread.

After filesystem work completes normally, the IRP is copied to the next stack location and sent to the target device object unless Windows 8+ minor-function rules skip it for data-only/no-sync variants. `FatFlushCompletionRoutine` merges lower-driver status with the filesystem flush status and treats unsupported device flush as non-fatal.

## File Flush

`FatFlushFile` calls `CcFlushCache` for the FCB section object pointers. If the FCB was not deleted during the flush, it acquires and releases `PagingIoResource` to serialize with the lazy writer and ensure cached I/O completion. If `FlushType == FlushAndInvalidate`, it marks the FCB condition bad while holding paging I/O synchronization.

## Directory Tree Flush

`FatFlushDirectory` flushes a DCB subtree in two passes while the VCB is exclusive:

1. File pass:
   - Walks top-down.
   - For regular files other than the EA FCB and deleted files, acquires FCB exclusive.
   - Verifies FCB and skips bad ones.
   - If `FCB_STATE_TRUNCATE_ON_CLOSE` is set, truncates allocation to file size.
   - Reads the dirent, corrects `Dirent->FileSize` from FCB size when needed, unpins before flushing, then flushes the file.
   - Handles expected filesystem exceptions and continues flushing as much of the tree as possible.

2. Directory pass:
   - Flushes DCB/root DCB entries after files so file sizes and timestamps reach disk first.
   - Verifies each directory FCB and flushes good ones.

It temporarily forces `IRP_CONTEXT_FLAG_WRITE_THROUGH` and `IRP_CONTEXT_FLAG_WAIT` when absent, then restores them. It finally attempts `FatUnpinRepinnedBcbs`, capturing exceptions into the return status.

## FAT Flush

`FatFlushFat` flushes the volume FAT area.

Behavior:

- Returns success immediately for write-protected volumes.
- Verifies the VCB and returns `STATUS_FILE_INVALID` if not good.
- For FAT16/FAT32, walks the FAT page by page and pins only if a BCB exists (`PIN_IF_BCB`), avoiding reading the entire FAT just to flush clean ranges.
- For FAT12, pins the whole FAT because the FAT is small and 12-bit entry packing is less page-friendly.
- Marks pinned data dirty, repins, unpins, and unpins repinned BCBs with write-through.
- Captures expected FAT exceptions and continues where possible for page-walk mode.

## Volume Flush

`FatFlushVolume` skips write-protected volumes, then:

- Flushes all files and directories via `FatFlushDirectory`.
- Flushes the FAT via `FatFlushFat`.
- Unlocks removable media with `FatToggleMediaEjectDisable` if the volume is removable and not a boot/paging volume.

`FatCommonFlushBuffers` additionally handles clean-volume state after a volume flush: it cancels pending clean timers/DPCs, marks the volume clean when it was not mounted dirty, clears `VCB_STATE_FLAG_VOLUME_DIRTY`, and unlocks removable media.

## Target Device Flush Hijacking

`FatHijackIrpAndFlushDevice` is used when FastFAT needs to force a device flush but does not have a flush IRP.

It:

- Copies the current IRP stack to the next stack location.
- Changes the major function to `IRP_MJ_FLUSH_BUFFERS`.
- Installs `FatHijackCompletionRoutine`, which signals an event and returns `STATUS_MORE_PROCESSING_REQUIRED`.
- Calls the target device and waits if pending.
- Normalizes `STATUS_INVALID_DEVICE_REQUEST` to success.
- Clears the original IRP status/information before returning.

This helper is used by range-specific flush helpers below.

## Range-Specific Flush Helpers

`FatFlushFatEntries` flushes the FAT page/range containing a cluster run.

- Computes the byte offset from reserved FAT bytes.
- Accounts for FAT12 packed entries, FAT16 entries, and FAT32 entries.
- Calls `CcFlushCache` on the VCB section object pointers.
- Sends a hijacked target-device flush if cache flush succeeds.
- Raises normalized status on failure.

`FatFlushDirentForFile` flushes the page containing a file's dirent in its parent directory.

- Uses `Fcb->DirentOffsetWithinDirectory`.
- Flushes the parent DCB section object pointers for one `DIRENT`.
- Sends a hijacked target-device flush on success.
- Raises normalized status on failure.

## Completion Routines

`FatFlushCompletionRoutine` preserves pending state, treats lower-driver success or unsupported flush as allowing the original filesystem status to stand, and returns `STATUS_SUCCESS`.

`FatHijackCompletionRoutine` signals the waiting event and returns `STATUS_MORE_PROCESSING_REQUIRED` so the hijacked IRP is not completed normally by the lower stack.

## Key Dependencies

- File object classification: `FatDecodeFileObject`.
- Metadata update: `FatUpdateDirentFromFcb`, `FatTruncateFileAllocation`.
- Cache Manager: `CcFlushCache`, `CcPinRead`, `CcSetDirtyPinnedData`, `CcRepinBcb`, `CcUnpinRepinnedBcb`.
- Device stack: `IoCopyCurrentIrpStackLocationToNext`, `IoSetCompletionRoutine`, `IoCallDriver`.
- Volume state: `FatMarkVolume`, clean-volume timer/DPC, removable-media eject disable.
- Verification and exception normalization: `FatVerifyFcb`, `FatVerifyVcb`, `FatExceptionFilter`, `FatNormalizeAndRaiseStatus`.

## Implementation Notes

The file prioritizes durability ordering: user-file flushes push file data, then dirent updates, parent directories, FAT metadata, and finally lower device flushes. Directory subtree flushing writes files before directories so size and timestamp metadata is coherent. FAT flushing avoids unnecessary FAT32 reads by relying on dirty BCB presence. Unsupported lower-device flush is normalized to success, matching the Windows storage-stack convention that some devices do not implement explicit flush.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/flush.c -->