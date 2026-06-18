# sources/distributed-fs/lizardfs/src/mount/chunk_locator.h

## Purpose
`chunk_locator.h` declares data structures and classes for locating file chunks on chunkservers and managing write locks.

## Important APIs, Types, And Functions
- `ChunkLocationInfo` stores `chunkId`, `version`, `fileLength`, and `std::vector<ChunkTypeWithAddress> locations`; `isEmptyChunk()` reports sparse chunks with id `0`.
- `ReadChunkLocator` is a thread-safe per-descriptor read locator with a one-entry cache.
- `WriteChunkLocator` owns a master write lock and exposes `locateAndLockChunk`, `unlockChunk`, `chunkIndex`, `updateFileLength`, and `locationInfo`.
- `TruncateWriteChunkLocator` adapts master-owned locks for truncation so the client destructor does not unlock them.

## Control Flow
Callers use `ReadChunkLocator::locateChunk` before reads and invalidate after stale data signals. Writers call `locateAndLockChunk`, pass `locationInfo` to `ChunkWriter`, update file length as writes complete, and eventually call `unlockChunk`. `WriteChunkLocator` also unlocks in its destructor if a lock remains.

## State And Persistence
The header declares transient locator state only. `WriteChunkLocator` state mirrors a master lock and final file length that will be persisted when write-end reaches the master.

## Dependencies And Integration Points
It depends on `ChunkTypeWithAddress`, logging, exceptions, and master communication implementation in the `.cc`. It is consumed by chunk read/write classes and truncate paths.

## Risks
- The destructor catches only `Exception&`; non-LizardFS exceptions from unlock would escape a destructor.
- `updateFileLength` has a cosmetic `locationInfo_. fileLength` spacing issue but compiles.
- The API exposes `locationInfo` by const reference while internal file length can later change.

## Test Signals
Unit tests should verify destructor behavior with fake locators, single-chunk invariant, `TruncateWriteChunkLocator` not unlocking, and `isEmptyChunk` sparse-read decisions.
