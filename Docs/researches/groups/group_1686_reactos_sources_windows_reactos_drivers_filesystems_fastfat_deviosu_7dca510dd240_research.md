# Group Research: group_1686_reactos_sources_windows_reactos_drivers_filesystems_fastfat_deviosu_7dca510dd240

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/deviosup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/deviosup.c

## Purpose

`deviosup.c` is the low-level device I/O support layer for ReactOS fastfat. It translates FAT file byte ranges into disk logical byte offsets, builds IRPs/associated IRPs and MDLs, sends read/write requests to the lower storage stack, waits or completes asynchronously, and handles user-buffer locking/mapping plus internal device-control requests.

The file sits below read/write dispatch logic and above the target disk device. Its central responsibility is preserving Windows fastfat semantics around paging I/O, noncached I/O, synchronous versus asynchronous completion, verify handling, dirty-volume escalation on paging-file media errors, and completion-time buffer zeroing.

## Main Entry Points

- `FatPagingFileIo` handles paging-file I/O without ordinary completion processing. It maps VBO runs through the file Mcb, sends a single IRP directly when possible, otherwise splits across runs using associated IRPs or the master IRP with a reserve MDL fallback.
- `FatNonCachedIo` is the general noncached read/write path. It locks the caller buffer, optionally prepares completion-time zeroing for unreadable trailing bytes, maps the file allocation with `FatLookupFileAllocation`, and dispatches either `FatSingleAsync` or `FatMultipleAsync`.
- `FatNonCachedNonAlignedRead` handles non-sector-aligned noncached reads by using a one-sector cache-aligned pool buffer for unaligned head/tail sectors and delegating aligned middle ranges back to `FatNonCachedIo`.
- `FatMultipleAsync` builds associated IRPs, partial MDLs, stack locations, completion routines, and accounting for multiple noncontiguous disk runs.
- `FatSingleAsync` reuses the caller IRP for a single contiguous disk run.
- `FatSingleNonAlignedSync` temporarily replaces the IRP MDL with an MDL over a nonpaged staging buffer for synchronous sector reads.
- `FatWaitSync` waits on the `FatIoContext` sync event set by completion routines.
- `FatLockUserBuffer`, `FatMapUserBuffer`, and `FatBufferUserBuffer` provide FAT’s explicit user-buffer management because the filesystem does not rely on direct I/O setup from the I/O manager.
- `FatToggleMediaEjectDisable` and `FatPerformDevIoCtrl` build and submit internal device-control IRPs.
- `FatBuildZeroMdl` creates an MDL that represents a repeated zero page for efficient zero writes or zero-fill style operations.

## I/O Flow

The common pattern is: caller prepares a `FAT_IO_CONTEXT`, this file locks/maps the buffer, converts VBO to LBO, chooses single or multiple request dispatch, installs a completion routine, sends to `Vcb->TargetDeviceObject`, then either waits or returns pending.

`FatNonCachedIo` first validates that file allocation exists. Missing allocation after the upper layer expected allocation is treated as corruption via `FatPopUpFileCorrupt` and `STATUS_FILE_CORRUPT_ERROR`. For single runs it increments noncached stats and calls `FatSingleAsync`. For multiple runs it builds an `IO_RUN` array, initializes the master IRP status to success/full byte count, then calls `FatMultipleAsync`.

`FatMultipleAsync` does all fallible allocation before issuing any driver requests. If associated IRP/MDL allocation fails, it unwinds only the IRPs built so far. Once it starts calling the lower driver, an unexpected raise is considered unrecoverable and bugchecks.

Paging-file I/O has a stricter path. `FatPagingFileIo` asserts `FCB_STATE_PAGING_FILE`, requires the Mcb lookup to succeed, bypasses volume verify with `SL_OVERRIDE_VERIFY_VOLUME`, and avoids normal completion ownership. For fragmented paging files it creates associated IRPs per run when possible, but can reuse the master IRP synchronously when associated IRP allocation or MDL allocation pressure forces use of `FatReserveMdl`.

## Completion Behavior

The completion routines divide into synchronous, asynchronous, paging-file, and special APC-level variants.

- `FatMultiSyncCompletionRoutine` copies error status to the master IRP, frees associated IRP MDL/IRP, decrements `Context->IrpCount`, performs any completion zeroing when the last run finishes, and signals the sync event.
- `FatMultiAsyncCompletionRoutine` also consolidates errors into the master IRP. On final completion it sets requested byte count on success, marks fast-read or modified flags for nonpaging I/O, decrements outstanding async write counters, releases captured resources, marks the master IRP pending, frees the context, and may repost `STATUS_VERIFY_REQUIRED` top-level requests.
- `FatSingleSyncCompletionRoutine` performs completion zeroing and signals the sync event.
- `FatSingleAsyncCompletionRoutine` mirrors the async multi-run finalization path for single-run I/O.
- `FatPagingFileCompletionRoutine` is invoked on paging-file error/cancel and copies error status to the master IRP if needed.
- `FatPagingFileCompletionRoutineCatch` handles the synchronous master-IRP reuse case, frees or returns the reserve MDL, restores the original MDL, and either signals the waiter or lets dirty-volume recovery work complete it.
- `FatSpecialSyncCompletionRoutine` is used for APC-level-compatible internal IRPs such as media-removal toggles; it copies status into a local sync context and signals without holding the caller to ordinary final IRP completion timing.

`FatDoCompletionZero` is a key helper macro: if `Context->ZeroMdl` is set and the I/O succeeded, it zeroes the mapped tail bytes and frees the MDL. This supports sector-aligned physical reads where only part of the final bytes are user-visible.

## State, Dependencies, and Side Effects

This file depends heavily on kernel I/O primitives (`IoCallDriver`, `IoMakeAssociatedIrp`, MDLs, IRP stack locations), cache/FSRTL helpers, FAT Mcb allocation lookup, `FAT_IO_CONTEXT`, VCB statistics, and global fastfat data such as `FatData`, `FatReserveMdl`, `FatReserveEvent`, `FatDiskAccountingEnabled`, and debug flags.

It updates per-processor filesystem statistics, optional Windows 8+ disk accounting counters, file-object flags (`FO_FILE_FAST_IO_READ`, `FO_FILE_MODIFIED`), outstanding async write counters/events, removable-media prevention state in `Vcb->VcbState`, and dirty-volume recovery state through queued work items on paging-file media errors.

## Correctness Notes and Risks

The highest-risk areas are MDL/IRP lifetime and completion ownership. Multi-run dispatch depends on exact associated IRP counts and on not allowing the I/O manager to complete the master IRP before FAT has reconciled state. The paging-file path is especially sensitive because it tries to continue under low-memory pressure using a global reserve MDL and may synchronously reuse the master IRP.

`STATUS_VERIFY_REQUIRED` handling is intentionally limited: only top-level nonrecursive async I/O is reposted because recursive I/O cannot safely perform volume verification. Paging-file I/O overrides verify entirely.

Media-error handling for paging files is best effort. `FatPagingFileErrorHandler` queues dirty/recover marking for non-total-device failures, but comments explicitly note no full forward-progress guarantee.

The file includes conditional Windows-version and `__REACTOS__` sections around disk accounting; those paths should be checked carefully when changing compile-time feature levels because some accounting variables are only declared outside ReactOS builds while accounting macros may compile away depending on `NTDDI_VERSION`.

## Research Coverage

Read completely. Covered declarations, paging-file I/O, noncached aligned and nonaligned paths, single/multiple dispatch, all completion routines, user-buffer helpers, media-removal/device-control helpers, and zero-MDL construction.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/deviosup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/dirctrl.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/dirctrl.c

## Purpose

`dirctrl.c` implements FAT directory-control IRP handling: `IRP_MN_QUERY_DIRECTORY` and `IRP_MN_NOTIFY_CHANGE_DIRECTORY`. It is the dispatch-facing layer that validates directory opens, manages query templates stored in the CCB, streams directory entries into the caller’s buffer in requested NT information formats, and registers directory change notifications with FSRTL.

## Main Entry Points

- `FatFsdDirectoryControl` is the FSD dispatch entry. It enters the filesystem, creates an IRP context with wait permission derived from the IRP, calls `FatCommonDirectoryControl`, and routes exceptions through `FatProcessException`.
- `FatCommonDirectoryControl` switches on the minor function and calls either `FatQueryDirectory` or `FatNotifyChangeDirectory`.
- `FatQueryDirectory` implements directory enumeration and wildcard matching.
- `FatGetDirTimes` converts FAT on-disk timestamp fields into NT `LARGE_INTEGER` timestamps for query output.
- `FatNotifyChangeDirectory` validates a directory open, acquires the DCB, ensures the full name is available, and calls `FsRtlNotifyFullChangeDirectory`.

## Query Directory Flow

`FatQueryDirectory` accepts only `UserDirectoryOpen` file objects and rejects malformed Unicode filename lengths. It reads query parameters from the IRP stack: user buffer length, information class, file index, optional filename, restart flag, return-single-entry flag, and index-specified flag.

The query template is persisted in the CCB. On initial query or restart, the function acquires the DCB exclusively so it can update template state safely. Otherwise it acquires shared access for enumeration. If acquisition cannot wait, the request is posted to the FSP.

Template handling supports several cases:

- No filename, empty filename, `*`, or DOS `????????.???` sets `CCB_FLAG_MATCH_ALL`.
- Non-extended ASCII names are upcased manually into a combined Unicode/OEM allocation.
- Extended names use `RtlUpcaseUnicodeString` and `RtlUpcaseUnicodeStringToCountedOemString`.
- Names that cannot be represented or are not legal short OEM names set `CCB_FLAG_SKIP_SHORT_NAME_COMPARE`, forcing LFN-only matching.
- Wildcard templates are stored in `Ccb->OemQueryTemplate.Wild`; constant 8.3 templates are stored in `Ccb->OemQueryTemplate.Constant`.

The scan starting point is chosen in priority order: explicit file index, restart scan, or `Ccb->OffsetToStartSearchFrom`.

## Output Formats

The function supports:

- `FileDirectoryInformation`
- `FileFullDirectoryInformation`
- `FileIdFullDirectoryInformation`
- `FileNamesInformation`
- `FileBothDirectoryInformation`
- `FileIdBothDirectoryInformation`

It computes each format’s base length with `FIELD_OFFSET(..., FileName[0])`, then repeatedly calls `FatLocateDirent` to find the next matching entry. It fills packed variable-length records in the caller buffer using `NextEntryOffset` chaining and quad alignment.

For 8.3-only entries it converts the OEM short name to Unicode with `RtlOemToUnicodeN`. For entries with LFNs it copies the Unicode long name directly. `FileBothDirectoryInformation` and `FileIdBothDirectoryInformation` include the short name when a long name exists. `FileId*` classes use `FatGenerateFileIdFromDirentAndOffset`.

For full information classes, EA size is fetched with `FatGetEaLength`; EA corruption is deliberately ignored so enumeration continues with `EaSize = 0`.

Buffer semantics match NT directory-query rules: the first entry may be partially returned with `STATUS_BUFFER_OVERFLOW`, but later entries are omitted entirely if they do not fit and the call succeeds with entries already returned.

## Timestamp and Attribute Handling

`FatGetDirTimes` always sets last-write time from `Dirent->LastWriteTime`. In Chicago mode it also derives creation and last-access times. It has fast paths when creation/access fields match last-write data and falls back to `FatJanOne1980` when optional FAT timestamp fields are zero.

Directory query output sets:

- `EndOfFile` from `Dirent->FileSize`.
- `AllocationSize` rounded to cluster size for non-directories.
- `FileAttributes` from dirent attributes, or `FILE_ATTRIBUTE_NORMAL` when no attributes are set.
- `FileIndex` to the next VBO returned by `FatLocateDirent`, allowing continuation.

## Notify Change Flow

`FatNotifyChangeDirectory` forces wait behavior, validates `UserDirectoryOpen`, reads the completion filter and `SL_WATCH_TREE`, and acquires the DCB exclusively. It verifies the FCB, builds the full file name, rejects delete-pending directories, then calls `FsRtlNotifyFullChangeDirectory` with the volume notify list and sync object.

If FSRTL takes ownership of the IRP, the function completes only the IRP context (`FatNull` IRP) and returns `STATUS_PENDING`.

## State, Dependencies, and Side Effects

This file depends on `dirsup.c` for `FatLocateDirent`, 8.3 conversion, LFN extraction, file IDs, and EA lookup. It relies on CCB fields for persistent query templates and offsets, DCB resources for synchronization, `FatMapUserBuffer` from `deviosup.c` for safe buffer access, and FSRTL notify infrastructure for change notifications.

It mutates CCB query-template buffers and flags, `Ccb->OffsetToStartSearchFrom`, IRP status/information, and may post requests when locks cannot be acquired synchronously.

## Correctness Notes and Risks

The main correctness pressure is preserving query state across calls while allowing concurrent directory enumeration. Initial and restart queries must update CCB template state under exclusive DCB access; regular scans use shared access.

User buffer writes are wrapped in SEH because the request is not necessarily buffered by the I/O manager. On exception, the function clears `IoStatus.Information`, suppresses CCB offset updates, and completes with the exception status.

The switch statements intentionally fall through from richer directory information classes into common base-field population. Changes here must preserve that fall-through structure.

## Research Coverage

Read completely. Covered FSD/common dispatch, query-template construction, directory scan/output packing, timestamp conversion, file-ID handling, EA-size behavior, cleanup, and notify registration.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/dirctrl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/dirsup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/dirsup.c

## Purpose

`dirsup.c` is the FAT directory-entry support layer. It allocates, initializes, locates, constructs, deletes, rescans, defragments, and updates FAT dirents. It also implements long-file-name parsing/construction, volume-label lookup/construction, directory emptiness checks, tunnel-cache support, and delayed on-disk metadata updates from FCB/FileObject state.

This is the lower-level companion to `dirctrl.c`: `dirctrl.c` asks for matching entries, while `dirsup.c` understands how FAT short dirents, LFN dirent chains, free/deleted entries, and directory bitmaps are represented on disk.

## Core Helpers and Macros

- `FatConstructDot`, `FatConstructDotDot`, and `FatConstructEndDirent` initialize special directory entries.
- `FatReadDirent` pins the page containing a directory entry and advances within page-sized mapped directory windows.
- `FatComputeLfnChecksum` implements the standard FAT LFN checksum over the 11-byte short name.
- `FatRescanDirectory` rebuilds `UnusedDirentVbo`, `DeletedDirentHint`, and `FreeDirentBitmap`.
- `FatDefragDirectory` compacts used dirents and groups free/deleted/orphaned entries at the end of a small directory.

## Allocation and Initialization

`FatCreateNewDirent` allocates contiguous dirent slots inside a parent directory. It first uses `UnusedDirentVbo` if possible, otherwise searches `FreeDirentBitmap` from `DeletedDirentHint`. For non-FAT32 root directories with fragmented free space, it may call `FatDefragDirectory` if the root directory is small enough.

If no slot exists, it grows the directory by preparing a write beyond current allocation, except for fixed-size FAT12/FAT16 roots or directories capped at 64K entries. It verifies that selected entries are actually never-used or deleted before marking the bitmap bits allocated.

In Chicago mode, when allocating a single dirent, it checks the preceding dirent for an orphaned LFN and marks it deleted to avoid accidental future LFN/short-name pairing.

`FatInitializeDirectoryDirent` turns a newly created file dirent into a directory by allocating the first two entries and constructing `.` and `..`. For FAT32 it fills high cluster fields as well.

## Deletion and Tunneling

`FatTunnelFcbOrDcb` handles name tunneling before names disappear. Directory deletion removes the directory key from the volume tunnel cache. File deletion converts the short OEM name to Unicode, repairs case according to NT byte lowercase flags, and adds short name, exact-case long name, opened-by-shortname status, and creation time to `FsRtlAddToTunnelCache`.

`FatDeleteDirent` marks the LFN chain and short dirent deleted. It requires the VCB to be held exclusive and acquires the parent DCB resource to synchronize with enumerators. It can delete OS/2 EA data for non-FAT32 entries, clears corresponding free-dirent bitmap bits, optionally preserves file size and first cluster in the deleted short dirent for undelete tools, and updates `DeletedDirentHint`.

## Lookup and Matching

`FatLocateDirent` is the main directory scanner. It walks dirents from a supplied VBO and returns the first undeleted matching entry, its BCB, byte offset, optional DOS-name match flag, and optional long/original long filename.

Its matching logic handles:

- End of directory and EOF.
- Deleted entries.
- Volume-label entries, unless `CCB_FLAG_MATCH_VOLUME_ID` is set.
- Chicago LFN chains with ordinal validation, checksum validation, tail `0xffff` validation, and maximum LFN dirent count checks.
- Short-name wildcard matching through `FatIsNameInExpression`.
- Fast constant 8.3 matching by comparing the 11-byte dirent name in word-sized chunks.
- LFN wildcard or equality matching after upcasing the disk LFN.

Malformed LFN chains are usually ignored, but a zero ordinal marked as last long entry is treated as corruption. Valid LFN state is reset when deleted entries or invalid continuations are encountered.

`FatLfnDirentExists` creates a temporary CCB that skips short-name comparison and uses mixed-case query behavior to search for a specific long name.

`FatLocateSimpleOemDirent` wraps `FatLocateDirent` for exact simple OEM 8.3 lookups without LFN handling. `FatLocateVolumeLabel` scans the root directory for a nondeleted volume-label dirent and pins it writable.

## Direct Dirent Access and Directory State

`FatGetDirentFromFcbOrDcb` reads and pins the short dirent identified by an FCB/DCB’s stored offset. It tolerates failure during removable-media verification when `ReturnOnFailure` is true, otherwise missing dirents raise corruption.

`FatIsDirectoryEmpty` scans after `.` and `..` for normal directories, or from zero for root, and treats deleted entries and LFNs as ignorable. Any live non-LFN dirent means the directory is not empty.

`FatRescanDirectory` walks a directory to rebuild free/allocated bitmap state. In this codebase, set bits represent allocated dirents and clear bits represent free/deleted slots. It finds the first never-used VBO, the first deleted hint, marks allocated runs set, free runs clear, and clears all entries after the never-used marker.

## Construction and Metadata Updates

`FatConstructDirent` fills a short dirent from an OEM name, optional LFN, attributes, case flags, and creation-time input. It can zero and initialize timestamps, uses current system time when needed, supports tunneled creation time, and sets `FAT_DIRENT_NT_BYTE_8_LOWER_CASE` / `FAT_DIRENT_NT_BYTE_3_LOWER_CASE`.

When an LFN is supplied, it writes the LFN entries immediately before the short dirent, computes the checksum, splits the Unicode name into 13-character LFN fragments, sets the final fragment’s last-entry bit, null terminator, and `0xffff` tail padding, and fills the standard LFN attribute/type/checksum fields.

`FatConstructLabelDirent` builds a volume-label dirent: zeroed record, padded 11-byte label, current FAT write time, volume-id attribute, no EA, and zero file size.

`FatSetFileSizeInDirent` and `FatSetFileSizeInDirentNoRaise` write an FCB file size into its dirent, with the latter swallowing expected exceptions.

`FatUpdateDirentFromFcb` flushes deferred file-object effects into the on-disk dirent. It may set archive bit, update last-write time, update file size, and in Chicago mode update last-access date only if the previous access day differs from the current local day. It reports notify changes and marks the BCB dirty, avoiding marking the volume dirty for access-time-only updates.

## Defragmentation

`FatDefragDirectory` is used when a small non-FAT32 root directory has enough free entries but not enough contiguous entries. It requires exclusive VCB ownership, forces wait/write-through, acquires all child FCB resources, builds a large MCB describing used dirent ranges including valid LFNs, copies used and unused ranges into separate buffers, marks all unused entries as deleted, writes used entries first and unused entries after them, flushes repinned BCBs, rebuilds the free bitmap, and updates open child FCB dirent offsets.

If the flush or relocation lookup fails, it marks child FCBs bad because their on-disk positions may no longer be reliable.

## State, Dependencies, and Side Effects

This file mutates on-disk directory contents, DCB free-dirent allocation hints, free-dirent bitmaps, FCB dirent offsets, FCB timestamps, dirent FAT flags, tunnel cache entries, notify state, and dirty BCB/volume state.

It depends on FAT cache helpers (`FatReadDirectoryFile`, `FatPrepareWriteDirectoryFile`, `FatPinMappedData`, `FatUnpinBcb`, `FatSetDirtyBcb`), name conversion helpers, FSRTL tunnel/cache/name-expression/Mcb APIs, EA deletion, notification reporting, time conversion routines, and FCB/DCB resource ordering.

## Correctness Notes and Risks

The most delicate code is LFN parsing and directory compaction. LFN chains are order-sensitive and checksum-sensitive, and scanner state must be reset on deleted or malformed entries to avoid false pairings. `FatCreateNewDirent` proactively deletes orphaned LFN entries before single-slot allocation for the same reason.

The bitmap convention is easy to misread: allocated dirents are represented by set bits, while free/deleted dirents are clear. Allocation sets bits; deletion clears bits; rescans and defrag must preserve that convention.

`FatDefragDirectory` changes physical dirent offsets and therefore must either update every open child FCB or mark affected FCBs bad. It also deliberately limits operation to small directories to avoid cache-manager view complications.

Deletion requires strong synchronization: VCB exclusive plus parent DCB resource, because enumeration code can otherwise observe a partially deleted LFN chain.

## Research Coverage

Read completely. Covered dirent allocation, directory initialization, tunneling, deletion, LFN existence and lookup, volume-label lookup, direct dirent access, emptiness checks, dirent/label construction, size/time updates, checksum logic, full directory rescan, and root-directory defragmentation.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/dirsup.c -->