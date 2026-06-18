# File Research: sources/block-storage/thin-provisioning-tools/src/thin/shrink.rs

## Purpose
Implements thin-pool data-device shrink support. It identifies mapped data blocks above a requested new data-block count, copies those blocks into free ranges below the new limit when requested, and rewrites either XML metadata or binary metadata so mappings point at the new locations and the superblock advertises the smaller data-device size.

## Main Components
- `copy_regions()` opens the data device read/write, wraps it in `VectoredBlockIo`, builds a `SyncCopier`, feeds block-level `CopyOp`s through `CopyOpBatcher`, and runs the copy work in a `ThreadedCopier`.
- `MappingCollector` implements `MetadataVisitor` to split mapped data ranges into `below` and `above` `RangeSet`s relative to the target `nr_blocks`.
- `MappingCollector::get_remaps()` computes gaps below the target size and delegates to shared shrink logic `build_remaps()` to map above-limit ranges into those free gaps.
- `DataRemapper` is another `MetadataVisitor` wrapper. It mutates the streamed superblock `nr_data_blocks` and rewrites affected mapping records through `remap()`.
- `build_remaps_from_metadata()` and `build_remaps_from_xml()` run the collection pass over binary metadata and XML metadata respectively.
- `rewrite_xml()` performs the two-pass XML path.
- `rebuild_metadata()` performs the binary metadata path, reconstructing metadata through `Restorer` and `WriteBatcher`.
- `shrink()` dispatches by `ThinShrinkOptions::binary_mode`.

## Behavior
The shrink algorithm is intentionally two-pass. First it reads all mappings to discover data ranges that are already below the new boundary and data ranges that must move. Ranges crossing the boundary are split: the below portion contributes to occupied space, and the above portion contributes to remap demand. Free gaps inside `0..nr_blocks` become destinations.

If `do_copy` is true, data blocks are physically copied before metadata is rewritten. The data block size comes from metadata as sectors shifted by `SECTOR_SHIFT`. `copy_regions()` expands remap ranges into individual source/destination block operations and batches them into the threaded copy pipeline.

Metadata rewriting preserves thin-device/device/shared-definition traversal structure and changes only:
- the superblock `nr_data_blocks`,
- mapping `data_begin` and `len` values that intersect or exceed the new boundary.

For XML, the input is opened exclusively, the XML superblock is read for block size, the input is seeked back between passes, and output is written through `XmlWriter`. For binary metadata, the input engine reads the superblock, builds and optimizes in-memory metadata, computes remaps by dumping metadata to the collector, then restores remapped metadata into a newly created output engine using a core metadata space map.

## Dependencies and Interactions
This file ties together:
- generic shrink range logic from `crate::shrink::toplevel`,
- thin metadata dump/restore visitor infrastructure,
- XML streaming parser/writer,
- synchronous and vectored IO engines,
- threaded copy infrastructure,
- metadata space-map allocation and `WriteBatcher`.

## Research Notes
The key invariant is that remapped metadata must be consistent with any optional data copy. The file assumes `build_remaps()` can satisfy all above-boundary ranges from free below-boundary gaps; if not, errors propagate before rewriting. `DataRemapper::map()` uses streamed mapping splitting, so large metadata can be transformed without materializing XML records in memory.
