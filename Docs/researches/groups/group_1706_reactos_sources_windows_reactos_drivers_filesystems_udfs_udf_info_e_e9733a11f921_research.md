# Group Research: group_1706_reactos_sources_windows_reactos_drivers_filesystems_udfs_udf_info_e_e9733a11f921

Scope: `Docs/research_subset_a.md` includes `sources/windows/reactos`. All three listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/extent.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/extent.cpp

## Purpose
Implements UDF extent and allocation mapping management for the ReactOS UDFS driver. It converts on-disk allocation descriptors into internal `EXTENT_MAP` arrays, translates file offsets to LBAs, resizes extents, builds allocation descriptor streams for writes, handles sparse/not-recorded extent state transitions, and performs extent-backed read/write/zero operations.

## Key Elements
- `UDFExtentOffsetToLba`, `UDFNextExtentToLba`, `UDFGetExtentLength`, `UDFGetMappingLength`, and `UDFMergeMappings` provide core extent traversal, length accounting, and array manipulation.
- `UDFShortAllocDescToMapping`, `UDFLongAllocDescToMapping`, and `UDFExtAllocDescToMapping` parse short, long, and extended allocation descriptors, including recursive `EXTENT_NEXT_EXTENT_ALLOCDESC` chains.
- `UDFReadMappingFromXEntry` chooses the allocation descriptor format from file-entry/extended-file-entry ICB flags and handles `ICB_FLAG_AD_IN_ICB` by returning an in-entry offset rather than a mapping.
- Write builds are guarded by `#ifndef UDF_READ_ONLY_BUILD`; they include short/long descriptor serialization, optional fragmented allocation descriptor chains, FE-space preallocation, allocation caches, file-allocation cleanup, resize, write, and zero/deallocate paths.
- `UDFResizeExtent` is the main grow/shrink engine. It can grow sparse extents, extend the last physical fragment when adjacent free space exists, allocate new fragments, cache truncated preallocated tails, and normalize in-ICB transitions.
- `UDFMarkAllocatedAsRecorded`, `UDFMarkNotAllocatedAsAllocated`, and `UDFMarkAllocatedAsNotXXX` split and rewrite mapping arrays as data moves between recorded, allocated-not-recorded, and not-allocated-not-recorded states.
- `UDFPackMapping` merges adjacent compatible fragments; `UDFUnPackMapping` expands mappings to one logical block per entry for FE-charge allocation.
- `UDFReadExtent`, `UDFReadExtentLocation`, `UDFIsExtentCached`, `UDFWriteExtent`, and `UDFZeroExtent` bridge extent mappings to the lower block-cache/data I/O layer.

## Dependencies
Uses UDF structures and constants from `udf.h`/ECMA definitions, pool helpers (`MyAllocatePoolTag__`, `MyReallocPool__`, `MyFreePool__`), bitmap/allocation helpers (`UDFAllocFreeExtent`, `UDFMarkSpaceAsXXX`, `UDFCheckSpaceAllocation`), cache helpers (`WCache*`, `UDFIsDataCached`), and physical/logical partition translation helpers (`UDFPartLbaToPhys`, `UDFPhysLbaToPart`, `UDFPartStart`, `UDFPartEnd`).

## Behavior/Risks
This is high-risk write-path code: it mutates allocation bitmaps and extent arrays while preserving UDF extent flags in the upper bits of `extLength`. Alignment is frequently rounded to logical block size and several compatibility paths exist for Windows 2000 and Adaptec DirectCD media. Recursive allocation descriptor parsing is bounded by `ALLOC_DESC_MAX_RECURSE`.

Potential concerns include heavy manual memory ownership, many conditional build paths, several “must never happen” realloc assumptions on truncate, disabled/commented code for extended allocation descriptor building, and a suspicious `UDFLocateLbaInExtent` range predicate that appears inverted for locating an LBA within `[extLocation, extLocation + length)`. Sparse support depends on `ALLOW_SPARSE`; otherwise paths deliberately hit `BrutePoint`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/extent.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/mount.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/mount.cpp

## Purpose
Implements UDF mount, verification, and unmount metadata handling. It discovers anchors and volume recognition sequences, processes main/reserve volume descriptor sequences, loads partition maps and file sets, builds internal free/zero-space bitmaps, loads sparing/VAT-related state, and flushes updated volume metadata on unmount.

## Key Elements
- `UDFFindAnchor` probes expected anchor locations, VAT-related tail locations, and MRW workaround offsets, registering valid anchors and forcing read-only mode when MRW addressing problems are detected.
- `UDFFindVRS` scans the volume recognition sequence for ISO9660, BEA01/TEA01, NSR02, and NSR03 signatures.
- `UDFReadVDS`, `UDFProcessSequence`, and `UDFVerifySequence` scan descriptor sequences, follow multipart `VolDescPtr` chains, and dispatch descriptor-specific load/verify routines.
- `UDFLoadLogicalVol` initializes logical block size, reads UDF domain flags, parses type 1/type 2 partition maps, detects virtual, sparable, and metadata partitions, and loads the logical volume integrity descriptor.
- `UDFLoadPartDesc`, `UDFBuildFreeSpaceBitmap`, `UDFAddXSpaceBitmap`, and verification counterparts populate or validate in-memory allocation/zero bitmaps from partition headers, unallocated/freed space bitmaps, and unallocated-space descriptors.
- `UDFLoadLogicalVolInt` walks LVID chains, keeps the last valid descriptor, imports revision/file/dir counters, and applies partial-damage policy.
- `UDFLoadSparingTable` merges sparing table entries from all advertised table locations and records relocation metadata.
- `UDFFindLastFileSet` follows file-set descriptor chains and `UDFLoadFileset` stores root and system stream ICB locations plus volume identity.
- `UDFUmount__` flushes cached allocations, handles CDR/VAT recording, updates bad-block/non-allocatable state, updates volume labels, VDS bitmaps, sparing tables, and LVID close state.

## Dependencies
Depends on `udf.h`, UDF/ECMA descriptor layouts, dstring helpers in this file plus Unicode compression/decompression elsewhere, extent I/O (`UDFReadExtent`, `UDFWriteExtent`), bitmap helpers, sparing/VAT helpers, write cache helpers, tagged descriptor read/write helpers, and VCB policy/configuration fields.

## Behavior/Risks
Mount behavior is tolerant and policy-driven: corrupt main VDS can fall back to reserve VDS, damaged LVID can trigger read-only, raw-disk, or risky read/write mode, and missing anchors on CD media lead to CDFS/zero-buffer checks. Unmount only writes metadata when the volume is writable and modified.

Risk areas include complex recovery fallbacks, many global VCB side effects, manual pool ownership across SEH blocks, descriptor length trust boundaries, and duplicated load/verify code paths that can drift. The sparing-table merge code is subtle and contains suspicious duplicate-location indexing in the already-processed check. Metadata writeback depends on the internal free-space bitmap accurately reflecting every allocation mutation made elsewhere.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/mount.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/osta_misc.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/osta_misc.h

## Purpose
Defines OSTA/UDF-specific packed metadata structures, identifiers, partition-map types, revision-related suffixes, VAT/sparing layouts, reserved names, and extent flag masks used by the UDFS implementation.

## Key Elements
- Declares `LogicalVolIntegrityDescImpUse` and `ImpUseVolDescImpUse`, which are consumed by mount logic for UDF revision limits, file/dir counts, volume identity, and implementation-use metadata.
- Defines type 2 partition map variants: generic UDF map, virtual partition map, sparable partition map, and UDF 2.5 metadata partition map.
- Provides partition type constants such as `UDF_TYPE1_MAP15`, `UDF_VIRTUAL_MAP15`, `UDF_VIRTUAL_MAP20`, `UDF_SPARABLE_MAP15`, and `UDF_METADATA_MAP25`.
- Defines VAT 1.5 and VAT 2.0 layouts, sparing entries/tables, domain/UDF/implementation identifier suffixes, entity identifier strings, OS class/id constants, name/path/label limits, and reserved UDF filenames/system stream names.
- Defines `UDF_EXTENT_LENGTH_MASK`, `UDF_EXTENT_FLAG_MASK`, and `UDF_EXTENT_FLAG_ERASED`, which are central to `extent.cpp` because extent state is encoded in the high bits of `extLength`.

## Dependencies
Includes `ecma_167.h` and uses packed layout via `#pragma pack(push, 1)`, so these definitions are intended to match on-disk UDF structures byte-for-byte. It also depends on `VER_STR_PRODUCT_NAME` for the developer identifier string.

## Behavior/Risks
This header is structural rather than executable, but layout correctness is critical: packing, fixed-size arrays, and identifier strings directly affect disk parsing and serialization. Any change to these definitions can break compatibility with UDF media, especially VAT, sparable, metadata partition, and implementation-use descriptors.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/osta_misc.h -->