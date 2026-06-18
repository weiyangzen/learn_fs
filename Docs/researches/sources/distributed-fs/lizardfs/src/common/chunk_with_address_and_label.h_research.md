<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_with_address_and_label.h -->
# sources/distributed-fs/lizardfs/src/common/chunk_with_address_and_label.h

## Purpose

This header defines serializable chunk-location records that include network addresses, media labels, and chunk part types.

## Important APIs, Types, and Functions

Legacy and modern `ChunkPartWithAddressAndLabel` classes store `NetworkAddress address`, `std::string label`, and a chunk part type. Modern `ChunkWithAddressAndLabel` stores `chunk_id`, `chunk_version`, and a vector of chunk parts.

## Control Flow

No algorithmic control flow exists. Equality/order for part records compare address, label, and chunk type.

## State and Persistence Behavior

These value objects are serialized into protocol or metadata messages describing all known locations/labels for a chunk.

## Dependencies and Integration Points

It depends on media labels, network addresses, chunk part types, and serialization macros. Master/client/chunkserver reporting paths can use these records for placement and goal decisions.

## Risks and Edge Cases

Labels are serialized as strings, so normalization must happen elsewhere. Legacy and modern chunk type encodings differ; conversions must be explicit at message boundaries.

## Test Signals

Expected tests include serialization round trips, ordering in sorted containers, and compatibility conversion from legacy records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_with_address_and_label.h -->
