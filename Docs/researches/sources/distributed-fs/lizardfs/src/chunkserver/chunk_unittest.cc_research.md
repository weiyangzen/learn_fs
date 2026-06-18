# sources/distributed-fs/lizardfs/src/chunkserver/chunk_unittest.cc

## Purpose
This GoogleTest file verifies selected `Chunk`, `MooseFSChunk`, and `InterleavedChunk` behavior.

## Important APIs, Types, And Functions
- Fixture `ChunkTests` constructs standard and XOR MooseFS/interleaved chunks.
- `MaxBlocksInFile` validates slice block capacity for standard, 2-of-XOR, and 3-of-XOR chunks.
- `GetFileName` validates generated standard, XOR data, and XOR parity filenames and extensions.
- `GetSubfolderName` validates current `chunksXX` subfolder naming from numbers and chunk ids.

## Control Flow
Tests instantiate chunks in memory, create a minimal `folder` with `/mnt/`, set owner/chunk ids, and compare generated strings.

## State And Persistence
No disk state is modified. The tests validate functions that determine persisted chunk paths and capacity.

## Dependencies And Integration Points
It depends on GoogleTest, `chunk.h`, and `slice_traits`.

## Risks
Coverage does not include EC filenames, interleaved standard filenames, MooseFS/interleaved file-size validation, header size, old directory layout, or rename behavior.

## Test Signals
This is direct evidence for core chunk naming and max-block math but not for the full disk lifecycle.
