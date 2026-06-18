# Group Research: group_1839_windows_driver_samples_sources_windows_windows_driver_samples_files_6fa44745eef7

Scope: `Docs/research_subset_a.md` includes `sources/windows/windows-driver-samples`. All five listed FastFAT files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/easup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/easup.c

This file implements FastFAT extended attribute support backed by the hidden FAT12/FAT16 EA metadata file `EA DATA. SF`. It handles EA length/count lookup, EA set creation/deletion, EA handle table management, packed EA list manipulation, and cache-manager pin/dirty/unpin handling for EA-file ranges.

Key routines:
- `FatGetEaLength` returns the packed EA byte count for a file dirent. It short-circuits to zero on FAT32 or handle zero, then opens the EA file, reads the owning EA set, and copies `cbList`.
- `FatGetNeedEaCount` similarly reads an EA set and returns `NeedEaCount`.
- `FatCreateEa` converts a user `FILE_FULL_EA_INFORMATION` list into FastFAT packed EA records, validates names/flags, removes duplicate names, ignores zero-length values, allocates an EA handle/set, writes the EA-set header/body, and flushes the virtual EA file.
- `FatDeleteEa` opens the EA file and delegates to `FatDeleteEaSet`.
- `FatGetEaFile` lazily locates or creates `EA DATA. SF` in the root directory, initializes `Vcb->EaFcb`, creates the virtual stream file, sets file sizes, allocates initial clusters, initializes `EA_FILE_HEADER`, base table, and offset tables, and unwinds partial creation on failure.
- `FatReadEaSet` validates an EA handle, reads the base/offset table entry, computes the set VBO, pins the EA set, verifies signature/handle ownership, and optionally repins the full set length.
- `FatDeleteEaSet` removes an EA set by purging cache pages, splitting the file allocation around the target cluster range, shrinking the EA file, updating dirent/file sizes, adjusting later base/offset entries, marking metadata dirty, and deallocating removed clusters.
- `FatAddEaSet` allocates and splices clusters for a new EA set, optionally inserts a new offset-table cluster, updates cache/file sizes, initializes the new set header, adjusts base/offset tables, and returns the new EA handle.
- `FatAppendPackedEa`, `FatDeletePackedEa`, `FatLocateNextEa`, and `FatLocateEaByName` implement in-memory packed-EA list editing.
- `FatIsEaNameValid` enforces FAT EA name legality using FAT ANSI character rules and DBCS lead-byte handling.
- `FatPinEaRange`, `FatMarkEaRangeDirty`, and `FatUnpinEaRange` wrap cache-manager pinned access to EA file ranges, including auxiliary buffers when a range crosses an EA section boundary.

Important data model:
- EA data lives in `EA DATA. SF`, not in each normal file.
- A file dirent’s `ExtendedAttributes` field is an EA handle.
- `EA_FILE_HEADER` contains base offsets for EA handle groups.
- Offset-table entries map each handle to a cluster offset, with `UNUSED_EA_HANDLE` marking free handles.
- `EA_SET_HEADER` stores the owning handle, needed-EA count, owner filename, packed list length, and packed EA records.
- The code assumes EA support is meaningful for FAT12/FAT16; FAT32 lookup returns zero EA length.

Concurrency and cache behavior:
- Callers are expected to hold filesystem critical-region state.
- EA FCB access is acquired shared or exclusive depending on mutation.
- Creation/deletion paths require waitable execution and exclusive EA FCB access.
- Cache coherency is explicit: dirty pinned data is marked, caches are flushed, purge retries are used before allocation splicing, and `CcSetFileSizes` updates cache-manager file sizes after growth/shrink.
- Ranges spanning `EA_SECTION_SIZE` or too many pages use auxiliary buffers to avoid assumptions about contiguous mapped system addresses.

Failure and corruption behavior:
- Invalid handles raise `STATUS_NONEXISTENT_EA_ENTRY`.
- Missing required EA file raises `STATUS_NO_EAS_ON_FILE`.
- Bad signatures, wrong owning handle, or impossible lengths raise data/corruption status.
- Oversized EA lists raise `STATUS_EA_TOO_LARGE`.
- Purge failure raises `STATUS_UNABLE_TO_DELETE_SECTION`.
- Most mutating paths maintain unwind state so partially allocated clusters, dirents, Mcbs, stream references, and cache sizes can be restored where possible.

Role in the subset:
- This is a dense example of legacy Windows FAT metadata support layered over a simple on-disk filesystem using a hidden metadata file, cache-manager pins, and FAT-chain splicing.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/easup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/fat.h -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/fat.h

This header defines FastFAT’s on-disk format contracts and core layout macros: boot sectors, BPBs, FAT entries, timestamps, directory entries, FAT geometry calculations, FAT12 entry packing, and extended-attribute structures.

Major definitions:
- Basic offset types:
  - `LBO` is a signed 64-bit logical byte offset, needed for FAT32-scale media.
  - `VBO` is a 32-bit file-relative byte offset.
- Packed BPB structures:
  - `PACKED_BIOS_PARAMETER_BLOCK` for FAT12/16-style BPB fields.
  - `PACKED_BIOS_PARAMETER_BLOCK_EX` for FAT32 extensions.
  - `BIOS_PARAMETER_BLOCK` is the unpacked in-memory form.
  - `FatUnpackBios` copies unaligned packed fields into the unpacked structure.
  - `IsBpbFat32` detects FAT32 by zero `SectorsPerFat`.
- Boot sector structures:
  - `PACKED_BOOT_SECTOR`
  - `PACKED_BOOT_SECTOR_EX`
  - `FSINFO_SECTOR` and FAT32 FSInfo signatures.
- FAT state:
  - `FAT_ENTRY`
  - FAT32 entry mask and clean/dirty constants.
  - available/reserved/bad/last-cluster markers.
- Time and directory layout:
  - `FAT_TIME`, `FAT_DATE`, `FAT_TIME_STAMP`.
  - `FAT8DOT3`.
  - `PACKED_DIRENT`/`DIRENT`, a 32-byte on-disk directory entry with attributes, timestamps, cluster fields, and file size.
  - Dirent first-byte states and attributes, including LFN attribute composition.
  - NT byte flags for EFS and lowercase-name optimization.
- Geometry macros:
  - `FatBytesPerCluster`
  - `FatBytesPerFat`
  - `FatReservedBytes`
  - `FatRootDirectorySize`
  - `FatRootDirectoryLbo`
  - `FatRootDirectoryLbo32`
  - `FatFileAreaLbo`
  - `FatNumberOfClusters`
  - `FatIndexBitSize`
- Allocation translation:
  - `FatVerifyIndexIsValid`
  - `FatGetLboFromIndex`
  - `FatGetIndexFromLbo`
- FAT12 helpers:
  - `FatLookup12BitEntry`
  - `FatSet12BitEntry`
- EA structures:
  - `EA_FILE_HEADER` for the hidden EA file header.
  - `EA_OFF_TABLE` for handle offset tables.
  - `EA_SET_HEADER` for a per-file EA set.
  - `PACKED_EA` for individual packed EAs.
  - `GetcbList`, `SetcbList`, `GetEaValueLength`, `SetEaValueLength`, and `SizeOfPackedEa`.
  - EA limits such as `MAXIMUM_EA_SIZE`, `MIN_EA_HANDLE`, `MAX_EA_HANDLE`, `UNUSED_EA_HANDLE`, `MAX_EA_BASE_INDEX`, and `MAX_EA_OFFSET_INDEX`.

Important filesystem semantics:
- FAT32 root directory handling differs from FAT12/16: the root is cluster-chain backed, while FAT12/16 has a fixed root directory region.
- Cluster indexes 0 and 1 are invalid for normal data; valid file clusters begin at 2.
- FAT type selection is cluster-count based for non-FAT32 volumes.
- FAT12 entries are 12-bit packed entries shared across byte boundaries, requiring unaligned copy/shifting helpers.
- EA constants and structures are consumed directly by `easup.c`.

Role in the subset:
- This is the central on-disk FAT schema file for the FastFAT sample. It maps raw FAT bytes into C structures and provides the arithmetic used by mount, allocation, directory, and EA code.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/fat.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/fatdata.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/fatdata.c

This file defines FastFAT global data and implements common request-control helpers: exception filtering/processing, request completion, top-level IRP marking, fast I/O metadata paths, and corruption popups.

Global state defined here:
- `FatData`, the main filesystem-wide state record.
- Filesystem device objects for disk and CD-ROM FAT.
- Common `LARGE_INTEGER` constants, FAT time constants, and magic divisors for time conversion.
- `FatFastIoDispatch`.
- Nonpaged lookaside lists for IRP contexts, nonpaged FCBs, and resources.
- Close-context SList and close queue mutex.
- Reserve MDL/event for paging-file forward progress.
- Disk accounting state.
- Debug/performance globals under `FASTFATDBG` and `DBG`.

Key routines:
- `FatBugCheckExceptionFilter` is debug-only and bugchecks on unexpected exceptions.
- `FatExceptionFilter` normalizes exception status, unwraps `STATUS_IN_PAGE_ERROR`, records expected statuses into the IRP context, forces waitability for cleanup, disables write-through where appropriate, and bugchecks on unexpected kernel exceptions.
- `FatProcessException` is the central exception completion path. It aborts MDL writes, unpins repinned BCBs, posts wait-required or verify-required requests when necessary, performs verify handling, raises hard errors for user-induced media/device conditions, marks volumes dirty or surface-test dirty on corruption/media failures, and completes the IRP.
- `FatCompleteRequest_Real` unpins repinned BCBs, deletes the IRP context, zeroes information on failed input operations, sets final status, and calls `IoCompleteRequest`.
- `FatIsIrpTopLevel` sets the current IRP as top-level when no top-level IRP exists.
- `FatFastIoCheckIfPossible` accepts only user file opens, checks byte-range locks for read/write, and rejects fast writes on write-protected volumes.
- `FatFastQueryBasicInfo` fills `FILE_BASIC_INFORMATION` from an FCB/DCB when the object is healthy and lock acquisition succeeds.
- `FatFastQueryStdInfo` fills `FILE_STANDARD_INFORMATION`, avoiding slow allocation lookup when allocation size is still unknown.
- `FatFastQueryNetworkOpenInfo` combines time, attribute, allocation, and EOF metadata for network-open fast path.
- `FatPopUpFileCorrupt` raises an informational hard error for corrupt non-root files, resolving the full name first and avoiding blocking system threads.

Important behavior:
- The exception path distinguishes recursive/cache-top-level calls from top-level filesystem calls.
- Verify-required errors are handled through `FatPerformVerify` when possible.
- User-induced errors can result in `IoRaiseHardError`; corruption-like statuses can mark the volume dirty.
- Fast I/O paths are conservative: they return false unless object type, FCB state, locking, and cached allocation information are all suitable.
- Root DCBs get synthesized metadata rather than normal dirent-derived timestamps/sizes.

Role in the subset:
- This file shows how a Windows filesystem driver centralizes global state, exception discipline, I/O completion, fast metadata queries, and dirty-volume escalation around NT I/O manager and cache manager contracts.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/fatdata.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/fatdata.h -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/fatdata.h

This header declares FastFAT global state, tuning constants, time conversion helpers, debug tracing macros, and debug-only break controls used across the driver.

Main declarations:
- Global filesystem data:
  - `FatData`
  - `FatGarbageIosb`
  - filesystem device objects
  - fast I/O dispatch table
  - disk accounting state
- Memory/synchronization globals:
  - IRP context, nonpaged FCB, and ERESOURCE lookaside lists.
  - close-context SList.
  - close queue mutex.
  - reserve MDL and reserve event.
- Time constants:
  - zero/max large integers.
  - small relative timeouts.
  - day and FAT epoch constants.
  - `FatTimeJanOne1980`.
  - magic divisors for fast conversion from 100ns units to milliseconds and milliseconds to days.
- Operational tuning:
  - `READ_AHEAD_GRANULARITY`
  - `FAT_MAX_IO_RUNS_ON_STACK`
  - `FAT_MAX_DELAYED_CLOSES`
  - `FAT_DEFAULT_DEFRAG_CHUNK_IN_BYTES`
  - close-count limit declaration.
- Time rounding constants:
  - 10ms and 2s rounding helpers.
  - `HighPartPerDay`.

Debug infrastructure:
- Under `FASTFATDBG`, it defines trace categories for each major subsystem: cleanup, close, create, directory control, EA, file info, fsctl, lock control, read/write, volume info, flush, device control, shutdown, PNP, allocation, directory support, cache support, device I/O support, FSP dispatcher, and others.
- `DebugTrace` prints thread id, indentation, and formatted messages when a trace level is enabled.
- `DebugDump` optionally dumps structures and asserts.
- `DebugUnwind` traces abnormal termination.
- `TimerStart`/`TimerStop` accumulate lightweight performance counters.
- Retail builds reduce these macros to no-ops.
- `DbgDoit` remains available for general `DBG` builds.
- Debug break controls expose statuses of interest for exception and IRP completion breakpoints.

Role in the subset:
- This header is the cross-file declaration point for FastFAT’s driver-wide state and diagnostics. It supports the implementation files in this group: `fatinit.c` initializes many of these globals, while `fatdata.c` defines and uses them.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/fatdata.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/fatinit.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/fatinit.c

This file implements FastFAT driver initialization, unload cleanup, and two registry-query helpers for compatibility behavior and Fujitsu FMR hardware detection.

Key routines:
- `DriverEntry`
  - Creates the disk filesystem device object named `\Fat`.
  - Creates the CD-ROM filesystem device object named `\FatCdrom`.
  - Installs unload, major IRP dispatch routines, and fast I/O dispatch routines.
  - Registers filesystem filter callbacks, specifically pre-acquire handling for section synchronization.
  - Zeroes and initializes `FatData`.
  - Initializes VCB queues, close lists, close work item, zero page, spin lock, cache-manager callbacks, process pointer, and processor count.
  - Reads `Win31FileSystem` to decide Chicago compatibility behavior.
  - Reads `FatDisableCodePageInvariance` to decide code-page invariance behavior.
  - Initializes the global resource and nonpaged lookaside lists.
  - Initializes close queue synchronization and paging reserve event.
  - Registers both filesystem device objects with the I/O manager and references them.
  - Detects Fujitsu FMR hardware.
  - On Windows 8+ caches global disk accounting state.
- `FatUnload`
  - Deletes lookaside lists and the global resource.
  - Frees the close work item.
  - Dereferences the disk and CD-ROM filesystem device objects.
- `FatGetCompatibilityModeValue`
  - Opens `\Registry\Machine\System\CurrentControlSet\Control\FileSystem`.
  - Queries a named DWORD-like value using `ZwQueryValueKey`.
  - Uses a stack buffer first and allocates a larger paged buffer on overflow.
  - Returns success only when data exists.
- `FatIsFujitsuFMR`
  - Opens `\Registry\Machine\Hardware\DESCRIPTION\System`.
  - Reads `Identifier`.
  - Returns true when it starts with `FUJITSU FMR-`.

Important initialization wiring:
- Major functions are assigned for create, close, read, write, query/set information, query/set EA, flush, query/set volume information, cleanup, directory control, filesystem control, lock control, device control, shutdown, and PNP.
- Fast I/O entries include check-if-possible, copy read/write, basic/standard/network open info, lock/unlock, cache flush acquire/release, and MDL read/write helpers.
- Cache-manager callbacks are configured for lazy write/read-ahead plus no-op variants.
- Delayed close depth scales with `MmQuerySystemSize`.

Failure handling:
- If CD-ROM device creation fails, the disk device is deleted.
- If filter callback registration fails, both device objects are deleted.
- If close work item or zero page allocation fails, created device objects are deleted.
- Registry-query helper frees any allocated query buffer before returning.

Role in the subset:
- This is the FastFAT driver bootstrap file. It connects the filesystem implementation to the Windows I/O manager, cache manager, filter manager callback path, global state, registry configuration, and unload lifecycle.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/fatinit.c -->