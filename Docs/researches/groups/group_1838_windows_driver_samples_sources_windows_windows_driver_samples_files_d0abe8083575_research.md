# Group Research: group_1838_windows_driver_samples_sources_windows_windows_driver_samples_files_d0abe8083575

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/dirsup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/dirsup.c

## Scope And Role

`dirsup.c` implements active FAT directory-entry support for the FastFat sample filesystem. It owns allocation, deletion, lookup, construction, timestamp/size synchronization, long-file-name handling, volume-label lookup, free-dirent rescans, and small-directory defragmentation.

The file is in subset A through `sources/windows/windows-driver-samples`, and was read completely.

## Main Entry Points

- `FatCreateNewDirent`: allocates contiguous directory entries in a parent DCB.
- `FatInitializeDirectoryDirent`: creates initial `.` and `..` entries for a new directory.
- `FatTunnelFcbOrDcb`: stores disappearing names/timestamps in the tunnel cache.
- `FatDeleteDirent`: marks an FCB/DCB dirent run deleted and optionally deletes EAs.
- `FatLfnDirentExists`: probes for an existing long filename.
- `FatLocateDirent`: central directory scan and matching routine for short names, LFNs, wildcards, and volume-label matches.
- `FatLocateSimpleOemDirent`: simpler 8.3 lookup wrapper.
- `FatLocateVolumeLabel`: scans the root directory for the volume-label dirent.
- `FatGetDirentFromFcbOrDcb`: pins the on-disk dirent associated with an FCB/DCB.
- `FatIsDirectoryEmpty`: tests whether only exempt entries remain.
- `FatConstructDirent`: fills short dirent fields and optional LFN prefix entries.
- `FatConstructLabelDirent`: fills a volume-label dirent.
- `FatSetFileSizeInDirent` / `FatSetFileSizeInDirentNoRaise`: writes FCB file size back to disk dirent.
- `FatUpdateDirentFromFcb`: flushes handle-derived archive, size, write-time, and access-time changes to the dirent and reports notifications.
- `FatComputeLfnChecksum`: computes the VFAT LFN checksum over the 11-byte short name.
- `FatRescanDirectory`: rebuilds DCB dirent hints and allocation bitmap state.
- `FatDefragDirectory`: compacts used dirents before free/deleted dirents for small directories.

## Important Local Helpers And Macros

- `FatConstructDot`, `FatConstructDotDot`, and `FatConstructEndDirent` build special directory entries. FAT32 high-cluster fields are always assigned but remain zero for non-FAT32.
- `FatReadDirent` pages through a directory by VBO, unpinning old BCBs and reading the next page when crossing a page boundary.
- The disabled `FatIsLfnPairValid` block documents a stricter LFN/short-name pairing check that was not compiled because Win95 could create short names without `~`.

## Directory Allocation Model

`FatCreateNewDirent` uses `ParentDirectory->Specific.Dcb.UnusedDirentVbo`, `DeletedDirentHint`, and `FreeDirentBitmap` as its allocator state. Clear bits represent free/deleted entries and set bits represent allocated entries, matching use of `RtlFindClearBits` for allocation and `RtlSetBits` after allocation.

The allocation path:

1. Rescans the directory if hints are uninitialized or forced by `RescanDir`.
2. Uses `UnusedDirentVbo` when never-used space is still inside current allocation.
3. Otherwise searches the free bitmap from `DeletedDirentHint`.
4. For non-FAT32 fixed root directories, may call `FatDefragDirectory` when fragmentation prevents satisfying a contiguous request.
5. If no free run exists, expands non-root/FAT32-capable directories by touching a byte through `FatPrepareWriteDirectoryFile`.
6. Rejects non-FAT32 root growth and also caps FAT32 directories at 64K entries.
7. In Chicago/VFAT mode, deletes an immediately preceding orphan LFN when allocating a single short dirent to reduce accidental LFN pairing.
8. Verifies selected dirents are actually `NEVER_USED` or `DELETED`, then marks bitmap bits allocated and saves updated hints.

## Directory Lookup And LFN Semantics

`FatLocateDirent` is the file’s core scanner. It requires the caller to hold the parent directory resource or VCB resource because deletion can rewrite LFN runs concurrently. It walks dirents from a rounded VBO, stopping on match, EOF, end-of-directory marker, or no match.

Short-name matching supports wildcard and constant 8.3 paths through CCB templates. Volume-label entries are skipped unless `CCB_FLAG_MATCH_VOLUME_ID` is set. If requested, VFAT LFN entries are reconstructed from reverse ordinal records, requiring ordinal continuity, matching checksum, `MustBeZero == 0`, valid tail bytes, and adjacency to the following short dirent. The final reconstructed LFN is upcased only when needed and matched with `FsRtlIsNameInExpression` or `FsRtlAreNamesEqual`.

`FatLfnDirentExists` builds a CCB that skips short-name comparison and does a case-insensitive LFN search. `FatLocateSimpleOemDirent` converts an OEM name to 8.3 and delegates to `FatLocateDirent`.

## Mutation, Synchronization, And Cache Use

The file uses BCB pinning and dirtying throughout, with careful unpin in `finally` blocks. Directory deletion asserts the VCB is held exclusive, acquires the parent DCB resource exclusive to synchronize with enumeration, then marks each LFN and short dirent in the run deleted. If `DeleteEa` is true and the filesystem is not FAT32, it attempts `FatDeleteEa` but swallows expected FAT exceptions. It clears free-bitmap bits for the deleted run and updates `DeletedDirentHint`.

`FatUpdateDirentFromFcb` skips bad FCBs, the root directory, and write-protected volumes. It derives updates from `FileObject->Flags` and CCB user-set flags, sets the archive bit on modification, updates last-write time unless user-set, updates file size when `FO_FILE_SIZE_CHANGED`, and updates last-access date only once per local day in Chicago mode. It reports notify filters and avoids marking the volume dirty for access-time-only updates.

## Directory Defragmentation

`FatDefragDirectory` is guarded by an exclusive VCB assertion and only handles directories up to `0x40000` bytes. It forces wait/write-through behavior, acquires every open child FCB exclusively, enumerates valid entries with `FatLocateDirent`, records used runs in a large MCB, copies used and unused bytes into pool buffers, marks unused dirents deleted, writes used dirents first and deleted/free dirents after them, updates the free bitmap, flushes repinned BCBs, then relocates open child FCB dirent offsets by short-name lookup. If relocation or flushing fails, affected children are marked bad.

## Integration Points

This file integrates with:

- Cache manager and mapped data helpers: `FatReadDirectoryFile`, `FatPrepareWriteDirectoryFile`, `FatPinMappedData`, `FatSetDirtyBcb`, `FatUnpinBcb`, `FatUnpinRepinnedBcbs`.
- FCB/DCB/VCB locking and conditions.
- Name conversion/matching helpers: `FatStringTo8dot3`, `Fat8dot3ToString`, `FatIsNameInExpression`, `FsRtlAreNamesEqual`, `FsRtlIsNameInExpression`.
- Tunnel cache: `FsRtlAddToTunnelCache`, `FsRtlDeleteKeyFromTunnelCache`.
- EA support through `FatDeleteEa`.
- Notify support through `FatNotifyReportChange`.
- FAT time conversion helpers.

## Risks And Test Signals

The riskiest areas are LFN reconstruction/deletion races, bitmap hint correctness, small-root defragmentation, and timestamp/dirty-volume side effects. Tests should cover fragmented fixed root directories, orphaned LFN cleanup, deletion during enumeration, volume-label lookup/update, FAT32 versus FAT12/16 root behavior, 64K-entry cap enforcement, case-preserving short-name tunneling, and last-access updates across local-day boundaries.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/dirsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/dumpsup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/dumpsup.c

## Scope And Role

`dumpsup.c` implements debug-only data-structure dump routines for FastFat. All code is compiled only under `FASTFATDBG`; there is no runtime behavior in non-debug builds.

The file is in subset A through `sources/windows/windows-driver-samples`, and was read completely.

## Main Entry Points

- `FatDump`: dispatches by `NodeType(Ptr)` to the right dump routine.
- `FatDumpDataHeader`: dumps global `FatData` and walks the VCB queue.
- `FatDumpVcb`: dumps a volume control block and then dumps its root DCB.
- `FatDumpFcb`: dumps file/directory/root DCB fields and recursively walks child FCB/DCB links for directories.
- `FatDumpCcb`: dumps CCB query-template and enumeration-offset fields.

## Formatting Helpers

The file defines local macros for debug output:

- `DumpNewLine` resets an 80-column style output cursor.
- `DumpLabel` formats field labels by trimming to the last dotted component.
- `DumpField` prints pointer/integer-style fields using `%p`.
- `DumpListEntry` prints `Flink` and `Blink`.
- `DumpName` copies fixed-width character fields to a local buffer.
- `TestForNull` rejects null pointers before dereferencing.

`FatDumpCurrentColumn` tracks output width for layout.

## Data Traversal

`FatDump` recognizes `FAT_NTC_DATA_HEADER`, `FAT_NTC_VCB`, `FAT_NTC_FCB`, `FAT_NTC_DCB`, `FAT_NTC_ROOT_DCB`, and `FAT_NTC_CCB`. Unknown node types print the raw node type code.

`FatDumpDataHeader` starts from global `FatData`, dumps core driver/global fields, then iterates `FatData.VcbQueue` and calls `FatDumpVcb` for each volume. `FatDumpVcb` prints volume allocation/cache/state fields and then dumps `RootDcb`. `FatDumpFcb` prints common FCB fields, name buffers, section object pointers, and either directory-specific child queues or file size. For DCB/root DCB nodes, it recursively dumps each child from `Specific.Dcb.ParentDcbQueue`.

## Integration Points

This file depends on FastFat internal structures and debug macros from `FatProcs.h`, including `PFAT_DATA`, `PVCB`, `PFCB`, `PCCB`, node type codes, list layout, and `DbgPrint`.

## Risks And Test Signals

The code is debug-only and intentionally walks internal linked lists without defensive consistency checks beyond null input. It can recurse deeply through directory trees and assumes structure layouts match the dump fields. Relevant verification is compile-time debug-build coverage plus manual debugger invocation on representative VCB/FCB/CCB objects.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/dumpsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/ea.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/ea.c

## Scope And Role

`ea.c` is the FastFat extended-attribute dispatch file. In this sample version, the live EA query and set common routines deliberately complete with `STATUS_INVALID_DEVICE_REQUEST`; most historical FAT EA implementation logic is retained under `#if 0`.

The file is in subset A through `sources/windows/windows-driver-samples`, and was read completely.

## Live Entry Points

- `FatFsdQueryEa`: FSD dispatch wrapper for `IRP_MJ_QUERY_EA`.
- `FatFsdSetEa`: FSD dispatch wrapper for `IRP_MJ_SET_EA`.
- `FatCommonQueryEa`: live implementation completes the IRP with `STATUS_INVALID_DEVICE_REQUEST` and returns that status.
- `FatCommonSetEa`: live implementation completes the IRP with `STATUS_INVALID_DEVICE_REQUEST` and returns that status.

The dispatch wrappers enter the filesystem with `FsRtlEnterFileSystem`, establish top-level IRP state with `FatIsIrpTopLevel`, create an IRP context using waitability from `CanFsdWait`, call the common routine, process FastFat exceptions, clear top-level IRP state when appropriate, and exit the filesystem.

## Disabled Historical Query Path

The disabled `FatCommonQueryEa` block shows the intended full algorithm:

1. Decode the file object and allow only user file/directory opens, excluding the root DCB.
2. Reject FAT32 with `STATUS_EAS_NOT_SUPPORTED`.
3. Acquire the FCB shared, map the user buffer, verify the FCB, and read the file’s dirent.
4. Check EA modification count consistency against the CCB for resumable enumeration.
5. If the dirent EA handle is zero, treat the file as having no EAs.
6. Otherwise get the volume EA file, validate that an EA database exists, read the EA set, and derive packed-EA range and length.
7. Clear the user output buffer and choose one of three helper paths: user EA-name list, index-specified scan, or simple scan.
8. Release FCBs, unpin BCBs and EA ranges, then complete the IRP.

## Disabled Historical Set Path

The disabled `FatCommonSetEa` block shows a wholesale replacement model:

1. Decode the file object, reject invalid opens/root DCB and FAT32.
2. Buffer and validate the caller’s full-EA list with `IoCheckEaBufferValidity`.
3. Require a waitable context, set `FO_FILE_MODIFIED`, and acquire VCB/FCB resources; write-through mode also acquires parent/root DCBs to preserve lock order.
4. Read the existing EA handle from the object dirent.
5. If previous EAs exist, read the EA file and current EA set.
6. Allocate a cluster-rounded EA set buffer, copy previous packed EAs or initialize a new owner-name header.
7. For each input `FILE_FULL_EA_INFORMATION`, validate name/flags, delete any existing packed EA with the same name, and append non-empty replacements.
8. If packed EAs remain, allocate a new EA set in the EA file, copy header/list data, dirty and flush the EA range.
9. Delete the previous EA set if one existed.
10. Store the new EA handle in the object dirent, dirty the dirent, notify `FILE_NOTIFY_CHANGE_EA`, and release all resources.

## Disabled Helper Routines

All helper implementations are inside `#if 0`:

- `FatQueryEaUserEaList`: handles explicit EA-name lists, validates names, skips duplicate requested names, returns dummy empty EAs for missing names, copies found packed EAs to full-EA records, and reports overflow status.
- `FatQueryEaIndexSpecified`: converts a 1-based EA index into an offset and delegates to simple scan, distinguishing nonexistent entries from end-of-list.
- `FatQueryEaSimpleScan`: copies packed EAs into caller full-EA records from a starting offset, updating `Ccb->OffsetOfNextEaToReturn`.
- `FatIsDuplicateEaName`: scans previous request entries and compares upcased EA names.

Because the entire block is disabled, these helpers are not compiled despite their prototypes.

## Integration Points

The live code integrates only with dispatch, IRP-context, top-level IRP, exception, and request-completion helpers. The disabled code references broader FastFat EA infrastructure such as `FatGetEaFile`, `FatReadEaSet`, `FatAddEaSet`, `FatDeleteEaSet`, packed EA manipulation helpers, EA range pinning/dirtying, and CCB EA enumeration state.

## Risks And Test Signals

The effective behavior is simple: EA query/set should return `STATUS_INVALID_DEVICE_REQUEST`. Regression tests should assert both FSD wrappers complete that way and preserve normal FastFat exception/top-level IRP cleanup behavior. If the disabled EA implementation were ever re-enabled, the high-risk areas would be user-buffer probing, packed/full EA size alignment, resumable enumeration offsets, EA database corruption handling, lock ordering across VCB/FCB/root/parent/EA FCB, and consistency between dirent EA handles and EA file contents.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/ea.c -->