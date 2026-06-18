# sources/distributed-fs/ceph/src/osdc/StriperTypes.h

## Purpose

`StriperTypes.h` defines lightweight extent containers used by `Striper` to represent object extents and their output-buffer mappings without the heavier `ObjectExtent` type. These types support fast common-case file layout mapping.

## Important APIs, types, and functions

Inside namespace `striper`, `BufferExtent` is an `(offset, length)` pair for an extent in the logical striped output buffer. `LightweightBufferExtents` is a `boost::container::small_vector<BufferExtent, 4>`, optimized for the common case of a few buffer spans.

`LightweightObjectExtent` is a non-default-constructible struct with `object_no`, in-object `offset`, in-object `length`, `truncate_size`, and `buffer_extents`. `LightweightObjectExtents` is a small vector of up to four lightweight object extents before heap allocation. An `operator<<` prints the extent fields and buffer mappings.

## Control flow

The types are passive data carriers. `Striper::file_to_extents()` constructs and possibly merges `LightweightObjectExtent` entries, then either returns them directly or converts them into heavyweight `ObjectExtent` values with object names and locators.

## State and persistence behavior

There is no persistent state. The containers hold transient mapping results for a single layout operation or read assembly operation.

## Dependencies and integration points

The header depends on `include/types.h`, Boost small vectors, and stream output. It is included by `Striper.h` and used by `Striper.cc`, `ObjectCacher`, and any path that wants lower-allocation mapping output.

## Risks and edge cases

The types do not validate ranges or ordering; callers must preserve sorted object order and meaningful buffer extents. `operator<<` relies on stream support for the small-vector of buffer extents. The deleted default constructor prevents accidental uninitialized object extents, but it also means container operations must construct with full extent values.

## Test signals

Test coverage is indirect through `Striper::file_to_extents()` and read assembly. Useful checks include small-vector behavior for one to four extents, conversion to heavyweight `ObjectExtent`, output formatting for debug logs, and preservation of `truncate_size` and `buffer_extents`.
