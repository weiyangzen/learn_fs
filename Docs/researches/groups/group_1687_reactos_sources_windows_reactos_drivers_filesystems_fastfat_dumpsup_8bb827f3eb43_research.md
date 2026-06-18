# Group Research: group_1687_reactos_sources_windows_reactos_drivers_filesystems_fastfat_dumpsup_8bb827f3eb43

Scope confirmed against `Docs/research_subset_a.md`. All six listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/dumpsup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/dumpsup.c

## Purpose

`dumpsup.c` is a `FASTFATDBG`-only debugging support module for dumping in-memory FastFAT structures through `DbgPrint`. It is compiled only when `FASTFATDBG` is defined and has no retail/runtime filesystem behavior.

## Main Contents

- `FatDump(PVOID Ptr)` dispatches by `NodeType(Ptr)` to the right dump routine:
  - `FAT_NTC_DATA_HEADER` -> `FatDumpDataHeader`
  - `FAT_NTC_VCB` -> `FatDumpVcb`
  - `FAT_NTC_FCB`, `FAT_NTC_DCB`, `FAT_NTC_ROOT_DCB` -> `FatDumpFcb`
  - `FAT_NTC_CCB` -> `FatDumpCcb`
- `FatDumpDataHeader()` prints global `FatData` fields and walks `FatData.VcbQueue`, dumping each `VCB`.
- `FatDumpVcb(PVCB Ptr)` prints volume state, allocation support fields, section object pointers, dirty/free cluster tracking, and then dumps the root DCB.
- `FatDumpFcb(PFCB Ptr)` prints file/directory control block state, names, allocation/file size fields, section object pointers, and recursively dumps child FCBs for DCB/root DCB nodes.
- `FatDumpCcb(PCCB Ptr)` prints CCB node metadata, query template text, and search offset.

## Formatting Helpers

The file defines local dump macros:

- `DumpNewLine` resets the current dump column.
- `DumpLabel` prints a shortened field label, preferring text after the last dot in nested field names.
- `DumpField` prints pointer/integer-like fields with fixed spacing.
- `DumpListEntry` prints `Flink` and `Blink`.
- `DumpName` copies a fixed-width character buffer into a local string for output.
- `TestForNull` rejects null pointers before dereferencing.

## Notable Details

- Recursive dumping follows the live VCB/FCB tree, so corrupted list links could make debug dumps recurse or walk bad memory.
- `DumpField` uses `%p` for all fields, including non-pointer scalar fields. This is acceptable for debug output but not semantically typed.
- `DumpName` copies fixed-width data without checking the actual string length. It is meant for diagnostic snapshots, not safe user-visible formatting.
- There is no synchronization. Callers are expected to use it only in debugging contexts where concurrent mutation is understood.

## Integration

This module is tied to `DebugDump` in `fatdata.h`, which calls `FatDump(PTR)` when debug tracing is enabled and then asserts. It provides introspection over core FastFAT structures defined elsewhere in the driver.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/dumpsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/ea.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/ea.c

## Purpose

`ea.c` implements the dispatch-facing Extended Attribute operations for FastFAT: `IRP_MJ_QUERY_EA` and `IRP_MJ_SET_EA`. In this ReactOS source snapshot, the real query/set implementations are compiled out with `#if 0`; the active common routines immediately complete requests with `STATUS_INVALID_DEVICE_REQUEST`.

## Active Runtime Behavior

- `FatFsdQueryEa(...)`
  - Enters filesystem context.
  - Marks top-level IRP if applicable.
  - Creates an IRP context.
  - Calls `FatCommonQueryEa`.
  - Uses `FatExceptionFilter` and `FatProcessException` for structured exception handling.
- `FatFsdSetEa(...)`
  - Same dispatch pattern as query.
  - Calls `FatCommonSetEa`.
- `FatCommonQueryEa(...)`
  - Active code calls `FatCompleteRequest(..., STATUS_INVALID_DEVICE_REQUEST)`.
  - Returns `STATUS_INVALID_DEVICE_REQUEST`.
- `FatCommonSetEa(...)`
  - Active code calls `FatCompleteRequest(..., STATUS_INVALID_DEVICE_REQUEST)`.
  - Returns `STATUS_INVALID_DEVICE_REQUEST`.

So although the FSD entry points exist, EA query/set are effectively unsupported at this layer in the compiled code.

## Disabled Query Implementation

The disabled `FatCommonQueryEa` body documents the intended design:

- Accepts only `UserFileOpen` and `UserDirectoryOpen`; rejects root DCB.
- Rejects FAT32 with `STATUS_EAS_NOT_SUPPORTED`.
- Requires a waitable context or posts the request.
- Acquires the target FCB shared.
- Reads the file dirent to obtain `Dirent->ExtendedAttributes`, the EA handle.
- If handle is zero, returns from an empty EA set.
- Otherwise opens/locks the EA data file using `FatGetEaFile`, reads the EA set through `FatReadEaSet`, and exposes packed EAs as full EA records.
- Supports three query modes:
  - user-supplied EA name list via `FatQueryEaUserEaList`
  - index-specified scan via `FatQueryEaIndexSpecified`
  - sequential scan via `FatQueryEaSimpleScan`
- Tracks resume state with `Ccb->OffsetOfNextEaToReturn`.
- Uses `Fcb->EaModificationCount` and `Ccb->EaModificationCount` to detect changes during enumeration.

## Disabled Set Implementation

The disabled `FatCommonSetEa` body documents replacement-style EA updates:

- Validates open type and rejects FAT32.
- Buffers and validates user EA input with `IoCheckEaBufferValidity`.
- Requires waitable context.
- Acquires VCB/FCB and, for write-through, parent/root DCBs in a prescribed order.
- Reads existing packed EA data if present.
- For each full EA:
  - validates EA name with `FatIsEaNameValid`
  - rejects unsupported flags
  - deletes any existing same-name packed EA
  - appends a new packed EA if the value length is nonzero
- Adds a new EA set with `FatAddEaSet` if packed EAs remain.
- Deletes the previous EA set with `FatDeleteEaSet`.
- Updates the owning dirent’s `ExtendedAttributes` handle.
- Marks the dirent dirty and emits `FILE_NOTIFY_CHANGE_EA`.

## Disabled Helper Algorithms

- `FatQueryEaUserEaList`
  - Validates requested EA names.
  - Skips duplicate names.
  - Returns matching packed EA data or a dummy zero-value EA record.
  - Uppercases returned dummy names.
  - Handles overflow vs success carefully.
- `FatQueryEaIndexSpecified`
  - Converts a 1-based EA index into a packed-EA offset.
  - Distinguishes nonexistent entry from no-more-EAs.
  - Delegates output construction to `FatQueryEaSimpleScan`.
- `FatQueryEaSimpleScan`
  - Iterates packed EAs from a start offset.
  - Copies packed EA data into `FILE_FULL_EA_INFORMATION` records.
  - Maintains next-entry offsets and CCB resume offset.
  - Returns `STATUS_NO_EAS_ON_FILE`, `STATUS_NO_MORE_EAS`, `STATUS_BUFFER_TOO_SMALL`, `STATUS_BUFFER_OVERFLOW`, or success as appropriate.
- `FatIsDuplicateEaName`
  - Searches only earlier entries in the caller’s EA-name list.
  - Compares names case-insensitively after upcasing.

## Integration

The active file depends on exception/completion support from `fatdata.c`. The disabled implementation depends heavily on lower-level EA file machinery from `easup.c` and EA on-disk structures/macros from `fat.h`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/ea.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/easup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/easup.c

## Purpose

`easup.c` is the lower-level Extended Attribute support layer for FastFAT. Unlike `ea.c`’s disabled dispatch implementation, this file contains active routines for creating, opening, reading, adding, deleting, pinning, dirtying, and unpinning EA data stored in the hidden FAT file `EA DATA. SF`.

## EA Storage Model

The implementation uses an EA database file in the root directory:

- File name: `EA DATA. SF`
- Attributes: read-only, hidden, system, archive
- Header: `EA_FILE_HEADER`
- Handle indirection:
  - `EaBaseTable[240]`
  - offset tables of 128 `USHORT` entries
- Per-file dirents store an EA handle in `Dirent->ExtendedAttributes`.
- Each handle maps to an `EA_SET_HEADER` plus packed EAs.
- `EA_SECTION_SIZE` is `0x40000`; ranges crossing this boundary are copied through an auxiliary buffer because cache mappings may not be contiguous.

## Query Support Routines

- `FatGetEaLength`
  - Returns zero for FAT32 or zero EA handle.
  - Opens the EA file, reads the EA set, and copies `cbList`.
  - Raises `STATUS_NO_EAS_ON_FILE` if a dirent references missing EA data.
- `FatGetNeedEaCount`
  - Returns zero for zero EA handle.
  - Opens the EA file, reads the EA set, and returns `NeedEaCount`.

## Create/Delete Entry Points

- `FatCreateEa`
  - Builds a packed EA set from a caller-provided full EA list.
  - Validates names and flags.
  - Deduplicates by deleting earlier packed EAs with the same name.
  - Ignores zero-length EA values.
  - Rejects EA payloads larger than `MAXIMUM_EA_SIZE`.
  - Creates/opens the EA file and calls `FatAddEaSet`.
  - Writes `cbList`, copies metadata/payload into the new set, marks dirty, flushes cache, and returns the new handle.
  - Returns handle zero when no EA data remains.
- `FatDeleteEa`
  - Opens the EA file.
  - Raises `STATUS_NO_EAS_ON_FILE` if expected EA data is missing.
  - Calls `FatDeleteEaSet`.
  - Flushes the EA file cache.

## EA File Discovery and Creation

`FatGetEaFile` is the central initializer:

- Acquires `Vcb->EaFcb` shared or exclusive depending on caller need.
- If `Vcb->VirtualEaFile` already exists, verifies the EA FCB and pins the EA dirent.
- Otherwise searches the root directory for `EA DATA. SF`.
- If found:
  - pins the dirent
  - initializes `EaFcb` first cluster, dirent offset, allocation size, file size, and MCB
  - opens the virtual stream file
  - stores it in `Vcb->VirtualEaFile`
- If not found and `CreateFile` is true:
  - allocates disk space for an initial EA header plus offset table
  - creates a root-dir dirent
  - constructs the hidden/system/read-only EA file
  - initializes cache/file sizes
  - writes `EA_FILE_SIGNATURE`
  - initializes base table and offset table entries
  - marks data dirty and flushes
- The routine has unwind paths for allocated disk space, created dirent, stream file references, and locks.

## Reading EA Sets

`FatReadEaSet`:

- Validates handle range: `MIN_EA_HANDLE` through `MAX_EA_HANDLE`.
- Pins the EA file header and the relevant offset table.
- Rejects unused handles.
- Computes the EA set VBO from `EaBaseTable[handle >> 7] + offset`.
- Pins the first cluster of the EA set.
- Verifies `EA_SET_SIGNATURE` and `OwnEaHandle`.
- If the caller wants the whole set and `cbList` spans multiple clusters, repins the full rounded range.

## Deleting EA Sets

`FatDeleteEaSet`:

- Validates handle and maps it through the base/offset tables.
- Pins and verifies the target EA set.
- Computes the cluster count from `cbList`.
- Flushes and purges cache pages around the splice point.
- Splits the target cluster run out of the EA file MCB.
- Merges any tail allocation back around the removed range.
- Shrinks `EaFcb` file/allocation size and updates `EaDirent->FileSize`.
- Updates cache manager file sizes.
- Marks the EA dirent dirty.
- Updates base table and offset table:
  - clears the removed handle to `UNUSED_EA_HANDLE`
  - decrements later offsets/base entries by the removed cluster count
- Deallocates removed disk space.
- Provides detailed abnormal-termination recovery before EA metadata is finalized.

## Adding EA Sets

`FatAddEaSet`:

- Pins the EA header and entire offset table.
- Searches backward for an unused handle, inserting near existing handle clusters when possible.
- Adds a new offset-table cluster if needed.
- Checks max handle and max EA file size constraints.
- Allocates all required disk space atomically.
- Flushes and purges cache at the insertion point.
- Splits and merges MCB ranges to insert:
  - optional new offset-table cluster
  - optional initial EA data
  - new EA set clusters
  - optional tail
- Grows file/allocation size and dirent file size.
- Pins new header, offset table, and EA set.
- Initializes `EA_SET_SIGNATURE` and `OwnEaHandle`.
- Updates base/offset tables, including offsets after insertion.
- Marks modified ranges dirty.
- Returns the new EA handle.
- Has extensive unwind logic to restore MCB layout, file sizes, cache state, and allocated disk space on failure.

## Packed EA Helpers

- `FatAppendPackedEa`
  - Converts a `FILE_FULL_EA_INFORMATION` entry into packed EA form.
  - Reallocates the working EA-set buffer in cluster-sized increments when needed.
  - Increments `NeedEaCount` for `FILE_NEED_EA`.
  - Uppercases EA names in stored packed form.
- `FatDeletePackedEa`
  - Removes one packed EA by offset.
  - Decrements `NeedEaCount` for `EA_NEED_EA_FLAG`.
  - Slides remaining packed data down and zeroes the freed tail.
- `FatLocateNextEa`
  - Computes the next packed EA offset or returns `0xffffffff`.
- `FatLocateEaByName`
  - Case-insensitive search across packed EAs.
- `FatIsEaNameValid`
  - Rejects empty names and names longer than 254 bytes.
  - Allows DBCS lead-byte pairs.
  - Uses FAT ANSI character legality rules without wildcards.

## Cache Pinning Helpers

- `FatPinEaRange`
  - Validates requested range is inside EA file allocation.
  - Pins page-sized chunks with `CcPinRead`.
  - Allocates a larger BCB chain if the fixed array is insufficient.
  - Uses an auxiliary buffer when the requested range crosses an EA section boundary.
- `FatMarkEaRangeDirty`
  - Copies auxiliary data back with `CcCopyWrite` if needed.
  - Marks each pinned BCB dirty with `CcSetDirtyPinnedData`.
- `FatUnpinEaRange`
  - Frees auxiliary buffer.
  - Unpins all BCBs.
  - Frees dynamically allocated BCB chains.

## Notable Risks and Behaviors

- The code is FAT12/FAT16-oriented for EA storage; FAT32 is intentionally excluded in higher-level paths.
- Many routines assume the caller holds the right FCB/VCB locks and is in a waitable context where documented.
- EA file mutation depends on careful cache purge and MCB splicing. The unwind logic is central to crash/failure safety.
- `FileName` parameters in `FatReadEaSet` and `FatDeleteEaSet` are currently marked unused, so owner-name verification described in comments is not enforced here.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/easup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/fat.h -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/fat.h

## Purpose

`fat.h` defines FastFAT’s on-disk FAT structures, constants, and low-level macros. It covers BIOS Parameter Blocks, boot sectors, FAT entries, directory entries, timestamp layout, FAT geometry conversion, FAT12 entry packing, and the on-disk EA file format.

## Addressing Types

- `LBO` is a signed 64-bit logical byte offset for disk-relative byte positions.
- `VBO` is a 32-bit virtual byte offset for file/directory/allocation-relative positions.

## Boot Sector and BPB Definitions

The header defines packed and unpacked BIOS Parameter Block forms:

- `PACKED_BIOS_PARAMETER_BLOCK`
- `PACKED_BIOS_PARAMETER_BLOCK_EX` for FAT32
- `BIOS_PARAMETER_BLOCK`

Important helpers:

- `IsBpbFat32(bpb)` checks whether `SectorsPerFat` is zero.
- `FatUnpackBios(Bios, Pbios)` copies packed unaligned byte fields into an unpacked BPB.
- `PACKED_BOOT_SECTOR` and `PACKED_BOOT_SECTOR_EX` model FAT12/16 and FAT32 boot sectors.
- `FSINFO_SECTOR` models the FAT32 FSInfo sector.

## FAT and Dirty-State Constants

The file defines FAT entry values and masks:

- `FAT_ENTRY` as `ULONG32`
- `FAT32_ENTRY_MASK`
- `FAT_CLUSTER_AVAILABLE`
- `FAT_CLUSTER_RESERVED`
- `FAT_CLUSTER_BAD`
- `FAT_CLUSTER_LAST`
- clean/dirty marker constants for FAT12/FAT16/FAT32

It also defines boot-sector dirty flags:

- `FAT_BOOT_SECTOR_DIRTY`
- `FAT_BOOT_SECTOR_TEST_SURFACE`

## Time and Directory Structures

- `FAT_TIME`, `FAT_DATE`, and `FAT_TIME_STAMP` model FAT’s packed timestamp format.
- `FAT8DOT3` models the 11-byte short name.
- `PACKED_DIRENT` / `DIRENT` models a 32-byte FAT directory entry, including:
  - 8.3 name
  - attributes
  - NT byte
  - creation/write/access timestamps
  - high cluster word or EA handle
  - first cluster low word
  - file size

Dirent markers and attributes include:

- never-used, deleted, alias, and escaped `0xE5`
- read-only, hidden, system, volume ID, directory, archive, device
- LFN attribute combination
- NT byte flags for encrypted/EFS and lowercase name optimization

## Geometry Macros

The header provides macro calculations for FAT volume layout:

- `FatBytesPerCluster`
- `FatBytesPerFat`
- `FatReservedBytes`
- `FatRootDirectorySize`
- `FatRootDirectoryLbo`
- `FatRootDirectoryLbo32`
- `FatFileAreaLbo`
- `FatNumberOfClusters`
- `FatIndexBitSize`
- `FatGetLboFromIndex`
- `FatGetIndexFromLbo`

`FatVerifyIndexIsValid` raises `STATUS_FILE_CORRUPT_ERROR` if a cluster index is outside valid volume bounds.

## FAT12 Entry Helpers

- `FatLookup12BitEntry` reads a 12-bit FAT entry from packed FAT12 storage.
- `FatSet12BitEntry` updates a packed 12-bit FAT entry while preserving neighboring nibble data.

These macros rely on unaligned byte-copy helpers to avoid alignment faults.

## EA On-Disk Format

The file defines FAT EA metadata structures:

- `EA_FILE_HEADER`
  - signature
  - recovery/log fields
  - base table of 240 entries
- `EA_OFF_TABLE`
  - 128 offset entries
- `EA_SET_HEADER`
  - per-file EA set signature
  - owner handle
  - `NeedEaCount`
  - owner short filename
  - packed `cbList`
  - packed EA payload
- `PACKED_EA`
  - flags
  - name length
  - value length
  - null-terminated name followed by value

EA constants include:

- `EA_FILE_SIGNATURE`
- `EA_SET_SIGNATURE`
- `SIZE_OF_EA_SET_HEADER`
- `MAXIMUM_EA_SIZE`
- `EA_NEED_EA_FLAG`
- `MIN_EA_HANDLE`
- `MAX_EA_HANDLE`
- `UNUSED_EA_HANDLE`
- table-size constants

Helpers:

- `GetcbList` and `SetcbList` manipulate the packed 4-byte `cbList`.
- `GetEaValueLength` and `SetEaValueLength` manipulate packed value length.
- `SizeOfPackedEa` computes packed EA record size.

## Integration

`fat.h` is foundational for the EA implementation in `easup.c`, the dirent/cluster logic used throughout FastFAT, and BPB/volume layout code elsewhere in the driver.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/fat.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/fatdata.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/fatdata.c

## Purpose

`fatdata.c` defines global FastFAT driver state and implements shared control-path helpers: exception filtering, exception processing, request completion, top-level IRP tracking, Fast I/O information callbacks, and file-corruption popups.

## Global Data

The file defines:

- `FAT_DATA FatData`
- filesystem device objects:
  - `FatDiskFileSystemDeviceObject`
  - `FatCdromFileSystemDeviceObject`
- common `LARGE_INTEGER` constants:
  - zero/max
  - short delays
  - one day
  - Jan 1 1980 and Dec 31 1979
  - magic divisors for time conversion
- `FAT_TIME_STAMP FatTimeJanOne1980`
- `FAST_IO_DISPATCH FatFastIoDispatch`
- nonpaged lookaside lists:
  - IRP contexts
  - nonpaged FCBs
  - ERESOURCE objects
- close-context SLIST and close queue mutex
- reserve MDL/event for paging-file forward progress
- global disk accounting flag

Debug-only globals include trace level, counters, performance timing buckets, and breakpoint-trigger statuses.

## Exception Handling

`FatExceptionFilter`:

- Normalizes `STATUS_IN_PAGE_ERROR` to the embedded I/O status when present.
- If no IRP context exists, bugchecks on unexpected statuses and otherwise handles the exception.
- Marks the IRP context waitable.
- Disables write-through except for `STATUS_CANT_WAIT` and `STATUS_VERIFY_REQUIRED`.
- Stores expected exception status in `IrpContext->ExceptionStatus`.
- Bugchecks unexpected statuses.

`FatProcessException`:

- Handles the saved exception status after an FSD/FSP routine unwinds.
- Aborts MDL writes on write-complete-MDL failures.
- Unpins repinned BCBs with write-through disabled.
- Posts requests when the failure requires waiting or verify work cannot happen at the current APC/IRQL context.
- Completes recursive calls directly, translating cache-top-level verify-required into `STATUS_FILE_LOCK_CONFLICT`.
- Handles user-induced errors:
  - `STATUS_VERIFY_REQUIRED` routes to `FatPerformVerify`.
  - other user-induced errors can raise hard-error popups unless disabled.
- Marks volumes dirty or dirty-with-surface-test for corruption/media errors.
- Calls `FatMarkVolume` under exclusive VCB acquisition when appropriate.
- Completes the IRP through `FatCompleteRequest`.

## Request Completion

`FatCompleteRequest_Real`:

- Debug-breaks on configured interesting completion status.
- Ensures repinned BCBs are unpinned.
- Deletes the IRP context before completing the IRP.
- Clears `IoStatus.Information` on failed input operations to prevent copying invalid output.
- Sets final status and calls `IoCompleteRequest`.

`FatIsIrpTopLevel`:

- If no top-level IRP exists, installs the current IRP and returns true.
- Otherwise returns false.

## Fast I/O

`FatFastIoCheckIfPossible`:

- Accepts only `UserFileOpen`.
- Uses FsRtl byte-range lock checks.
- For writes, also rejects write-protected volumes.
- Does not acquire FCB resources; it is a quick feasibility check.

`FatFastQueryBasicInfo`:

- Accepts user file/directory opens.
- Acquires the FCB shared unless it is a paging file.
- Rejects bad FCB condition.
- Fills timestamps and attributes.
- Root DCB gets zero timestamps and directory attribute.
- Adds temporary/normal attributes as needed.

`FatFastQueryStdInfo`:

- Accepts user file/directory opens.
- Acquires the FCB shared unless paging file.
- Returns link count 1 and delete-pending state.
- For files, requires known allocation size; otherwise fails fast path.
- For directories, returns zero allocation/end-of-file and `Directory = TRUE`.

`FatFastQueryNetworkOpenInfo`:

- Similar acquisition and validation pattern.
- Supplies default change time based on Jan 1 1980.
- Handles root DCB specially.
- Fills allocation and EOF for files only when allocation size is known.

## User Notification

`FatPopUpFileCorrupt`:

- Suppresses popups for the root DCB.
- Ensures the FCB has a full filename.
- Avoids blocking system threads.
- Calls `IoRaiseInformationalHardError` with `STATUS_FILE_CORRUPT_ERROR`.

## Notable Details

- The file contains ReactOS-specific initializer variations for `LARGE_INTEGER` and thread pointer casts.
- Exception processing is tightly coupled to cache-manager state: repinned BCBs, MDL writes, verify handling, and volume dirtying all converge here.
- Fast I/O paths deliberately return false when state is incomplete, forcing the normal IRP path to handle slower or blocking cases.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/fatdata.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/fatdata.h -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/fatdata.h

## Purpose

`fatdata.h` declares global FastFAT driver data and debug/timing macros shared across the driver. It is the header counterpart to `fatdata.c`.

## Global Declarations

The header declares:

- `extern FAT_DATA FatData`
- `FatGarbageIosb`
- lookaside lists:
  - `FatIrpContextLookasideList`
  - `FatNonPagedFcbLookasideList`
  - `FatEResourceLookasideList`
- close queue state:
  - `FatCloseContextSList`
  - `FatCloseQueueMutex`
- filesystem device objects:
  - `FatDiskFileSystemDeviceObject`
  - `FatCdromFileSystemDeviceObject`
- time and arithmetic constants:
  - `FatLargeZero`
  - `FatMaxLarge`
  - `Fat30Milliseconds`
  - `Fat100Milliseconds`
  - `FatOneSecond`
  - `FatOneDay`
  - `FatJanOne1980`
  - `FatDecThirtyOne1979`
  - `FatTimeJanOne1980`
  - `FatMagic10000`
  - `FatMagic86400000`
- reserve MDL/event:
  - `FatReserveMdl`
  - `FatReserveEvent`
- `FatFastIoDispatch`
- `FatDiskAccountingEnabled`

## Time Conversion Macros

- `FatConvert100nsToMilliseconds`
- `FatConvertMillisecondsToDays`
- `FatConvertDaysToMilliseconds`

These use `RtlExtendedMagicDivide` and predefined magic divisors/shifts for fast time conversion.

## I/O and Close Constants

- `READ_AHEAD_GRANULARITY` is `0x10000`.
- `FAT_MAX_IO_RUNS_ON_STACK` is 5.
- `FAT_MAX_DELAYED_CLOSES` is 16.
- `FatMaxDelayedCloseCount` is declared.
- `FAT_DEFAULT_DEFRAG_CHUNK_IN_BYTES` is `0x10000`.

## Time Rounding Constants

Defines:

- `TenMSec`
- `TwoSeconds`
- `AlmostTenMSec`
- `AlmostTwoSeconds`
- `HighPartPerDay`

These support FAT timestamp rounding/conversion behavior elsewhere.

## Debug Trace Infrastructure

Under `FASTFATDBG`, the header defines trace-level bit flags for major subsystems:

- errors, debug hooks, exceptions, unwind
- cleanup, close, create, directory control
- EA, file info, FS control, locks
- read/write/flush/volume info
- device control, shutdown, PNP
- support modules such as allocation, directory, cache, verify, device I/O, structure support
- FSP dispatcher/dump

It declares:

- `FatDebugTraceLevel`
- `FatDebugTraceIndent`
- FSD/FSP/I/O counters
- `FatTotalTicks`
- `FatPerformanceTimerLevel`
- `FatNull`

Macros:

- `DebugTrace`
  - checks trace mask
  - prints thread id and indentation
  - adjusts indentation before/after printing
- `DebugDump`
  - prints text and optionally dumps a FastFAT structure with `FatDump`
  - asserts afterward
  - has MSVC and non-MSVC variants
- `DebugUnwind`
  - reports abnormal SEH termination
- `DebugDoit`
  - executes debug-only statements
- `TimerStart` / `TimerStop`
  - collect performance-counter elapsed ticks by trace level

Without `FASTFATDBG`, these macros become no-ops and `FatNull` is `NULL`.

## DBG-Only Support

Under `DBG`, the header declares:

- `FatBreakOnInterestingIoCompletion`
- `FatBreakOnInterestingExceptionStatus`
- `FatBreakOnInterestingIrpCompletion`
- `FatTestRaisedStatus`

It also defines `DbgDoit` as enabled only for DBG builds.

## Integration

This header is included broadly through `fatprocs.h`. It connects:

- debug dump support in `dumpsup.c`
- globals implemented in `fatdata.c`
- exception tracing and completion diagnostics throughout FastFAT
- timing and conversion helpers used by timestamp code
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/fatdata.h -->