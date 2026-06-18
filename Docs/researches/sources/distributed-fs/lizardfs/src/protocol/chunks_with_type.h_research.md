# sources/distributed-fs/lizardfs/src/protocol/chunks_with_type.h

## Purpose
Defines serializable chunk-id plus chunk-part-type records for protocol messages.

## Important APIs, Types, And Functions
Uses `LIZARDFS_DEFINE_SERIALIZABLE_CLASS` to declare `legacy::ChunkWithType` using `legacy::ChunkPartType` and modern `ChunkWithType` using `ChunkPartType`, each with `uint64_t id` and `type`.

## Control Flow
No executable flow beyond generated serialization/deserialization methods from macros.

## State And Persistence Behavior
No runtime state; it defines wire-serializable value types.

## Dependencies And Integration Points
Depends on `common/chunk_part_type.h` and `common/serialization_macros.h`. Used by protocol messages that need to carry chunk ids with standard/xor/EC part type information.

## Risks And Edge Cases
Legacy and modern names differ only by namespace, so call sites must choose the correct type for packet version compatibility. Serialization size changes follow `ChunkPartType` representation changes.

## Test Signals
Covered indirectly by packet tests that serialize chunk type fields.
