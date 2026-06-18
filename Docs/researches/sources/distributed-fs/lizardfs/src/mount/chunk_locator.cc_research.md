# sources/distributed-fs/lizardfs/src/mount/chunk_locator.cc

## Purpose
`chunk_locator.cc` implements master lookups for read and write chunk locations. It translates master statuses into read/write exception classes and maintains read-side caching and write-side lock lifecycle.

## Important APIs, Types, And Functions
- `ReadChunkLocator::locateChunk(inode,index)` returns a cached or freshly fetched `ChunkLocationInfo`.
- `ReadChunkLocator::invalidateCache(inode,index)` clears the one-entry cache if it matches.
- `WriteChunkLocator::locateAndLockChunk(inode,index)` asks the master for write locations and a lock id via `fs_lizwritechunk`.
- `WriteChunkLocator::unlockChunk()` sends `WRITE_END` with chunk id, lock id, inode, and final file length.

## Control Flow
Read lookup first checks a mutex-protected one-entry cache. On miss it calls either legacy `fs_readchunk` parsing raw server address data, or modern `fs_lizreadchunk` filling `locations`. Master `ENOENT` is treated as unrecoverable, other nonzero read errors as recoverable. The result is cached under lock.

Write lookup asserts a single active inode/index, clears prior locations, keeps old lock/file length, calls `fs_lizwritechunk`, maps transient statuses (`IO`, no chunkservers, locked, busy, lost) to `RecoverableWriteException`, maps others to unrecoverable and clears `lockId_`, and preserves previous file length when refreshing an existing lock. Unlock sends `fs_lizwriteend`; communication IO is recoverable, returned non-OK after unlock is unrecoverable.

## State And Persistence
Read state is a single cached `shared_ptr<const ChunkLocationInfo>` plus inode/index protected by a mutex. Write state is inode/index, lock id, and mutable `locationInfo_` file length. Locks are persisted/owned at the master until `WRITE_END`; the destructor in the header attempts unlock if needed.

## Dependencies And Integration Points
It integrates with `mount/mastercomm.h`, `protocol/MFSCommunication.h`, common exceptions, request logging, and chunkserver address/type structures. `ChunkReader` and `ChunkWriter` consume these locators.

## Risks
- `ReadChunkLocator` default constructor in the header does not initialize `inode_`/`index_`; cache checks are safe only because `cache_` gates their use.
- Write locators assume one chunk at a time; misuse across multiple inode/index pairs trips `sassert`.
- Destructor unlock failures are logged but cannot be propagated.
- Recoverable/unrecoverable classification controls retry behavior and must stay aligned with master semantics.

## Test Signals
Tests should mock master calls for cache hits/misses, legacy parsing, status-to-exception mapping, repeated write-lock refresh preserving file length, unlock IO failure, and destructor unlock logging behavior.
