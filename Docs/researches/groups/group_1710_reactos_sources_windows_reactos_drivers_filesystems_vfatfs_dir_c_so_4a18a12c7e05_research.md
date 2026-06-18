# Group Research: ReactOS VFAT Directory, FAT, FCB, Info, Fast I/O, Flush

Scope: `Docs/research_subset_a.md`, source tree `sources/windows/reactos`.

This grouped report covers nine ReactOS VFAT filesystem driver files. The files implement directory enumeration and notifications, FAT/FATX directory entry parsing and mutation, FAT cluster-chain allocation and dirty/free-count metadata, FCB lifecycle/path lookup, file-information query/set operations, conservative Fast I/O callbacks, flushing, and the extended-attribute unsupported stub.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/dir.c -->
# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/dir.c

Purpose: Implements IRP_MJ_DIRECTORY_CONTROL for VFAT, including directory queries and directory change notifications. It converts DOS/FAT timestamps to NT system time, formats results for Windows directory information classes, and delegates actual entry scanning to the directory-entry layer.

Key routines:
- `FsdDosDateTimeToSystemTime` and `FsdSystemTimeToDosDateTime` translate FAT/FATX date/time fields using `DeviceExt->BaseDateYear` and local/system time conversion helpers.
- `VfatGetFileNamesInformation`, `VfatGetFileDirectoryInformation`, `VfatGetFileFullDirectoryInformation`, and `VfatGetFileBothInformation` populate caller buffers for `FileNamesInformation`, `FileDirectoryInformation`, `FileFullDirectoryInformation`, and `FileBothDirectoryInformation`.
- `DoQuery` handles query-directory state, search-pattern allocation, restart/index flags, shared/exclusive resource acquisition, repeated `FindFile` calls, output chaining through `NextEntryOffset`, and `IoStatus.Information`.
- `VfatNotifyChangeDirectory` registers notify IRPs through `FsRtlNotifyFullChangeDirectory`.
- `VfatDirectoryControl` dispatches `IRP_MN_QUERY_DIRECTORY` and `IRP_MN_NOTIFY_CHANGE_DIRECTORY`.

Implementation notes:
- FAT and FATX metadata are formatted separately. FATX has access time fields, while normal FAT uses access date with zero time.
- Directory entries report zero EOF/allocation size for directories in most query formats; file allocation is rounded to `BytesPerCluster`.
- Query state is kept in the CCB search pattern and entry index. A missing search pattern defaults to `*`.
- If resources cannot be acquired synchronously, the IRP user buffer is locked and the request is queued with `STATUS_PENDING`.
- The first output entry may return partial-name data with `STATUS_BUFFER_OVERFLOW`; subsequent entries require enough room for the complete variable-length entry.

Dependencies and interactions:
- Uses `FindFile`/`VfatGetNextDirEntry` from the directory-entry dispatch path, FCB `MainResource`, VCB `DirResource`, `VfatGetUserBuffer`, `VfatLockUserBuffer`, and FsRtl notification infrastructure.
- Directory-query output relies on `VFAT_DIRENTRY_CONTEXT` carrying both long and short Unicode names plus the raw FAT/FATX entry.

Notable limitations:
- FileIndex population is mostly left as comments except for the common `FILE_NAMES_INFORMATION`-compatible header path.
- The user-buffer probe is disabled behind `#if 0`, with a comment about SEH availability.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/direntry.c -->
# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/direntry.c

Purpose: Provides read-side directory-entry manipulation for FAT/FAT32/FATX. It extracts first cluster values, tests whether directories are empty, and iterates directory entries while reconstructing VFAT long names.

Key routines:
- `vfatDirEntryGetFirstCluster` returns a full first-cluster number, combining high/low words for FAT32 and using FATX layout for FATX volumes.
- `FATIsDirectoryEmpty` and `FATXIsDirectoryEmpty` scan cached directory data and treat only end/deleted entries, skipping `.` and `..` for normal FAT non-root directories.
- `FATGetNextDirEntry` maps directory file pages, handles starting in the middle of long-name slot runs, reconstructs LFN entries, verifies alias checksums against the 8.3 entry, and falls back to short names when needed.
- `FATXGetNextDirEntry` scans FATX entries, synthesizes `.` and `..` for non-root directories, and converts FATX OEM names to Unicode.

Implementation notes:
- Directory content is accessed through `vfatFCBInitializeCacheFromVolume` and cache manager calls (`CcMapData`, `CcUnpinData`) instead of direct disk reads.
- FAT long-name reconstruction copies 13 UTF-16 characters per slot, uses the `0x40` final-slot marker to terminate, validates slot index bounds, tracks a slot bitmap, and checks the short-name checksum.
- Deleted entries reset accumulated long-name state. End entries terminate iteration with `STATUS_NO_MORE_ENTRIES`.
- FATX has one fixed-size entry per file and uses filename length/deleted markers rather than VFAT LFN slot chains.

Dependencies and interactions:
- Called through the `VFAT_DISPATCH` table initialized in `dirwr.c`.
- Feeds `FindFile`, FCB creation, directory query formatting, delete checks, and path resolution.

Notable limitations and risks:
- Some corruption cases are logged and skipped or converted to no-more-entries rather than surfaced as hard corruption errors.
- The FAT directory-size traversal assumes page-sized mapping windows and carefully remaps at page boundaries; bugs here would affect all path lookup and enumeration.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/direntry.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/dirwr.c -->
# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/dirwr.c

Purpose: Implements write-side directory operations: directory cache setup, entry updates, add/delete/move/rename logic, free-slot discovery, and FAT/FATX dispatch table wiring.

Key routines:
- `vfatFCBInitializeCacheFromVolume` creates a stream file object for a directory FCB, attaches a CCB, initializes a cache map, grabs the FCB, and marks `FCB_CACHE_INITIALIZED`.
- `VfatUpdateEntry` pins the parent directory entry for an FCB and writes the current in-memory entry back to disk.
- `vfatRenameEntry` renames FATX entries in place but delegates normal FAT rename to `VfatMoveEntry` because long-name/short-name slot changes may be needed.
- `vfatFindDirSpace` scans for contiguous deleted/end slots, extends directories by one cluster when needed, and clears new/free separator entries.
- `FATAddEntry` creates FAT directory entries, generates DOS 8.3 aliases and VFAT LFN slots, allocates directory clusters for new directories, writes `.` and `..`, and constructs or updates the FCB.
- `FATXAddEntry` creates fixed FATX entries with up to 42 OEM bytes of filename data.
- `FATDelEntry` and `FATXDelEntry` mark entries deleted and, unless moving, free the file cluster chain.
- `VfatMoveEntry` deletes the old entry into a move context, re-adds under the target parent/name while preserving cluster/time/size, and flushes parent directory caches.

Implementation notes:
- Normal FAT long names use one or more LFN slots plus a short entry. Short-name generation uses `RtlIsNameLegalDOS8Dot3` and `RtlGenerate8dot3Name`, checking for collisions with `FindFile`.
- Creation timestamps are initialized from system time; moves preserve creation time, file size, and first cluster.
- Directory creation allocates a first cluster, initializes cache for the new directory, zeroes the cluster, and writes `.`/`..` entries with parent cluster values.
- FAT32 free-cluster count is refreshed after cluster allocation/free in relevant paths.
- FATX root/non-root indices differ because FATX iteration synthesizes `.`/`..`; add/update logic adjusts indices accordingly.

Dependencies and interactions:
- Calls FAT-chain functions (`NextCluster`, `GetNextCluster`, `WriteCluster`, `FAT32UpdateFreeClustersCount`), FCB update/create helpers, cache manager pin/dirty APIs, and notification-adjacent FCB metadata update paths.
- Exports `FatDispatch` and `FatXDispatch` with empty-dir, add, delete, and get-next-entry function pointers.

Notable limitations and risks:
- Several comments say status checks are FIXME, especially around cluster-chain writes and FCB creation/update in FATX add.
- FAT rename is implemented as move/delete/re-add, which is correct for LFN slot reshaping but makes crash consistency dependent on flush ordering.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/dirwr.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/ea.c -->
# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/ea.c

Purpose: Contains the extended-attribute set handler for the VFAT driver.

Key routine:
- `VfatSetExtendedAttributes` accepts a file object, EA buffer, and EA length, marks all parameters unused, and returns `STATUS_EAS_NOT_SUPPORTED`.

Implementation notes:
- There is no EA parsing, validation, storage, or query implementation here.
- This aligns with the rest of the VFAT code where EA query size is reported as zero and FAT12/FAT16 EA support is logged as not implemented.

Dependencies and interactions:
- Called by create/set paths when extended attributes are supplied.

Notable limitations:
- Extended attributes are explicitly unsupported for this driver.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/ea.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/fastio.c -->
# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/fastio.c

Purpose: Defines VFAT Fast I/O dispatch callbacks and cache-manager acquire/release callbacks.

Key routines:
- `VfatFastIoCheckIfPossible`, `VfatFastIoRead`, `VfatFastIoWrite`, file-lock callbacks, MDL callbacks, compressed I/O callbacks, device control, query-open, and network-open callbacks return `FALSE` or `STATUS_INVALID_DEVICE_REQUEST`, preventing those fast paths.
- `VfatFastIoQueryBasicInfo` and `VfatFastIoQueryStandardInfo` acquire the FCB shared resource and delegate to `VfatGetBasicInformation` / `VfatGetStandardInformation`.
- `VfatAcquireForCcFlush` and `VfatReleaseForCcFlush` acquire/release the FCB main resource for cache flushes.
- `VfatAcquireForLazyWrite` and `VfatReleaseFromLazyWrite` provide cache-manager lazy-writer synchronization around `MainResource`.
- `VfatInitFastIoRoutines` fills the `FAST_IO_DISPATCH` table.

Implementation notes:
- The driver deliberately disables data Fast I/O by returning `FALSE`, which forces normal IRP paths for reads, writes, locks, MDL I/O, compressed I/O, and query-open.
- Fast basic/standard information queries are supported only when the FCB can be locked without violating the caller's `Wait` parameter.
- Page-file FCBs bypass normal resource locking in the query-info fast paths.

Dependencies and interactions:
- Uses `VfatGetBasicInformation` and `VfatGetStandardInformation` from `finfo.c`.
- The cache manager uses lazy-write and flush acquire/release callbacks for synchronization with cached file data.

Notable limitations:
- Section create acquire/release callbacks are no-ops, and most Fast I/O operations are placeholders. This is safe but leaves performance on the IRP path.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/fastio.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/fat.c -->
# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/fat.c

Purpose: Implements File Allocation Table access, cluster allocation/free accounting, dirty-bit handling, and FAT32 FSINFO free-cluster updates.

Key routines:
- `FAT12GetNextCluster`, `FAT16GetNextCluster`, and `FAT32GetNextCluster` read the next cluster from the cached FAT file object, normalize end-of-chain values to `0xffffffff`, and detect zero/corrupt entries in FAT16/32 paths.
- `FAT12FindAndMarkAvailableCluster`, `FAT16FindAndMarkAvailableCluster`, and `FAT32FindAndMarkAvailableCluster` scan from `LastAvailableCluster`, wrap once to cluster 2, mark the found cluster EOF, and decrement cached free-cluster counts when valid.
- `FAT12CountAvailableClusters`, `FAT16CountAvailableClusters`, `FAT32CountAvailableClusters`, and `CountAvailableClusters` compute and cache free-cluster counts under `FatResource`.
- `FAT12WriteCluster`, `FAT16WriteCluster`, `FAT32WriteCluster`, and `WriteCluster` mutate FAT entries and update free-cluster accounting based on old/new values.
- `ClusterToSector` maps data cluster numbers to sectors.
- `GetNextCluster` and `GetNextClusterExtend` wrap FAT-specific get/extend operations with resource locking.
- `GetDirtyStatus`, `SetDirtyStatus`, `FAT16GetDirtyStatus`, `FAT32GetDirtyStatus`, `FAT16SetDirtyStatus`, and `FAT32SetDirtyStatus` read/write FAT16/FAT32 volume dirty bits in boot-sector reserved fields.
- `FAT32UpdateFreeClustersCount` writes the cached free-cluster count into the FAT32 FSINFO sector.

Implementation notes:
- `CACHEPAGESIZE` uses at least one page and may use a whole cluster when clusters exceed page size.
- FAT12 code maps/pins the full FAT because 12-bit entries can cross byte boundaries; FAT16/FAT32 operate in chunks.
- FAT32 preserves the high 4 reserved bits when writing cluster entries.
- Dirty-bit operations can optionally bypass cache manager via `VOLUME_IS_NOT_CACHED_WORK_AROUND_IT`, but the normal path pins the volume FCB cache.

Dependencies and interactions:
- Used by allocation-size changes, directory creation/deletion, move/delete cleanup, and volume metadata reporting.
- Protected by `DeviceExt->FatResource` wrappers for shared/exclusive access.

Notable limitations and risks:
- FAT12 `GetNextCluster` asserts on zero but does not mirror the FAT16/32 `STATUS_FILE_CORRUPT_ERROR` handling.
- Some callers ignore `WriteCluster` status, so FAT-chain mutation failures can be underreported in higher-level operations.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/fat.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/fcb.c -->
# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/fcb.c

Purpose: Manages VFAT file control blocks: allocation, destruction, path hashing, parent/child relationships, FCB cache lookup, root FCB creation, file-object attachment, directory searches, and path resolution.

Key routines:
- `vfatNameHash` computes case-insensitive hashes for Unicode path/name strings.
- `vfatSplitPathName` splits a full path into directory and file components.
- `vfatInitFcb`, `vfatNewFCB`, `vfatDestroyFCB`, and `vfatDestroyCCB` manage FCB/CCB memory, resources, file locks, names, and attributes pointers.
- `vfatGrabFCB` and `vfatReleaseFCB` maintain reference counts under `DirResource`, uninitialize cache maps when refcount drops to one, and recursively release parent FCBs when children are destroyed.
- `vfatAddFCBToTable`, `vfatDelFCBFromTable`, and `vfatGrabFCBFromTable` maintain the VCB hash table by full long path and, for normal FAT, short-name path.
- `vfatMakeFullName`, `vfatInitFCBFromDirEntry`, `vfatMakeFCBFromDirEntry`, `vfatUpdateFCB`, and `vfatSetFCBNewDirName` build/update FCB identity and metadata from directory entries.
- `vfatMakeRootFCB` and `vfatOpenRootFCB` create/cache the root FCB with FAT/FAT32/FATX-specific size and first-cluster state.
- `vfatAttachFCBToFileObject` attaches an FCB and fresh CCB to an opened file object.
- `vfatDirFindFile` scans a directory for long or short-name matches and creates an FCB for the found entry.
- `vfatGetFCBForFile` resolves absolute or parent-relative paths component by component, using the FCB hash table first and directory scans on misses.

Implementation notes:
- FCBs contain both full path strings and split `DirNameU`/`LongNameU`, plus `ShortNameU` where applicable.
- Directory FCB sizes are derived from root-directory sectors or by walking cluster chains.
- Parent-child relationships are tracked with `ParentListHead`/`ParentListEntry`; adding an FCB grabs its parent.
- Root FCB starts with refcount 2, initializes directory caching immediately, and is stored in `pVCB->RootFcb`.
- Path resolution normalizes casing/path spelling by replacing path components with the long names from cached or discovered FCBs.

Dependencies and interactions:
- Heavily used by create/open, directory enumeration, rename/move, cleanup/close, flush, and file-information paths.
- Depends on directory-entry scanning through `VfatGetNextDirEntry`, FAT-chain helpers for directory sizing, and cache initialization from `dirwr.c`.

Notable limitations and risks:
- `vfatInitFcb` bugchecks on path-buffer allocation failure rather than returning an error.
- Directory size calculation loops appear to call `NextCluster` with the first cluster rather than the current cluster in the shown implementation, which is worth reviewing against the expected helper signature.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/fcb.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/finfo.c -->
# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/finfo.c

Purpose: Implements IRP_MJ_QUERY_INFORMATION and IRP_MJ_SET_INFORMATION for VFAT files, including basic/standard/name/internal/network/EA/all information queries and position, disposition, allocation/EOF, basic metadata, and rename setters.

Key routines:
- `VfatGetStandardInformation`, `VfatGetBasicInformation`, `VfatGetNameInformation`, `VfatGetInternalInformation`, `VfatGetNetworkOpenInformation`, `VfatGetEaInformation`, and `VfatGetAllInformation` fill Windows file-information structures.
- `VfatSetPositionInformation` updates `FileObject->CurrentByteOffset`.
- `VfatSetBasicInformation` updates allowed attributes and FAT/FATX timestamp fields, writes the directory entry, and reports change notifications.
- `VfatSetDispositionInformation` marks/unmarks delete pending, rejecting read-only files, root, dot entries, mapped image sections, and non-empty directories.
- `vfatPrepareTargetForRename` opens/checks a rename target, enforces `ReplaceIfExists`, flushes/deletes replaceable targets, and rejects directories/read-only/open targets.
- `IsThereAChildOpened` and `VfatRenameChildFCB` protect directory renames with open descendants and update cached child paths after successful directory renames.
- `VfatSetRenameInformation` handles relative roots, fully qualified `\??\X:` names, target file objects, same-volume checks, in-place case-only rename, same-directory rename, cross-directory move, notification reporting, and child FCB path repair.
- `UpdateFileSize` synchronizes FCB sizes, on-disk file size fields, and cache-manager file sizes.
- `VfatSetAllocationSizeInformation` grows/shrinks allocation and EOF, allocates cluster chains, truncates/free chains, checks mapped-file truncation, updates FAT32 free counts, writes directory entries, and reports size changes.
- `VfatQueryInformation` and `VfatSetInformation` are the IRP entry points with resource acquisition/queueing behavior.

Implementation notes:
- Attribute setting masks to FAT-supported attributes and synthesizes `FILE_ATTRIBUTE_NORMAL` on query when no other basic attribute is set.
- FATX and FAT timestamp layouts are handled separately. Normal FAT access time stores only date.
- Delete disposition only marks pending; actual entry deletion is handled elsewhere during cleanup/close.
- Rename code distinguishes exact same-name success, case-only rename, replacement, and move across parent directories.
- Allocation growth from zero obtains a first cluster, then extends to the rounded target offset; truncation updates EOF/allocation first and then frees trailing clusters.

Dependencies and interactions:
- Calls directory-entry, FCB, FAT-chain, cache-manager, memory-manager, and notification helpers: `VfatUpdateEntry`, `VfatMoveEntry`, `vfatRenameEntry`, `VfatDelEntry`, `VfatIsDirectoryEmpty`, `OffsetToCluster`, `NextCluster`, `WriteCluster`, `MmCanFileBeTruncated`, `MmFlushImageSection`, `CcSetFileSizes`, and `vfatReportChange`.
- Fast I/O basic/standard query callbacks delegate into functions defined here.

Notable limitations and risks:
- `FileAlternateNameInformation` is not implemented, and most unsupported setters return `STATUS_NOT_SUPPORTED`.
- EA information always reports zero and logs missing FAT12/FAT16 support.
- The rename logic has assertions disabled via `NASSERTS_RENAME`, indicating historical fragility or unresolved reference-count edge cases.
- Some FAT-chain cleanup loops ignore or overwrite intermediate statuses, so disk-full or write failures may leave partially adjusted chains.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/finfo.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/flush.c -->
# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/flush.c

Purpose: Implements flush operations for individual files and whole VFAT volumes.

Key routines:
- `VfatFlushFile` flushes cache-manager data for an FCB, treats `STATUS_INVALID_PARAMETER` as success for possibly uninitialized caching, and writes dirty directory entries through `VfatUpdateEntry` under `DirResource`.
- `VfatFlushVolume` flushes all non-directory FCBs first, then directory FCBs, then the FAT file object, and finally sends `IRP_MJ_FLUSH_BUFFERS` to the underlying storage device.
- `VfatFlush` dispatches flush IRPs, rejecting the filesystem control device, and choosing volume flush versus single-file flush based on `FCB_IS_VOLUME`.

Implementation notes:
- Whole-volume flush iterates the VCB FCB list twice to flush file data before directory metadata.
- The FAT file object is flushed under `FatResource`.
- Storage devices that return `STATUS_INVALID_DEVICE_REQUEST` for flush are tolerated and treated as success.

Dependencies and interactions:
- Uses FCB list management from `fcb.c`, dirty-entry writing from `dirwr.c`, cache-manager flush APIs, and lower storage-device IRP dispatch.

Notable limitations:
- Comments note removable-media handling is incomplete; volume flushing does not stop early if media is removed.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/flush.c -->