<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/lsmt/file.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/lsmt/file.cpp

## Purpose
Implements OverlayBD LSMT layered file objects: read-only sealed layers, writable append-only layers, sparse writable layers, warp files with remote data mappings, stacking, compaction, sealing, and merge/open helpers.

## Important APIs, Types, And Functions
Key internal types are `HeaderTrailer`, `CompactOptions`, `LSMTReadOnlyFile`, `LSMTFile`, `LSMTSparseFile`, `LSMTWarpFile`, `parallel_load_task`, and many helpers including `write_header_trailer`, `compact`, `pcopy`, `load_layer_info`, `verify_ht`, `do_load_index`, `load_merge_index`, and `verify_order`. Exports `create_file_rw`, `open_file_rw`, `open_file_ro`, `open_files_ro`, `create_warpfile`, `open_warpfile_rw`, `open_warpfile_ro`, `merge_files_ro`, `stack_files`, `open_file_index`, `open_files_with_merged_index`, and `is_lsmt`.

## Control Flow
New RW files write headers to data/index files and insert mappings on aligned writes. Reads use `foreach_segments` over memory indexes, returning zero-filled holes and reading mapped data from tagged backing files. `close_seal` dumps the RW index into the data file and writes a sealed trailer. `commit`/`flatten` compact valid mappings into a new sealed file, writing header, live data, compressed index, and trailer. `open_file_ro`/`open_file_rw` validate headers/trailers and rebuild memory indexes. `open_files_ro` loads layer indexes in parallel, reverses to top-first order, and merges them. `stack_files` combines a writable upper layer with lower read-only layers via a combo index.

## State And Persistence
LSMT files persist 4 KiB headers/trailers, UUID/parent UUID/user tags, virtual size, data extents, discard mappings, and index arrays of 512-byte-sector `SegmentMapping`s. Runtime state includes memory indexes, backing file vectors, ownership flags, write mutex, group-commit buffer, current RW tag, compact counters, and virtual size.

## Dependencies And Integration Points
Uses Photon `IFile`/virtual file APIs, UUID, aligned memory helpers, Photon threads/mutexes, and index primitives from `index.h`. Provides the C API consumed by OverlayBD layer/image code.

## Risks And Test Signals
All read/write/discard operations require 512-byte alignment, and `set_max_io_size` requires 4 KiB alignment. Header/trailer packed ABI is compatibility-critical. `is_zero_block` currently returns `1` before its real scan, so compaction zero-detection is effectively disabled/incorrectly marked by the current code path. Parallel index loading mutates shared task state with minimal synchronization. Parent UUID order checks can reject invalid stacks. Tests are not in this subset but `lsmt/test` is enabled by CMake. Source size reviewed: 1969 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/lsmt/file.cpp -->
