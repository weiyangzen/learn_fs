# Group Research: group_1708_reactos_sources_windows_reactos_drivers_filesystems_udfs_udf_info_u_4afb5fed0d66

Scope checked against `Docs/research_subset_a.md`. Both listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/udf_info.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/udf_info.cpp

## Purpose

`udf_info.cpp` implements core UDF filesystem metadata operations for the ReactOS UDFS driver. It is the high-level file/object layer above extent mapping, allocation, directory indexing, and raw sector I/O. The file handles UDF filename encoding, DOS-compatible name mangling, descriptor tag generation and validation, File Entry and File Identifier construction, open/create/delete/rename/hard-link operations, stream directories, file resizing and flushing, VAT loading/recording for virtual rewritable media, and CRC helpers.

This implementation is heavily stateful. Most routines operate on `PVCB`, `PUDF_FILE_INFO`, `PUDF_DATALOC_INFO`, `EXTENT_INFO`, `DIR_INDEX_HDR`, and on-disk UDF descriptor structures from `ecma_167.h`. It updates both in-memory state (`Dloc`, `DirIndex`, linked `FileInfo` chains, modification flags) and on-disk metadata via helpers such as `UDFWriteExtent`, `UDFResizeExtent`, `UDFBuildAllocDescs`, `UDFSetUpTag`, and `UDFFlushFI`.

## Major Functional Areas

### Unicode, DOS Names, and CRCs

The file implements UDF compressed Unicode conversion:

- `UDFDecompressUnicode` converts CS0 compressed UDF names to `UNICODE_STRING`, supporting 8-bit and 16-bit compression IDs and optionally returning the CRC of the compressed payload.
- `UDFCompressUnicode` converts `UNICODE_STRING` to CS0 bytes, choosing 8-bit compression when all characters fit and 16-bit otherwise.
- `UDFIsIllegalChar` checks DOS-illegal characters, with x86 assembly and generic C variants.
- `UDFDOSName`, `UDFDOSName100`, `UDFDOSName200`, and `UDFDOSName201` implement OSTA/UDF revision-specific DOS 8.3 name mangling, including illegal-character replacement, truncation, extension selection, and CRC suffix generation.
- `crc32`, `UDFUnicodeCksum`, `UDFUnicodeCksum150`, and `UDFCrc` provide checksum routines used by name mangling and descriptor tag validation.

`UDFDOSName` dispatches based on `Vcb->CurrentUDFRev`, with optional OS-native DOS-name generation outside console builds.

### Tagged Descriptor and File Entry Handling

`UDFReadTagged` reads one block from disk and validates UDF descriptor tags by checking tag location, tag checksum, descriptor version, and descriptor CRC. It returns `STATUS_CRC_ERROR`, `STATUS_FILE_CORRUPT_ERROR`, or `STATUS_SUCCESS` depending on validation.

`UDFReadFileEntry` reads a tagged descriptor at an ICB address and requires it to be either `TID_FILE_ENTRY` or `TID_EXTENDED_FILE_ENTRY`.

Write-side descriptor construction is guarded by `#ifndef UDF_READ_ONLY_BUILD`:

- `UDFSetUpTag` fills descriptor version, tag location, serial number, descriptor CRC, and tag checksum.
- `UDFBuildFileEntry` allocates FE space, stores a `Dloc`, initializes a standard or extended FE, sets ICB strategy/type/default ownership fields, and marks the FE modified.
- `UDFBuildFileIdent` compresses the supplied name, validates UDF name length, allocates a dword-aligned File Identifier Descriptor, fills its ICB reference, version, implementation-use length, and compressed filename payload.
- `UDFLoadExtInfo` interprets FE allocation descriptors through `UDFReadMappingFromXEntry`; if none are present but the FE carries inline data, it falls back to mapping the FE’s own extent. It sets file data length from standard or extended FE `informationLength`.

### File Size, Link Count, Unique ID, and Counters

The file provides small accessors and mutators for FE fields:

- `UDFSetFileSize`, `UDFGetFileSize`, and `UDFSetFileSizeInDirNdx` synchronize FE `informationLength` and cached directory-index size fields.
- `UDFSetAllocDescLen` updates `lengthAllocDescs`, including a Windows 2000 compatibility mode that may use `DataLoc.Length`.
- `UDFChangeFileLinkCount`, `UDFGetFileLinkCount`, and optional `UDFSetFileLinkCount` manage FE link counts, with special handling for UDF 2.0 stream-directory semantics.
- `UDFAssingNewFUID`, `UDFSetFileUID`, and `UDFGetFileUID` manage UDF unique IDs and mirror the low UID bits into FileIdent implementation-use data.
- `UDFChangeFileCounter` updates `Vcb->numFiles` or `Vcb->numDirs`.
- `UDFSetEntityID_imp_` fills implementation EntityID suffixes for WinNT.
- `UDFReadEntityID_Domain` reads domain suffix revision and read-only flags, updating `Vcb->CurrentUDFRev`, volume read-only flags, and user-visible flags.

### Open, Close, Cleanup, and Reference Management

`UDFOpenFile__` is the main file-open path for directory children. It can open by name or by directory index. It:

1. Finds the target `DIR_INDEX_ITEM`, unless an index is supplied.
2. Reuses an already-open `FileInfo` when present.
3. Handles hard-link or parallel-parent cases by finding or cloning a linked `FileInfo`.
4. Reads the FileIdent from the parent directory extent.
5. Stores or reuses a `Dloc` keyed by FE physical LBA.
6. Reads the FE, builds FE/data/allocation mappings, shrinks the FE cache to actual FE length, and notes stream-directory presence.
7. Builds a directory index for directory files and optionally packs directories with too many deleted entries.
8. References the opened file and releases the data-location lock.

`UDFOpenRootFile__` performs the same initialization for root-like objects whose FE location is already known, including root directory, stream directory, and VAT file opens.

`UDFCloseFile__` decrements references, updates parent open counts, repairs `parentICBLocation` when needed, flushes directory preallocation charges, flushes FE and FI metadata when the last link reference is gone, and applies recovery marking if FE flush fails.

`UDFCleanUpFile__` releases memory and tree links after all references are gone. It is careful about:

- open counts, FCB references, and linked/parallel FileInfo chains;
- stream directory back-pointers;
- child directory entries still pointing at this object;
- whether to keep or free a shared `Dloc`;
- freeing directory-index names, FE/data/allocation mappings, FileIdent buffers, and Dloc objects;
- preserving shared Dloc state for hard links or OS references.

The cleanup logic is one of the highest-risk areas because it mutates several pointer graphs: parent directory index entries, stream directory pointers, linked `FileInfo` rings, `Dloc->LinkedFileInfo`, and OS-specific FCB/list pointers.

### Create, Delete, Rename, Hard Link

`UDFCreateFile__` creates or reuses a FileIdent and allocates a zero-sized in-ICB FE. It checks for existing live/deleted names, supports undeleting a matching deleted FileIdent, appends or reuses directory-index entries, aligns FileIdent implementation-use space to avoid too-small sector tails, initializes the FE and `DataLoc`, writes/zeros FE storage where appropriate, sets default attributes and timestamps, flushes metadata, and marks the FileIdent live only near the end.

`UDFUnlinkFile__` marks FileIdent entries deleted, decrements link counts, checks open/reference counts, handles non-empty directory rejection, manages stream directory deletion, zeroes FileIdent ICBs for deleted entries when freeing space, unlinks Dlocs, and frees allocation once link count reaches zero.

`UDFUnlinkAllFilesInDir` recursively opens and deletes every non-dot entry in a directory, refusing to proceed if any child already has an open `FileInfo`.

`UDFRenameMoveFile__` implements rename/move as a multi-phase operation:

1. Handle case-only rename in the same directory by replacing compressed name bytes and hash entry.
2. Create a destination FileIdent/FE placeholder.
3. Optionally remove an existing destination when replace is allowed.
4. Unlink the source FileIdent without freeing source allocation.
5. Transfer FileIdent ICB, characteristics, directory-index location, attributes, and parent linkage from source to destination.
6. Free the temporary destination FE and keep the original Dloc/FileInfo.
7. Return whether replacement recovery occurred through the `Replace` flag.

`UDFHardLinkFile__` is similar to rename’s destination creation, but it keeps both FileIdents and points the new one at the existing FE. It increments link count, marks directory-index entries linked, assigns a new FileIdent unique ID, removes the temporary FE allocation, shares the source `Dloc`, inserts the new `FileInfo` into the linked chain, and closes/cleans the temporary object.

`UDFPretendFileDeleted__` hides an opened file from normal name lookup by setting `UDF_FI_FLAG_FI_INTERNAL` and dropping its cached name, after consulting OS-specific permission checks.

### File Write, Resize, Directory Record, and Flush

`UDFWriteFile__` writes data through `Dloc->DataLoc`. It handles three cases:

- Write entirely inside recorded length: direct `UDFWriteExtent`.
- Write inside allocated but not recorded space: extend logical size, maybe mark allocation descriptors modified, then write.
- Write beyond allocation: reject direct writes, save in-ICB data if needed, convert allocation mode out of in-ICB, grow the extent with directory preallocation when suitable, roll back on failure, restore old inline data, then write user data and mark metadata modified.

`UDFResizeFile__` grows by calling `UDFWriteFile__` with zero length at the target offset. For truncation it may convert small files back into in-ICB storage, freeing external data/allocation mappings and moving retained bytes into the FE tail. Larger truncations call `UDFResizeExtent`, mark data/allocation descriptors modified, and update FE file size.

`UDFRecordDirectory__` converts a zero-sized file into a directory by setting FileIdent and ICB directory flags, building the parent-directory FileIdent entry, writing it into the new directory data stream, updating file/dir counters, and indexing the resulting directory.

`UDFPadLastSector` zero-fills the tail of the final sector of an extent.

`UDFFlushFE` is the main FE flush routine. It retags directory entries, rebuilds allocation descriptors when data/allocation mappings are modified, writes allocation descriptors, updates `lengthAllocDescs`, sets the FE tag, writes the FE, and can relocate the FE if the current block is bad or a write returns `STATUS_DEVICE_DATA_ERROR`. FE relocation updates `Dloc`, inline data/allocation mapping base, and parent FileIdent ICB references.

`UDFFlushFI` writes a modified FileIdent back into its parent directory extent. If the directory offset is not yet allocated, it writes one byte to force allocation, recomputes the target LBA, retags the FileIdent, and writes the full descriptor.

`UDFFlushFile__` is the explicit flush wrapper: it optionally trims directory preallocation, flushes FE, retries with full preallocation flush when a lite flush fails, then flushes FI.

### VAT and Virtual Partition Support

`UDFLoadVAT` loads the Virtual Allocation Table in CDR mode. It tries likely FE locations near the end of media, opens the VAT file as a root file, distinguishes UDF 1.50 and 2.00 VAT formats by file type, allocates `Vcb->Vat`, reads the VAT file, initializes identity mappings and free entries, stores initial VAT count, records VAT partition index, re-enables CDR mode, synchronizes free-space bitmap state, and preformats reserved packet areas.

`UDFRecordVAT` writes an updated VAT at session end. It temporarily disables VAT translation, synchronizes free entries from the free-space bitmap, reads the previous VAT image, builds a new VAT image and header, updates previous-VAT pointers, resizes the VAT file if needed, handles in-ICB and external VAT storage separately, relocates modified VAT sectors to next writable addresses, rebuilds allocation mapping for VAT allocation descriptors, updates FE location to the final packet position, flushes the VAT file, and flushes write cache.

`UDFUpdateVAT` updates in-memory VAT entries during writes, mapping requested logical blocks to the current next writable address and extending `VatCount` as needed. It rejects writes to partitions other than the VAT partition.

### Stream Directories and Extended FEs

`UDFCreateStreamDir__` creates a UDF 2.0 stream directory associated with an existing file. It checks revision support, rejects streams under stream directories, converts the parent FE to extended form if needed, creates a root-like stream-dir FE, records it as a directory, updates the parent extended FE’s `streamDirectoryICB`, shares the parent unique ID, sets stream flags, and links `Dloc->SDirInfo`.

`UDFOpenStreamDir__` opens an existing stream directory by using the parent extended FE `streamDirectoryICB`; it also handles already-open stream directories and parallel `FileInfo` cases.

`UDFConvertFEToNonInICB` forces inline data out to external short or long allocation descriptors by saving inline data, growing allocation, changing ICB allocation mode, restoring original length, writing saved data, and marking allocation/data descriptors modified.

`UDFConvertFEToExtended` converts a standard FE to an extended FE, copying fields and extended attributes, changing FE/data/allocation offsets, and preserving in-ICB data by temporarily reading, truncating, resizing, and rewriting it.

## Key Dependencies

This file depends on the broader UDFS subsystem for lower-level operations and policy:

- Raw and cached I/O: `UDFReadSectors`, `UDFWriteData`, `UDFReadExtent`, `UDFWriteExtent`, `UDFZeroExtent`, `WCache*`.
- Extent and allocation management: `UDFResizeExtent`, `UDFExtentToMapping`, `UDFReadMappingFromXEntry`, `UDFBuildAllocDescs`, `UDFMarkSpaceAsXXX`, `UDFAllocateFESpace`, `UDFFreeFESpace`, `UDFFlushFESpace`.
- Directory index management: `UDFIndexDirectory`, `UDFFindFile`, `UDFDirIndex*`, `UDFBuildHashEntry`, `UDFPackDirectory__`, `UDFReTagDirectory`.
- Dloc tracking: `UDFStoreDloc`, `UDFAcquireDloc`, `UDFReleaseDloc`, `UDFRemoveDloc`, `UDFUnlinkDloc`, `UDFFreeDloc`, `UDFRelocateDloc`, linked/parallel FileInfo helpers.
- OS policy hooks: `UDFDoesOSAllowFileToBeTargetForRename__`, `UDFDoesOSAllowFileToBeTargetForHLink__`, `UDFDoesOSAllowFilePretendDeleted__`, `UDFRemoveFileId__`, attribute and time conversion/update helpers.
- UDF media constants and structures from `ecma_167.h`, `udf_rel.h`, and the rest of the UDFS driver.

## State and Invariants

Important invariants enforced or assumed:

- `FileInfo` must usually pass `ValidateFileInfo`.
- FE and FileIdent changes are tracked through `UDF_FE_FLAG_FE_MODIFIED`, `UDF_FI_FLAG_FI_MODIFIED`, and `DataLoc/AllocLoc/FELoc.Modified`.
- `DataLoc.Length` is logical file length, while mapping length may include allocated but not recorded/preallocated space.
- In-ICB files use the FE’s own extent as data mapping with `DataLoc.Offset == FileEntryLen`.
- Directory index slots 0 and 1 are special current/parent entries; deletion usually rejects them.
- `Dloc` objects are shared by hard links and must survive while link references, common FCBs, or linked FileInfos exist.
- Stream directories require extended FEs and UDF write revision >= 2.00.
- VAT mode temporarily disables `Vcb->Vat` while recording to avoid recursive remapping.

## Risks and Notable Edge Cases

- `UDFLoadVAT` allocates VAT header buffers but appears to read fields such as `lengthHeader`, revision fields, and counters before filling the buffer from disk; in the visible code, the VAT 2.00 `Buf` is also freed before later field reads. This is a high-risk correctness issue unless hidden macros or platform behavior compensate elsewhere.
- `UDFConvertFEToExtended` copies allocation descriptor bytes with a source expression that appears to point into `ExFileEntry` rather than the old `FileEntry`, so allocation descriptor preservation may be wrong for non-empty descriptor areas.
- `UDFReadTagged` treats `descCRCLength + sizeof(tag) > Vcb->BlockSize` as part of a success condition. That may be intentional tolerance, but it is suspicious because an over-block descriptor CRC length normally indicates corruption.
- Rename and hard-link operations create temporary FEs then transplant metadata. Failures midway require careful cleanup; the code contains many recovery paths but still has broad pointer-state risk.
- Cleanup and stream-directory logic mutates linked lists and back-pointers across parent objects and Dlocs. Refcount bugs here can leak Dlocs or leave directory-index `FileInfo` pointers stale.
- Many write paths are compiled out under `UDF_READ_ONLY_BUILD`; consumers must not assume create/rename/VAT-record paths exist in read-only builds.
- There are several x86/MSVC assembly fast paths with generic fallbacks. Behavior should be verified on non-MSVC or non-x86 builds because ReactOS may build with different compilers.
- Directory FileIdent layout logic pads implementation-use bytes to avoid too-small sector tails; off-by-one or alignment regressions here can make directories unreadable.
- FE relocation on bad blocks updates multiple mappings and FileIdent references. It needs tests for in-ICB and non-in-ICB files.

## Testing Guidance

Useful tests around this file would include:

- CS0 8-bit and 16-bit filename round-trips, empty names, max-length names, and CRC output.
- DOS name mangling for UDF 1.00, 1.50, 2.00, and 2.01, including illegal characters, spaces, trailing dots, multiple dots, long basename/extension, and `.`/`..`.
- Descriptor tag validation for good tags, bad checksum, bad version, bad location, bad descriptor CRC, zero descriptor CRC, and excessive descriptor CRC length.
- Create/open/close/delete lifecycle for regular files, directories, hard links, deleted FileIdent reuse, and undelete-on-create behavior.
- Rename with and without replacement, same-directory case-only rename, cross-directory rename, and rollback after simulated allocation/write failures.
- Resize across in-ICB to external allocation boundaries and back to in-ICB truncation.
- Directory preallocation trimming during close/flush.
- Stream directory create/open/delete paths and FE conversion to extended form.
- VAT load/record/update on virtual UDF 1.50 and 2.00 partitions, including packet-boundary writes and free-space bitmap synchronization.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/udf_info.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/udf_info.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/udf_info.h

## Purpose

`udf_info.h` is the private support API header for the UDFS metadata layer. It declares the functions implemented in `udf_info.cpp` and neighboring UDF modules, plus inline wrappers and macros for common file, extent, directory-index, bitmap, allocation, stream, and verification-cache operations.

The header includes `ecma_167.h`, `osta_misc.h`, `udf_rel.h`, and `wcache.h`, so it bridges UDF on-disk descriptor definitions, OSTA Unicode helpers, driver-local state definitions, and write-cache/verification support.

## API Surface

### Extent and Mapping Operations

The header declares operations for translating and using UDF extents:

- `UDFExtentOffsetToLba`, `UDFLocateLbaInExtent`, `UDFGetExtentLength`, `UDFGetMappingLength`.
- `UDFReadExtent`, `UDFWriteExtent`, `UDFZeroExtent`, and `UDFReadExtentLocation`.
- `UDFMergeMappings`, `UDFExtentToMapping`, `UDFPackMapping`, and `UDFUnPackMapping`.
- Allocation descriptor parsers: `UDFShortAllocDescToMapping`, `UDFLongAllocDescToMapping`, `UDFExtAllocDescToMapping`, `UDFReadMappingFromXEntry`.
- Conversion and mutation helpers for allocation state: `UDFMarkAllocatedAsRecorded`, `UDFMarkNotAllocatedAsAllocated`, `UDFMarkAllocatedAsNotXXX`, and wrappers for sparse/unrecorded allocation transitions.

These APIs establish that UDFS represents file storage as `EXTENT_INFO` containing a mapping array, logical length, offset, flags, and modification state.

### Directory Index and File Lookup

Directory operations include:

- `UDFDirIndexGetFrame`, `UDFDirIndexFree`, `UDFDirIndexGrow`, `UDFDirIndexTrunc`.
- `UDFDirIndexInitScan`, `UDFDirIndexScan`, `UDFIndexDirectory`.
- `UDFFindFile` and inline `UDFFindFile__`.
- `UDFGetDirIndexByFileInfo`, `UDFIsDirEmpty`, `UDFDirIndexGetLastIndex`.
- `UDFDirIndex` inline access, with x86 optimized declaration and generic frame-based lookup.

The directory index is frame-based unless `UDF_LIMIT_DIR_SIZE` is enabled. `UDF_DIR_INDEX_FRAME_SH` is 9 normally and 7 in limited/demo builds. `AlignDirIndex` aligns directory index counts to 32-entry granularity.

### File Entry, File Ident, and File Lifecycle APIs

The header declares the main file-object routines:

- FE/FileIdent construction and loading: `UDFReadFileEntry`, `UDFBuildFileEntry`, `UDFBuildFileIdent`, `UDFLoadExtInfo`, `UDFSetUpTag`.
- File lifecycle: `UDFOpenFile__`, `UDFOpenRootFile__`, `UDFCreateFile__`, `UDFCreateRootFile__`, `UDFCloseFile__`, `UDFCleanUpFile__`, `UDFUnlinkFile__`, `UDFUnlinkAllFilesInDir`.
- Data operations: inline `UDFReadFile__`, inline `UDFReadFileLocation__`, `UDFWriteFile__`, `UDFZeroFile__`, `UDFSparseFile__`, `UDFResizeFile__`, `UDFPadLastSector`.
- Metadata flush: `UDFFlushFE`, `UDFFlushFI`, `UDFFlushFile__`, and `UDFIsFlushed`.
- Rename/link/directory conversion: `UDFRenameMoveFile__`, `UDFHardLinkFile__`, `UDFRecordDirectory__`, `UDFPackDirectory__`, `UDFReTagDirectory`, `UDFPretendFileDeleted__`.
- Stream support: `UDFCreateStreamDir__`, `UDFOpenStreamDir__`, and stream-state macros.

The header also defines cleanup return flags: `UDF_FREE_NOTHING`, `UDF_FREE_FILEINFO`, and `UDF_FREE_DLOC`.

### Allocation, Free Space, and Partition Helpers

Allocation and free-space APIs include:

- `UDFGetBitmapLen`, `UDFFindMinSuitableExtent`, `UDFAllocFreeExtent`.
- `UDFMarkSpaceAsXXXNoProtect`, `UDFMarkSpaceAsXXX`, and optional `UDFCheckSpaceAllocation`.
- Allocation-state constants `AS_FREE`, `AS_USED`, `AS_DISCARDED`, and `AS_BAD`.
- FE allocation helpers: `UDFAllocateFESpace`, `UDFFreeFESpace`, `UDFFlushFESpace`, `UDFFreeFileAllocation`.
- Cached allocation helpers: `UDFGetCachedAllocation`, `UDFStoreCachedAllocation`, `UDFFlushAllCachedAllocations`.
- Partition translation and bounds: `UDFPhysLbaToPart`, `UDFPartLbaToPhys`, `UDFGetPartNumByPhysLba`, `UDFPartStart`, `UDFPartEnd`, `UDFPartLen`, `UDFGetPartNumByPartNdx`.
- Free/zero bitmap descriptor support: `UDFAddXSpaceBitmap`, `UDFDelXSpaceBitmap`, `UDFBuildFreeSpaceBitmap`, `UDFPrepareXSpaceBitmap`, `UDFUpdateXSpaceBitmaps`.

Several macros add optional tracking parameters when `UDF_TRACK_ONDISK_ALLOCATION` or `UDF_TRACK_ALLOC_FREE_EXTENT` is enabled, using `UDF_BUG_CHECK_ID` and `__LINE__`.

### Volume, Mount, VAT, and Descriptor Sequence APIs

The header exposes volume-recognition and mount-time functions:

- `UDFFindAnchor`, `UDFFindVRS`, `UDFReadTagged`.
- `UDFLoadPVolDesc`, `UDFLoadLogicalVolInt`, `UDFLoadLogicalVol`, `UDFLoadPartDesc`.
- `UDFReadVDS`, `UDFProcessSequence`, `UDFVerifySequence`, `UDFLoadFileset`, `UDFLoadPartition`, `UDFGetDiskInfoAndVerify`.
- Update/unmount helpers: `UDFUpdatePartDesc`, `UDFUpdateLogicalVolInt`, `UDFUpdateUSpaceDesc`, `UDFUpdateVDS`, `UDFUmount__`, `UDFUpdateVolIdent`.
- VAT support: `UDFLoadVAT`, `UDFRecordVAT`, `UDFModifyVAT`, `UDFUpdateVAT`.

The `UDFGetLVIDiUse` macro computes the implementation-use structure address inside a Logical Volume Integrity Descriptor after the per-partition free/size arrays.

### Dloc and Linked FileInfo Management

The header declares the shared data-location table API:

- `UDFFindDloc`, `UDFFindFreeDloc`, `UDFAcquireDloc`, `UDFReleaseDloc`.
- `UDFStoreDloc`, `UDFRemoveDloc`, `UDFUnlinkDloc`, `UDFFreeDloc`, `UDFRelocateDloc`, `UDFReleaseDlocList`.
- `UDFLocateParallelFI`, `UDFLocateAnyParallelFI`, and `UDFInsertLinkedFile`.

These functions support hard links, stream directories, parallel opens, and shared FE/data mapping state.

### Name, Attribute, Link, UID, and Counter Helpers

The header declares:

- `UDFDecompressUnicode`, `UDFCompressUnicode`, `UDFBuildHashEntry`.
- DOS name translation variants: `UDFDOSName`, `UDFDOSName201`, `UDFDOSName200`, `UDFDOSName100`, and `UDFDOSName__`.
- `UDFUnicodeInString`, `UDFIsIllegalChar`, `UDFUnicodeCksum`, `UDFUnicodeCksum150`, `UDFCrc`, `crc32`.
- File size and allocation descriptor length accessors: `UDFSetFileSize`, `UDFSetFileSizeInDirNdx`, `UDFGetFileSize`, `UDFGetFileSizeFromDirNdx`, `UDFSetAllocDescLen`.
- Link-count helpers: `UDFChangeFileLinkCount`, `UDFIncFileLinkCount`, `UDFDecFileLinkCount`, `UDFGetFileLinkCount`, optional `UDFSetFileLinkCount`.
- EntityID and UID helpers: `UDFSetEntityID_imp_`, `UDFSetEntityID_imp`, `UDFReadEntityID_Domain`, `UDFSetFileUID`, `UDFGetFileUID`.
- Volume counters: `UDFChangeFileCounter`, `UDFIncFileCounter`, `UDFDecFileCounter`, `UDFIncDirCounter`, `UDFDecDirCounter`.

### FileInfo and Stream Macros

Important inline/macro policies:

- `UDFIsDeleted` checks `FILE_DELETED`.
- `UDFIsADirectory` treats either a loaded directory index or a FileIdent `FILE_DIRECTORY` bit as directory evidence.
- `UDFGetFileAllocationSize` returns mapped data allocation length or one logical block.
- `UDFReferenceFile__`, `UDFReferenceFileEx__`, and `UDFDereferenceFile__` update `FileInfo->RefCount`, `Dloc->LinkRefCount`, and parent open counts.
- `UDFSetFileAllocMode__`, `UDFGetFileAllocMode__`, and `UDFGetFileICBAllocMode__` manipulate allocation-mode bits.
- `UDFStreamsSupported` and `UDFNtAclSupported` require `maxUDFWriteRev >= 0x0200`.
- `UDFIsAStreamDir`, `UDFHasAStreamDir`, `UDFIsAStream`, and `UDFIsSDirDeleted` test stream-directory FE flags.

### Bitmap Bit Operations

The header defines bit operations for free-space, bad-space, and zero-space bitmaps:

- On x86, external optimized routines are declared for `UDFGetBit__`, `UDFSetBit__`, `UDFSetBits__`, `UDFClrBit__`, and `UDFClrBits__`.
- On generic builds, macros directly manipulate 32-bit bitmap words.
- Semantic aliases invert or reuse raw bits for used/free state: `UDFGetUsedBit` is `!UDFGetBit`, while `UDFGetFreeBit` is `UDFGetBit`.

Optional allocation-owner tracking macros are enabled only under debug/console plus `UDF_TRACK_ONDISK_ALLOCATION_OWNERS`.

### Verification Cache API

The bottom of the header declares a verification/cache layer:

- Constants: `UDF_MAX_VERIFY_CACHE`, `UDF_VERIFY_CACHE_LOW`, `UDF_VERIFY_CACHE_GRAN`, `UDF_SYS_CACHE_STOP_THR`.
- I/O flags: `PH_FORGET_VERIFIED`, `PH_READ_VERIFY_CACHE`, `PH_KEEP_VERIFY_CACHE`.
- Lifecycle and I/O: `UDFVInit`, `UDFVRelease`, `UDFVWrite`, `UDFVRead`, `UDFVForget`, `UDFVVerify`, `UDFVFlush`.
- `UDFVIsStored` inline checks whether a logical block is present in `Vcb->VerifyCtx.StoredBitMap`.
- `UDFCheckArea` verifies an LBA range.

## Compile-Time Shape

The header is highly conditional:

- `UDF_READ_ONLY_BUILD` removes many mutating write/create/delete APIs from implementation but declarations are still organized around the full writable engine.
- `_X86_` enables assembly or external optimized helpers for directory index and bitmap operations.
- `UDF_LIMIT_DIR_SIZE` changes directory index frame size and layout.
- `UDF_CHECK_DISK_ALLOCATION`, `UDF_TRACK_ONDISK_ALLOCATION`, `UDF_TRACK_ALLOC_FREE_EXTENT`, `UDF_TRACK_EXTENT_TO_MAPPING`, `UDF_TRACK_FS_STRUCTURES`, and owner-tracking macros add diagnostics and source-location tracking.
- `_CONSOLE`, `UDF_DBG`, and `DBG` alter assertions, address checks, and inline-vs-macro wrappers.

## Integration Notes

This header is not a standalone public API. It assumes the full UDFS internal type universe from `udf.h` and included headers: `PVCB`, `PUDF_FILE_INFO`, `PUDF_DATALOC_INFO`, `PEXTENT_INFO`, `PEXTENT_MAP`, UDF descriptor structures, directory-index structures, memory allocation helpers, status macros, debug macros, and Windows kernel-style types.

The declarations show that `udf_info.cpp` is only one part of the `udf_info` module. Many declared functions are implemented in sibling files such as allocation, extent, mount, remap, and directory-tree sources.

## Risks and Review Points

- The many macro wrappers hide side effects, especially reference counting and allocation tracking. Callers must know whether a helper mutates parent open counts, Dloc link counts, or bitmap state.
- Generic bitmap macros evaluate arguments directly and are not type-safe; callers should avoid expressions with side effects.
- `UDFIsADirectory` can return true from either loaded state or on-disk FileIdent flags, which is convenient but can blur incomplete-open and fully-indexed-directory states.
- Reference macros assume `fi`, `fi->Dloc`, and optionally parent pointers are valid; they do not guard nulls.
- Directory index inline access returns `NULL` on out-of-range but relies on correct frame counts and `LastFrameCount`; corrupt or partially initialized indexes can break traversal assumptions.
- Build-configuration divergence is significant. Writable builds, read-only builds, x86 builds, and generic builds can exercise different code paths.
- `UDFGetFileAllocationSize` returns one logical block when no mapping exists, which may be a policy choice but can surprise callers expecting zero allocation for unmapped/empty objects.
- Stream and NT ACL support are revision-gated only by `maxUDFWriteRev`; callers still need to ensure the FE format and volume state support the requested operation.

## Testing Guidance

Tests using this header’s API surface should cover:

- Generic and x86 bitmap operations for aligned and unaligned bit ranges.
- Directory-index frame growth/truncation and index lookup at frame boundaries.
- Reference/dereference macro behavior with and without parent files.
- Allocation tracking macros in debug/tracking builds.
- Read-only build compilation, ensuring mutating paths are either unavailable or return write-protected status.
- Stream capability checks around UDF 1.50, 2.00, and later revisions.
- Verification cache init/read/write/forget/flush flows.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/udf_info.h -->