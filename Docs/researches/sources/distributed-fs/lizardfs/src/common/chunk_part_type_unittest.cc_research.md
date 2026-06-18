<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_part_type_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/chunk_part_type_unittest.cc

## Purpose

This file validates chunk part type serialization, id validity, and slice length/block calculations.

## Important APIs, Types, and Functions

Tests are `SerializeDeserialize`, `validChunkTypeIDTest`, `chunkTypeLengthTest`, and `GetNumberOfBlocks`. It uses `slice_traits` helpers and chunk type constants.

## Control Flow

The tests enumerate standard, tape, XOR levels, and EC data/parity combinations, marking valid ids across the 16-bit space. They serialize/deserialize known types and check length/block arithmetic for representative chunk lengths.

## State and Persistence Behavior

Only local vectors/booleans are used.

## Dependencies and Integration Points

It integrates `ChunkPartType` with `Goal::Slice::Type` and `slice_traits`.

## Risks and Edge Cases

The valid-id test is broad but can be expensive because it scans all 65536 ids. Length tests are representative, not exhaustive for every EC layout.

## Test Signals

Passing tests are strong signals that type encoding and core slice arithmetic remain compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_part_type_unittest.cc -->
