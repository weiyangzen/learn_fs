# sources/distributed-fs/beegfs/meta/source/components/chunkbalancer/SyncCandidate.h

## Purpose
Defines chunk-balancer candidate value types describing a chunk to copy from one target/group to another for a file entry.

## Important APIs And Types
Important types are IdType, ChunkSyncCandidateDir, ChunkSyncCandidateFile, and ChunkSyncCandidateStore. Candidates carry idType, relativePath, targetID, destinationID, EntryInfo copy, and FileEvent copy.

## Control Flow
Producers construct candidates from balancing requests; ChunkBalancerJob queues them; ChunkBalancerMetaSlave fetches file candidates and uses their entry/event data to lock metadata and submit CopyChunkFileWork.

## State And Persistence
Candidates are in-memory queue records. EntryInfo and FileEvent are stored by value to avoid depending on caller lifetime.

## Dependencies And Integration Points
Depends on Program/App, MetaStore and GlobalInodeLockStore, ChunkSyncCandidateStore, storage target mapping/state stores, comm slave queues, CopyChunkFileWork, and chunk-balancer statistics types.

## Risks And Edge Cases
The constructor casts an IdType parameter that is already IdType, but invalid numeric values can still be represented. getFileEvent() always returns a pointer to the internal event despite the comment about nullptr. Pool IDs are defined but not handled by the listed slave logic.

## Test Signals
Test value-copy behavior, default construction, invalid ID handling, group-ID mirrored path, and queue fetch/add semantics.
