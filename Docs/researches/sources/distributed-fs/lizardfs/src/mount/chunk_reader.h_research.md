# sources/distributed-fs/lizardfs/src/mount/chunk_reader.h

## Purpose
`chunk_reader.h` declares the `ChunkReader` class that performs prepared chunk reads using a connector and erasure/replication-aware planning.

## Important APIs, Types, And Functions
- Constructor accepts a `ChunkConnector` and `bandwidth_overuse` score/planner parameter.
- `prepareReadingChunk` locates the chunk and selects candidate chunkservers.
- `readData` appends bytes to a caller-owned buffer.
- Accessors expose whether a chunk is located, current inode/index, chunk id, and version.
- `preparations` is a static atomic diagnostic counter.

## Control Flow
The class separates prepare from read: a caller can prepare once per chunk and call `readData` for ranges. Force prepare bypasses the same-chunk short-circuit.

## State And Persistence
All state is transient and per reader. It includes the locator, selected locations, planner, and CRC-failed server/type list. No on-disk state is modified.

## Dependencies And Integration Points
It includes chunk connector, read planner/executor, connection pool, network address, time utilities, and `chunk_locator.h`. It is a mount read-path component.

## Risks
- Accessors `chunkId()` and `version()` dereference `location_`; callers must check `isChunkLocated` or ensure preparation.
- No explicit synchronization exists in `ChunkReader`; it appears intended for descriptor/path-local use rather than concurrent calls.

## Test Signals
Header-level tests are through implementation: lifecycle checks, accessor behavior after prepare, and correct use by higher-level read data code.
