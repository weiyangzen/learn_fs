<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_type_with_address.h -->
# sources/distributed-fs/lizardfs/src/common/chunk_type_with_address.h

## Purpose

This header defines serializable records pairing a chunkserver address with a chunk part type, including a modern version carrying chunkserver version metadata.

## Important APIs, Types, and Functions

`legacy::ChunkTypeWithAddress` stores `NetworkAddress address` and legacy `ChunkPartType chunkType`. Modern `ChunkTypeWithAddress` stores `NetworkAddress address`, `ChunkPartType chunk_type`, and `uint32_t chunkserver_version`. Both define equality, ordering, and serialization methods.

## Control Flow

No runtime algorithm is present. Comparisons use address and part type; modern comparisons intentionally ignore `chunkserver_version`.

## State and Persistence Behavior

Instances are serialized in messages/metadata that list where a chunk part is stored. Modern serialization includes chunkserver version for compatibility decisions.

## Dependencies and Integration Points

It depends on network address, chunk part type, slice traits, and serialization macros. Readers, repair planners, and chunkserver selection code consume these records.

## Risks and Edge Cases

Ignoring `chunkserver_version` in equality/order is intentional for CRC error counting, but containers keyed by this type cannot distinguish same address/type with different versions. Legacy and modern field names differ.

## Test Signals

Useful tests are serialization round trips and set/map behavior proving version-insensitive comparison where expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_type_with_address.h -->
