# sources/distributed-fs/ceph/src/osdc/Striper.h

## Purpose

`Striper.h` declares the static striping utility used to translate file byte ranges into object byte ranges and to reassemble striped object read results. It is a central shared helper for CephFS client IO, the filer/object cacher stack, and objecter scatter/gather helpers.

## Important APIs, types, and functions

`Striper::file_to_extents()` has overloads returning lightweight extents, a map from `object_t` to `ObjectExtent` vectors, and a flat vector of `ObjectExtent`. Another overload accepts an inode number and builds the conventional `%llx.%08llx` object name format. `extent_to_file()` maps object extents back to file extents. `object_truncate_size()`, `get_num_objects()`, and `get_file_offset()` expose layout math helpers.

`StripedReadResult` stores partial results by output offset and supports dense results from vector buffer extents or lightweight buffer extents, sparse results from either map or vector sparse extents, and final assembly into a `bufferlist`, caller buffer, or sparse extent map plus buffer.

## Control flow

The declared mapping flow is stateless: callers provide a `file_layout_t`, logical offset/length, truncate size, and optional buffer offset. The implementation computes one or more object extents, each with its in-object offset/length/truncate size and mapping back to output buffer extents. Read paths add each object's result to `StripedReadResult`, then call an assembly overload to produce the final logical read result.

## State and persistence behavior

`Striper` itself has no instances and no persistent state. `StripedReadResult` has transient aggregation state that is cleared by assembly methods. The persistent interpretation comes from the caller's file layout and object naming convention, not from this class.

## Dependencies and integration points

The header depends on Ceph file and OSD types plus `StriperTypes.h`. It forward-declares `file_layout_t`. Integration points include `Filer.cc`, `ObjectCacher`, CephFS client layout handling, MDS code that reasons about object counts/offsets, and `Objecter` scatter/gather read completion.

## Risks and edge cases

All APIs assume valid layout values, especially `object_size`, `stripe_unit`, and `stripe_count`. The vector/map overloads differ in grouping behavior; callers that need object grouping should use the map overload. The raw-buffer assembly requires the destination length to match `total_intended_len`, so mismatched extents will assert. Sparse assembly has several overloads with different sparse-map types; tests should protect against semantic drift between them.

## Test signals

Useful signals are unit tests for file-to-object and object-to-file mapping across stripe boundaries, object count calculations, truncate propagation, and read assembly through dense and sparse paths. Integration tests should validate `Filer` and `ObjectCacher` behavior for multi-object reads/writes.
