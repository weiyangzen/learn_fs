# sources/distributed-fs/ceph/src/osdc/Striper.cc

## Purpose

`Striper.cc` implements the mapping between logical file offsets and RADOS object extents for CephFS-style striped layouts, and provides helpers to assemble read results from multiple object reads back into file-order buffers or sparse extent maps.

## Important APIs, types, and functions

`format_oid()` creates object names from a printf-style object format and object number. `OrderByObject` supports binary insertion/search by object number in lightweight extent vectors. The internal templated `add_partial_sparse_result()` merges sparse read replies into the `StripedReadResult::partial` map while accounting for holes.

Public `Striper` functions implemented here include three `file_to_extents()` overloads, `extent_to_file()`, `object_truncate_size()`, `get_num_objects()`, `get_file_offset()`, and `StripedReadResult` methods for adding dense/sparse partial results and assembling final results into a `bufferlist`, raw buffer, or sparse extent map plus buffer.

## Control flow

`file_to_extents()` first maps a logical `(offset, len)` through `file_layout_t` fields: `object_size`, `stripe_unit`, and `stripe_count`. It computes block number, stripe number, stripe position, object set, object number, in-object offset, and slice length. Adjacent extents for the same object are merged when contiguous; each object extent records `buffer_extents` so later IO completion can place data back into logical output order. Lightweight extents can be returned directly or converted to heavyweight `ObjectExtent` values with formatted oid and `OSDMap::file_to_object_locator()`.

`extent_to_file()` performs the reverse mapping from object number and in-object extent to file extents. `object_truncate_size()` maps a file truncate size to the truncate size visible for one backing object. `get_num_objects()` computes object count for a file size using layout period and remainder. `get_file_offset()` maps one object offset back to file offset.

`StripedReadResult` accumulates partial object results keyed by logical buffer offset. Dense adds splice or move buffers according to `buffer_extents`. Sparse adds use the sparse map to skip holes and record intended lengths. Assembly emits data in sorted offset order, zero-filling holes when requested or when copying to a raw buffer; sparse assembly emits only present extents and returns total intended length.

## State and persistence behavior

No persistent state is stored. `StripedReadResult` holds transient `partial` buffers and `total_intended_len`, then clears `partial` on assembly. Mapping behavior is pure with respect to the file layout and truncate parameters.

## Dependencies and integration points

The file depends on Ceph buffer utilities, `file_layout_t`, `ObjectExtent`, `OSDMap::file_to_object_locator()`, debug logging, and `StriperTypes.h`. It is used by `Filer`, `ObjectCacher`, CephFS client code, MDS purge/accounting paths, and `Objecter` scatter/gather assembly. The lightweight path reduces allocation overhead for common small stripe counts before converting to heavyweight structures for older APIs.

## Risks and edge cases

`file_to_extents()` asserts `len > 0` and `object_size >= stripe_unit`; callers must avoid zero-length mapping requests. The VLA-style `char buf[strlen(object_format) + 32]` in `format_oid()` depends on compiler support and bounded format strings. Sparse assembly mutates input `bufferlist` by splicing, so callers must not expect the source buffer to remain intact. `total_intended_len` is incremented on every added partial and is not reset after assembly, so `StripedReadResult` instances should be one-shot or carefully reused. Truncate math around stripe/objectset boundaries is correctness-sensitive.

## Test signals

Tests should cover stripe_count 1, multi-object stripes, non-power-of-two stripe units, adjacent extent merging, buffer offset remapping, truncate sizes before/inside/after a target object, reverse mapping, sparse holes, raw-buffer zero fill, and integration through `Filer`/`ObjectCacher` scatter-gather reads and writes.
