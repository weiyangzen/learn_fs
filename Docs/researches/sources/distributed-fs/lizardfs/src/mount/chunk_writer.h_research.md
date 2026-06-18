# sources/distributed-fs/lizardfs/src/mount/chunk_writer.h

## Purpose
`chunk_writer.h` declares `ChunkWriter`, the stateful engine that turns write-cache blocks for one chunk into network write operations.

## Important APIs, Types, And Functions
- Constructor binds `ChunkserverStats`, `ChunkConnector`, and optional `dataChainFd`.
- `init`, `addOperation`, `startNewOperations`, `processOperations`, `finish`, and `abortOperations` form the write lifecycle.
- `startFlushMode` stops accepting new operations and allows all queued work to flush.
- `dropNewOperations` discards work not yet started and stops accepting more.
- `releaseJournal` transfers remaining journal blocks back to the caller after abort/defer.
- Nested `Operation` groups journal positions, parity buffers, unfinished write count, and file end offset.

## Control Flow
Callers initialize against a locked chunk locator, add write blocks, periodically start/process operations, enter flush mode, wait for pending operations to finish, then call `finish`. On retry paths, callers can abort and recover the journal.

## State And Persistence
The header exposes transient write state members. Persistent write completion is indirect through chunkservers and the associated locator’s final file length.

## Dependencies And Integration Points
It depends on chunk part/address structures, `WriteExecutor`, `WriteChunkLocator`, and `WriteCacheBlock`. It is used by the mount write cache/workers.

## Risks
- The class is noncopyable and appears not thread-safe internally; external worker serialization is required.
- `locator_` is a raw pointer that must outlive the writer lifecycle.
- `allocateId` can wrap around after `uint32_t` overflow and collide with outstanding ids in extreme long-lived cases.

## Test Signals
Header behavior is validated through writer unit/integration tests for lifecycle order, noncopyability, journal release, and operation grouping.
