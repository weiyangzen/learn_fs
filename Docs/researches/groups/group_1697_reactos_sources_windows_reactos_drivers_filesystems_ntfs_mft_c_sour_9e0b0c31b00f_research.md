# Group Research: group_1697_reactos_sources_windows_reactos_drivers_filesystems_ntfs_mft_c_sour_9e0b0c31b00f

Scope confirmed against `Docs/research_subset_a.md`: `sources/windows/reactos` is included in subset A. All six listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/mft.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ntfs/mft.c

## Purpose

`mft.c` is the ReactOS NTFS driver's central metadata and attribute I/O implementation. It reads and writes MFT file records, finds and resizes NTFS attributes, handles data-run backed nonresident attributes, updates directory indexes, allocates new MFT records, updates `$MFTMirr`, and provides file/path lookup helpers over NTFS directory indexes.

## Main Responsibilities

- Create and release `NTFS_ATTR_CONTEXT` objects around copied attribute records.
- Decode and cache nonresident attribute mapping pairs through `LARGE_MCB`.
- Find attributes in a file record, including attribute-list references to extension records.
- Read and write resident and nonresident attributes.
- Resize resident and nonresident attributes, including resident-to-nonresident migration.
- Grow `$MFT` and `$MFT::$BITMAP` when no free file-record slots remain.
- Apply and generate NTFS update-sequence-array fixups for file and index records.
- Add a new MFT record and mark it allocated in `$MFT::$BITMAP`.
- Add a filename entry to a directory's `$I30` index using the B-tree helper layer.
- Search directory indexes and subnodes for exact filename lookup or wildcard enumeration.
- Update parent directory `$FILE_NAME` index-entry sizes after file-size changes.

## Key Functions

`PrepareAttributeContext` and `ReleaseAttributeContext`

- Allocate attribute contexts from `NtfsGlobalData->AttrCtxtLookasideList`.
- Copy the raw `NTFS_ATTR_RECORD` into nonpaged pool.
- For nonresident attributes, initialize run-cache fields and convert mapping pairs into `DataRunsMCB`.
- Release the MCB and copied record on cleanup.

`FindAttribute`

- Iterates attributes with `FindFirstAttribute` / `FindNextAttribute`.
- Matches by type and optional name.
- Returns a prepared context and optional record offset.
- If not found locally, scans the attribute list and recursively reads referenced MFT records.
- Rejects attribute-list references back to the same record as missing/corrupt.

`ReadAttribute`

- For resident attributes, bounds the request to `Resident.ValueLength` and copies from the resident value.
- For nonresident attributes, converts the context MCB back into data runs, walks runs to the requested offset, reads clusters via `NtfsReadDisk`, and zero-fills sparse runs.
- Maintains cache-run fields, but the cache path is disabled with `if (0)`.

`WriteAttribute`

- For resident attributes, finds the matching attribute in the file record, copies into the resident value, updates the file record, and refreshes the caller's context copy.
- For nonresident attributes, converts MCB runs back into mapping pairs, walks target runs, and writes sectors through `NtfsWriteDisk`.
- Does not support writing sparse runs and returns `STATUS_NOT_IMPLEMENTED` for them.

`SetAttributeDataLength`, `SetResidentAttributeDataLength`, and `SetNonResidentAttributeDataLength`

- Check memory-mapped-file truncation with `MmCanFileBeTruncated`.
- Dispatch resizing by resident/nonresident type.
- Grow nonresident attributes by allocating clusters with `NtfsAllocateClusters` and appending runs with `AddRun`.
- Shrink nonresident attributes through `FreeClusters`.
- Resize resident attributes in-record when possible.
- Convert resident attributes to nonresident when they no longer fit, backing up existing data and rewriting it after allocation.
- Update FCB file sizes and cache manager sizes after successful top-level resizing.

`IncreaseMftSize`

- Acquires `Vcb->DirResource` exclusively.
- Creates blank file records and clears their in-use flag.
- Reads `$MFT::$BITMAP`, computes the larger bitmap size, grows `$MFT::$DATA`, optionally grows `$BITMAP`, writes the expanded bitmap, writes blank records, and updates `$MFTMirr`.
- Adds 64 records at a time because `ATTR_RECORD_ALIGNMENT * 8` new bitmap bits are introduced.

`AddNewMftEntry`

- Reads `$MFT::$BITMAP`, masks reserved records `0x10` through `0x17`, finds a free bit starting at 24, marks it used, restores reserved bits, writes the bitmap, and writes the new file record.
- If no free slot exists, calls `IncreaseMftSize` and retries recursively.
- Disables global write support for MFT bitmap sizes beyond 32-bit `RTL_BITMAP` support.

`NtfsAddFilenameToDirectory`

- Reads the parent directory record and its `$I30` `$INDEX_ROOT`.
- Converts the index to a B-tree, inserts the filename key, updates `$INDEX_ALLOCATION`, possibly demotes the root, rebuilds `$INDEX_ROOT`, resizes the resident index-root attribute, writes the parent record, and writes the new index-root payload.
- The comments explicitly describe this as work-in-progress and warn that intermediate failure can leave the directory damaged.

`BrowseIndexEntries`, `BrowseSubNodeIndexEntries`, `NtfsFindMftRecord`, `NtfsLookupFileAt`, and `NtfsFindFileAt`

- Traverse directory `$I30` index roots and optional `$INDEX_ALLOCATION` subnodes.
- Use `$I30` `$BITMAP` to validate subnode allocation.
- Apply fixups to index buffers before scanning.
- Skip DOS-name entries and system entries below `NTFS_FILE_FIRST_USER_FILE`.
- Support exact lookup and wildcard directory enumeration via `CompareFileName`.

`UpdateFileNameRecord` and `UpdateIndexEntryFileNameSize`

- Locate the parent directory's `$I30` index entry for a filename.
- Update `FileName.DataSize` and `FileName.AllocatedSize`.
- Write back either the resident index root or a nonresident index allocation record.

`ReadFileRecord`, `UpdateFileRecord`, `FixupUpdateSequenceArray`, and `AddFixupArray`

- Read/write records through `$MFT::$DATA`.
- Verify and restore update-sequence-array protected sector trailers on read.
- Insert update-sequence numbers before writing and immediately undo them in-memory afterward.

`UpdateMftMirror`

- Reads `$MFTMirr`, locates `$MFTMirr::$DATA` and `$MFT::$DATA`, copies the mirrored prefix of `$MFT`, and writes it into `$MFTMirr::$DATA`.

## Integration

- Uses allocation helpers from `volinfo.c`: `NtfsAllocateClusters`.
- Uses attribute construction/run helpers from `attrib.c`: `AddRun`, `FreeClusters`, `ConvertDataRunsToLargeMCB`, `ConvertLargeMCBToDataRuns`, `DecodeRun`, and filename extraction helpers.
- Uses B-tree helpers from `btree.c` for directory index mutation.
- Uses raw block helpers from `blockdev.c`: `NtfsReadDisk`, `NtfsWriteDisk`, and `NtfsReadSectors`.
- Serves read/write paths in `rw.c`, create paths in `create.c`, directory control in `dirctl.c`, and file information update paths in `finfo.c`.

## Notable Behavior and Risks

- Several write paths are explicitly incomplete: sparse writes, large-file writes through callers, compressed/encrypted streams, robust rollback, and full attribute-list growth are not complete.
- `ReadAttribute` and `WriteAttribute` convert MCBs back to data-run buffers for every nonresident I/O because the run cache is disabled.
- `SetNonResidentAttributeDataLength` forcibly recalculates `HighestVCN` with a FIXME noting sparse files will break this math.
- `NtfsAddFilenameToDirectory` can leave a directory inconsistent if failure occurs after temporarily shrinking `$INDEX_ROOT`.
- Many APIs use `ULONG` offsets/lengths even when NTFS sizes are 64-bit; callers reject or avoid large-file cases in some paths, but this remains a structural limit.
- `FindAttribute` does not guard all malformed attribute lengths itself; it relies heavily on lower-level attribute iterators and assertions.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/mft.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/misc.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ntfs/misc.c

## Purpose

`misc.c` contains small shared utility routines for NTFS IRP setup, top-level IRP tracking, NTFS-to-Windows attribute conversion, and user-buffer access/locking.

## Main Functions

`NtfsIsIrpTopLevel`

- Checks `IoGetTopLevelIrp()`.
- If no top-level IRP is set, installs the current IRP and returns `TRUE`.
- Otherwise returns `FALSE`.

`NtfsAllocateIrpContext`

- Allocates an `NTFS_IRP_CONTEXT` from the global IRP-context lookaside list.
- Initializes identifier, IRP, device object, stack location, major/minor function, file object, top-level state, priority boost, and default completion flag.
- Sets `IRPCONTEXT_CANWAIT` for filesystem control, device control, shutdown, synchronous operations, and most non-cleanup/non-close requests.

`NtfsFileFlagsToAttributes`

- Converts NTFS file attribute flags into Win32 file attributes.
- Maps `NTFS_FILE_TYPE_DIRECTORY` to `FILE_ATTRIBUTE_DIRECTORY`.
- Produces `FILE_ATTRIBUTE_NORMAL` when the NTFS attribute mask is zero.

`NtfsGetUserBuffer`

- Returns a system address for an MDL-backed IRP buffer with `MmGetSystemAddressForMdlSafe`.
- Otherwise returns `Irp->UserBuffer`.
- Uses higher page priority for paging I/O.

`NtfsLockUserBuffer`

- Ensures an IRP has an MDL for its user buffer.
- Allocates an MDL if needed and probes/locks pages with the requested `LOCK_OPERATION`.
- Uses SEH to free the MDL and return the exception code if probing fails.

## Integration

These helpers are used by dispatch and read/write code. `NtfsAllocateIrpContext` creates the common request state consumed by all NTFS major-function handlers, while `NtfsGetUserBuffer` and `NtfsLockUserBuffer` are used directly in `rw.c`.

## Notable Behavior

- `NtfsGetUserBuffer` returns raw `Irp->UserBuffer` when no MDL exists, so callers must know whether direct, buffered, or neither I/O is in effect.
- `NtfsLockUserBuffer` leaves successful MDL unlock/free responsibility to the I/O manager or later IRP cleanup.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/ntfs.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ntfs/ntfs.c

## Purpose

`ntfs.c` is the NTFS driver entry module. It creates the filesystem device object, initializes global state, registers dispatch and fast-I/O entry points, initializes lookaside lists, reads the experimental write-support registry switch, and registers the filesystem with the I/O manager.

## Main Functions

`DriverEntry`

- Creates the `\Ntfs` device with type `FILE_DEVICE_DISK_FILE_SYSTEM`.
- Stores and initializes `NtfsGlobalData` in the device extension.
- Initializes the global resource.
- Disables write support by default.
- Reads registry value `MyDataDoesNotMatterSoEnableExperimentalWriteSupportForEveryNTFSVolume`; if present and true, enables write support globally.
- Calls `NtfsInitializeFunctionPointers`.
- Installs cache manager callbacks for lazy write and read-ahead.
- Installs fast-I/O callbacks for check, read, and write.
- Initializes nonpaged lookaside lists for IRP contexts, FCBs, and attribute contexts.
- Sets `DriverUnload` to `NULL`.
- Marks the filesystem device as `DO_DIRECT_IO`.
- Calls `IoRegisterFileSystem` and references the device object.

`NtfsInitializeFunctionPointers`

- Routes supported major functions to `NtfsFsdDispatch`:
  - create, close, cleanup
  - read, write
  - query/set file information
  - query/set volume information
  - directory control
  - filesystem control
  - device control

## Integration

This file owns the global `PNTFS_GLOBAL_DATA NtfsGlobalData`. The lookaside lists it initializes are used throughout the driver by `misc.c`, `mft.c`, FCB code, and mount/volume paths. The dispatch table points all handled IRPs into the common dispatch layer declared in `ntfs.h`.

## Notable Behavior

- Write support is deliberately gated behind a long, explicit registry value name and remains off by default.
- The driver cannot be unloaded after initialization.
- Fast I/O is advertised through callbacks, but actual capability depends on the implementations in `fastio.c`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/ntfs.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/ntfs.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ntfs/ntfs.h

## Purpose

`ntfs.h` is the central private header for the ReactOS NTFS driver. It defines on-disk NTFS structures, in-memory VCB/FCB/CCB/global/IRP-context structures, constants, tags, helper macros, inline queue marking, and cross-module prototypes.

## Major Definitions

### Driver and Allocation Constants

- Pool tags: `TAG_NTFS`, `TAG_CCB`, `TAG_FCB`, `TAG_IRP_CTXT`, `TAG_ATT_CTXT`, `TAG_FILE_REC`.
- Rounding helpers: `ROUND_UP`, `ROUND_DOWN`.
- Device name: `\Ntfs`.
- File-record and data-run alignment constants:
  - `ATTR_RECORD_ALIGNMENT`
  - `DATA_RUN_ALIGNMENT`
  - `VALUE_OFFSET_ALIGNMENT`.

### Boot and Volume Structures

- `BIOS_PARAMETERS_BLOCK`
- `EXTENDED_BIOS_PARAMETERS_BLOCK`
- `BOOT_SECTOR`
- `NTFS_INFO`

These capture NTFS boot-sector geometry, MFT/MFTMirr locations, cluster and record sizes, volume label, version, flags, and MFT-zone reservation.

### In-Memory Driver State

`DEVICE_EXTENSION` / `NTFS_VCB`

- Contains volume resource state, FCB list, VPB/storage device pointers, stream file object, `$MFT` context and record, volume FCB, parsed NTFS info, file-record lookaside list, MFT data offset, flags, and open-handle count.

`NTFS_GLOBAL_DATA`

- Stores global driver identity, resource, driver/device object pointers, cache callbacks, fast-I/O dispatch table, lookaside lists, and global experimental write-support flag.

`NTFS_CCB`

- Per-open context with directory enumeration state and search pattern.

`NTFS_FCB`

- Per-file state with `FSRTL_COMMON_FCB_HEADER`, section pointers, stream name, path/object names, paging/main resources, parent link, list entry, ref/open counts, flags, MFT index, link count, and cached filename attribute.

`NTFS_IRP_CONTEXT`

- Per-request dispatch state, including IRP, stack location, major/minor function, wait/queue flags, top-level state, target device/file object, saved exception status, and priority boost.

`NTFS_ATTR_CONTEXT`

- Per-attribute state with cached data-run position fields, `LARGE_MCB`, owning file MFT index fields, and copied `NTFS_ATTR_RECORD`.

### On-Disk NTFS Structures

- Attribute type enum covering standard NTFS attributes from `$STANDARD_INFORMATION` through `$LOGGED_UTILITY_STREAM`.
- System file numbers: `$MFT`, `$MFTMirr`, `$LogFile`, `$Volume`, `$AttrDef`, root, `$Bitmap`, `$Boot`, `$BadClus`, `$Quota`, `$UpCase`, `$Extend`.
- File reference mask `NTFS_MFT_MASK`.
- Collation constants and index flags.
- File-name namespace constants.
- NTFS file-attribute flags.
- `NTFS_RECORD_HEADER`, `FILE_RECORD_HEADER`, `NTFS_ATTR_RECORD`, `NTFS_ATTRIBUTE_LIST_ITEM`.
- `STANDARD_INFORMATION`, `ATTRIBUTE_LIST`, `FILENAME_ATTRIBUTE`.
- Directory-index structures:
  - `INDEX_HEADER_ATTRIBUTE`
  - `INDEX_ROOT_ATTRIBUTE`
  - `INDEX_BUFFER`
  - `INDEX_ENTRY_ATTRIBUTE`
- B-tree helper structures:
  - `B_TREE_KEY`
  - `B_TREE_FILENAME_NODE`
  - `B_TREE`
- `VOLINFO_ATTRIBUTE`, `REPARSE_POINT_ATTRIBUTE`, and `FIXUP_ARRAY`.

## Inline Helper

`NtfsMarkIrpContextForQueue`

- Clears `IRPCONTEXT_COMPLETE`.
- Sets `IRPCONTEXT_QUEUE`.
- Returns `STATUS_PENDING`.

## Prototype Surface

The header exposes module contracts for:

- `attrib.c`: attribute creation, data-run conversion, attribute enumeration, filename/standard-info extraction, run packing, cluster freeing.
- `blockdev.c`: raw disk reads/writes, sector reads, device I/O controls.
- `btree.c`: directory index B-tree creation, insertion, split/demotion, serialization, and index-allocation updates.
- `cleanup.c`, `close.c`, `create.c`, `devctl.c`, `dirctl.c`, `dispatch.c`, `fastio.c`, `fcb.c`, `finfo.c`, `fsctl.c`.
- `mft.c`: attribute contexts, attribute I/O, file-record read/write, fixups, directory lookup, MFT growth, filename-index update.
- `misc.c`: IRP context and user-buffer helpers.
- `rw.c`: read/write dispatch handlers.
- `volinfo.c`: cluster allocation/free-space reporting and volume-information IRPs.
- `ntfs.c`: driver initialization and dispatch-table setup.

## Notable Details

- The header uses packed definitions for boot-sector structures, matching on-disk layout.
- Many structures intentionally mirror NTFS on-disk records, so field widths and alignment are critical.
- `MAX_PATH` is locally defined as 260 for FCB path buffers.
- Several comments mark speculative or incomplete knowledge, such as `FILE_RECORD_END` and resident indexed flags.
- Prototypes reveal unimplemented or limited areas elsewhere: write support, directory B-tree mutation, sparse/compressed/encrypted handling, large-file limits, and volume mutation.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/ntfs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/rw.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ntfs/rw.c

## Purpose

`rw.c` implements NTFS read and write IRP handling. It maps file objects to FCBs, locates the requested `$DATA` stream, performs attribute reads/writes through `mft.c`, manages sector alignment for reads, grows streams for user writes when allowed, and serializes writes through FCB or volume resources.

## Read Path

`NtfsReadFile`

- Rejects zero-length reads as success.
- Rejects compressed and encrypted files with `STATUS_NOT_IMPLEMENTED`.
- Reads the file's MFT record.
- Finds the requested data stream by `Fcb->Stream`.
- Reports available data streams to debug output if lookup fails.
- Rejects offsets at or beyond end of stream with `STATUS_END_OF_FILE`.
- Clips reads that extend past stream end and zero-fills the caller's trailing buffer.
- Uses a temporary aligned buffer for unaligned sector reads.
- Reads data through `ReadAttribute`.

`NtfsRead`

- Extracts IRP stack, file object, read length, byte offset, and user buffer.
- Calls `NtfsReadFile`.
- Updates synchronous file-object current byte offset and `IoStatus.Information` on success.

## Write Path

`NtfsWriteFile`

- Rejects zero-length writes with a null buffer as success and non-null buffer as invalid.
- Rejects compressed files.
- Reads the target file record and finds the requested data stream.
- If the write extends the stream:
  - Allows growth only for normal, non-volume, non-paging writes.
  - Calls `SetAttributeDataLength`.
  - Gets updated allocation size.
  - Uses the file's best filename attribute to update the parent directory index entry size via `UpdateFileNameRecord`.
- Rejects disallowed extension attempts with `STATUS_ACCESS_DENIED`.
- Writes through `WriteAttribute`.
- Treats short successful writes as `STATUS_UNEXPECTED_IO_ERROR`.

`NtfsWrite`

- Rejects writes to the main filesystem device object.
- Resolves `FILE_WRITE_TO_END_OF_FILE`.
- Rejects non-volume writes whose byte offset uses the high 32 bits.
- Enforces sector alignment for paging, noncached, volume, and no-intermediate-buffering writes.
- Rejects zero-length writes with no user/MDL buffer as success, otherwise invalid.
- Acquires the volume directory resource for volume writes, paging resource for paging I/O, or FCB main resource for ordinary writes.
- Rejects asynchronous file writes as not implemented.
- Gets and locks the user buffer.
- Calls `NtfsWriteFile`.
- Updates synchronous current byte offset, priority boost, and `IoStatus.Information`.

## Integration

- Uses `ReadFileRecord`, `FindAttribute`, `ReadAttribute`, `WriteAttribute`, `SetAttributeDataLength`, and `UpdateFileNameRecord` from `mft.c`.
- Uses `AttributeDataLength` and `AttributeAllocatedLength` to compute stream bounds and allocation.
- Uses FCB state and compression/encryption predicates from `fcb.c`.
- Uses buffer helpers from `misc.c`.
- Relies on `ntfs.h` contracts for IRP context, FCB, and VCB structures.

## Notable Behavior and Risks

- Compressed and encrypted files are not supported.
- Large file writes are rejected when the high 32 bits of the byte offset are nonzero.
- Async writes are not supported.
- Cached writes, file locks, page-file writes, transactions, and timestamp updates are marked TODO or absent.
- The stream-extension path updates only the best filename/hardlink, with a TODO to update every filename attribute and hardlink.
- In the failure path after `FindAttribute` fails, the code calls `ReleaseAttributeContext(DataContext)` even though `DataContext` may not have been initialized by a failed lookup.
- Read failure handling treats a zero-byte `ReadAttribute` result as failure but returns the existing `Status`, which is still initialized to success in that branch.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/rw.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/volinfo.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ntfs/volinfo.c

## Purpose

`volinfo.c` implements NTFS free-space accounting, cluster allocation from `$Bitmap`, query-volume-information IRPs, and the unsupported set-volume-information path.

## Cluster Bitmap Functions

`NtfsGetFreeClusters`

- Allocates a file-record buffer and reads system file `$Bitmap`.
- Finds `$Bitmap::$DATA`.
- Allocates a sector-rounded bitmap buffer.
- Reads the bitmap attribute sector by sector.
- Initializes an `RTL_BITMAP` over `DeviceExt->NtfsInfo.ClusterCount`.
- Returns `RtlNumberOfClearBits`.
- Returns zero on allocation, read, or attribute lookup failures.

`NtfsAllocateClusters`

- Reads `$Bitmap::$DATA`.
- Caps bitmap data size to 32-bit addressable length.
- Builds an `RTL_BITMAP` over volume clusters.
- Fails with `STATUS_DISK_FULL` if clear-bit count is below requested clusters.
- Tries to allocate one contiguous clear run at or after `FirstDesiredCluster`.
- If that fails, returns the next forward clear run or the longest clear run.
- Writes the modified bitmap attribute back through `WriteAttribute`.
- Does not yet observe the NTFS MFT reservation zone.

## Query Volume Information

`NtfsGetFsVolumeInformation`

- Validates output buffer size.
- Returns VPB serial number and volume label.
- Fills dummy volume creation time of zero and `SupportsObjects = FALSE`.

`NtfsGetFsAttributeInformation`

- Reports:
  - `FILE_CASE_PRESERVED_NAMES`
  - `FILE_UNICODE_ON_DISK`
  - `FILE_READ_ONLY_VOLUME`
- Maximum component name length: 255.
- Filesystem name: `NTFS`.

`NtfsGetFsSizeInformation`

- Returns free clusters via `NtfsGetFreeClusters`.
- Returns total clusters, sectors per allocation unit, and bytes per sector from `NtfsInfo`.

`NtfsGetFsDeviceInformation`

- Reports `FILE_DEVICE_DISK` and the mounted device object's characteristics.

`NtfsQueryVolumeInformation`

- Acquires `DeviceExt->DirResource` shared, or queues if it cannot wait.
- Zeroes the caller's system buffer.
- Dispatches `FileFsVolumeInformation`, `FileFsAttributeInformation`, `FileFsSizeInformation`, and `FileFsDeviceInformation`.
- Releases the resource and sets `IoStatus.Information` from consumed buffer length on success.

`NtfsSetVolumeInformation`

- Always returns `STATUS_NOT_SUPPORTED`.

## Integration

- Uses MFT and attribute helpers from `mft.c` to read/write `$Bitmap`.
- Supplies `NtfsAllocateClusters` to nonresident attribute growth in `mft.c`.
- Uses `NtfsMarkIrpContextForQueue` from `ntfs.h` when query-volume work cannot acquire the volume resource immediately.

## Notable Behavior and Risks

- Free-space counting is explicitly noted as underoptimized.
- `$Bitmap` reads are manually sector-looped in `NtfsGetFreeClusters`.
- Cluster allocation rewrites the whole bitmap attribute after setting bits.
- `NtfsAllocateClusters` checks enough total free clusters before choosing a run, but may return a smaller run than requested when no contiguous run exists.
- The reported filesystem attributes always include `FILE_READ_ONLY_VOLUME`, even though experimental write support can be enabled globally.
- Set-volume information is entirely unsupported.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/volinfo.c -->