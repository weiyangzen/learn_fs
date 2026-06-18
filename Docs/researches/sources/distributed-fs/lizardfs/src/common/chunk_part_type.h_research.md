<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_part_type.h -->
# sources/distributed-fs/lizardfs/src/common/chunk_part_type.h

## Purpose

This header defines compact identifiers for chunk part types, including legacy one-byte encoding and modern two-byte encoding that supports more slice types and parts.

## Important APIs, Types, and Functions

`legacy::ChunkPartType` stores an 8-bit id with `kMaxPartsCount=11` and `kMaxType=9`. Modern `ChunkPartType` stores a 16-bit id with `kMaxPartsCount=64` and `kMaxTypeCount=2048`. Both expose constructors, `getSliceType()`, `getSlicePart()`, `getId()`, `isValid()`, `toString()`, comparisons, and serialization/deserialization. Modern type converts to/from legacy.

## Control Flow

Ids are computed as `slice_type * max_parts + part`. Deserialization validates that the resulting type/part is valid for `Goal::Slice::Type`. Legacy conversion clamps unsupported modern values to an invalid-but-representable legacy type.

## State and Persistence Behavior

The id is serialized into protocols/metadata. Numeric stability is critical for compatibility.

## Dependencies and Integration Points

It depends on `Goal`, `slice_traits`, and serialization helpers. It is used by planners, chunk metadata structs, network messages, and calculators.

## Risks and Edge Cases

Changing `kMaxPartsCount` or `Goal::Slice::Type` numbering changes the wire/storage encoding. Legacy conversion intentionally loses information for unsupported types. Assertions guard constructor ranges only in debug builds.

## Test Signals

`chunk_part_type_unittest.cc` covers serialization, valid id space, chunk part lengths, and block counts for standard/XOR/EC-related traits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_part_type.h -->
