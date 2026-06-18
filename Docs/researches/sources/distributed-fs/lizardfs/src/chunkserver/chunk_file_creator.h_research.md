# sources/distributed-fs/lizardfs/src/chunkserver/chunk_file_creator.h

## Purpose
`chunk_file_creator.h` declares the safe chunk creation helper used to create a complete chunk and delete it automatically unless committed.

## Important APIs, Types, And Functions
- `ChunkFileCreator(uint64_t chunkId, uint32_t chunkVersion, ChunkPartType chunkType)` stores target identity.
- `create`, `write`, and `commit` form the lifecycle API.
- Accessors `chunkId`, `chunkVersion`, and `chunkType` expose target identity to replication planning.
- Protected fields hold target identity, the owned `Chunk *`, and lifecycle booleans.

## Control Flow
Consumers construct the object on the stack, call `create`, write data blocks, and call `commit`. Stack unwinding before commit triggers cleanup in the implementation destructor.

## State And Persistence
The header describes ownership of one in-progress chunk file. Persistence becomes permanent only after commit.

## Dependencies And Integration Points
It includes `ChunkPartType` and `chunk.h`, tying it to chunkserver disk abstractions. `ChunkReplicator` is the primary listed consumer.

## Risks
The class is copyable by default unless disabled elsewhere by compiler rules from members; copying would be unsafe because both instances would point at the same `Chunk *`. The header does not explicitly delete copy/move operations.

## Test Signals
No direct tests are listed for this class.
