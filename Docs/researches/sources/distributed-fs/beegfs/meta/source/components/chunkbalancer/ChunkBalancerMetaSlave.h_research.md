# sources/distributed-fs/beegfs/meta/source/components/chunkbalancer/ChunkBalancerMetaSlave.h

## Purpose
Declares the metadata chunk-balancing slave thread derived from SyncSlaveBase.

## Important APIs And Types
Exports constructor, destructor, getNumChunksSynced(), getErrorCount(), and syncLoop(). Stores queue pointer, targetID, inodeLockStore pointer, and atomic counters.

## Control Flow
ChunkBalancerJob creates these slaves and reads their counters while managing the candidate queue.

## State And Persistence
Runtime state is non-owning with respect to the candidate store and parent job. Counters are atomic and used for job stats.

## Dependencies And Integration Points
Depends on Program/App, MetaStore and GlobalInodeLockStore, ChunkSyncCandidateStore, storage target mapping/state stores, comm slave queues, CopyChunkFileWork, and chunk-balancer statistics types.

## Risks And Edge Cases
targetID and inodeLockStore members are not initialized in the constructor shown; targetID appears unused, but future use would require initialization. Queue lifetime is owned by the job.

## Test Signals
Compile tests should flag unused/uninitialized member use if warnings are enabled. Integration tests should verify counters and thread state through the parent job.
