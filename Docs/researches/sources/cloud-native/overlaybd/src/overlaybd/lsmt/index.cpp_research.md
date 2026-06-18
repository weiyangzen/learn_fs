# sources/cloud-native/overlaybd/src/overlaybd/lsmt/index.cpp

## Purpose
Implements the in-memory mapping indexes used by OverlayBD's log-structured mapped table layer. It provides immutable read indexes, writable level-0 indexes, combo indexes that overlay writable mappings on read-only backing mappings, merge/compression helpers, and an optional linearized B+tree lookup accelerator.

## Important APIs and Types
Key concrete types are `Index`, `IndexLBPT`, `LevelIndex`, `Index0`, and `ComboIndex`. Factory exports include `create_memory_index0`, `create_memory_index`, `create_level_index`, `create_combo_index`, `merge_memory_indexes`, `compress_raw_index`, and `compress_raw_index_predict`. Helpers validate mapping order and mapped-offset ranges, trim lookup edge mappings, and choose AVX-512 accelerated inner search on x86_64 when supported.

## Control Flow
Read-only `Index::lookup` binary-searches sorted `SegmentMapping` ranges, copies intersecting mappings, and trims the first/last result to the requested `Segment`. `Index0::insert` mutates a `std::set` by splitting or erasing overlapping old mappings before inserting the new mapping. `ComboIndex::lookup` walks front mappings and fills gaps from the backing index. `merge_indexes` recursively gives newer layers precedence, tags merged mappings by source layer, and trims boundary ranges.

## State and Persistence
The file owns only memory state: vectors, sets, optional raw buffers, B+tree nodes, allocation counters, virtual size, and ownership flags. Persistence is indirect: these mappings describe which logical sectors are present, zeroed, or remotely mapped in LSMT data files.

## Dependencies and Integration Points
Depends on `index.h`, LSMT file constants from `file.h`, Photon logging/utilities, and Photon filesystem types. `file.cpp` and warp-file paths consume these indexes for read, write, commit, stack, flatten, restack, and remote-data operations.

## Risks
Mapping correctness is sensitive to packed bit-field limits, sector units, sorted non-overlap assumptions, tag overflow, and ownership of raw buffers. `Index0` mutates set elements via casts, which depends on not changing sort keys after insertion except in carefully bounded split paths. `compress_raw_index_predict` ignores mapped-offset continuity, unlike `compress_raw_index`, so it is only a size estimate.

## Test Signals
`lsmt/test/test.cpp` exercises lookup trimming, overlap insertion, layered merge tags, compression, sparse writes, commit, stacking, zfile-backed layers, restack, warp files, and multithreaded verification. Useful additional checks are ASAN/UBSAN runs around `Index0` mutation and large mapping sets that force B+tree fallback/accelerated lookup paths.
