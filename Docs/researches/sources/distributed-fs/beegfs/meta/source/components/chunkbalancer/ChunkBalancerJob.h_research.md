# sources/distributed-fs/beegfs/meta/source/components/chunkbalancer/ChunkBalancerJob.h

## Purpose
Declares the PThread job that manages metadata chunk balancing candidate queues and worker slaves.

## Important APIs And Types
Important APIs are run(), abort() declaration, addChunkSyncCandidate(), shutdown(), getStatus(), isRunningStarting(), getJobStats(), createSyncSlave(), and private stats mutators. Constants cap slaves, queue-per-slave threshold, and sleep interval.

## Control Flow
External message handlers enqueue candidates and query status/stats. The job internally starts ChunkBalancerMetaSlave threads and shuts them down when idle or interrupted.

## State And Persistence
State includes jobStatsMutex-protected ChunkBalancerJobStatistics, a ChunkSyncCandidateStore, slave vector, abort/offline atomics, createSlaveRes, and a GlobalInodeLockStore pointer.

## Dependencies And Integration Points
Depends on Program/App, MetaStore and GlobalInodeLockStore, ChunkSyncCandidateStore, storage target mapping/state stores, comm slave queues, CopyChunkFileWork, and chunk-balancer statistics types.

## Risks And Edge Cases
abort() is declared but not implemented in the listed source, so callers should use shutdown if that remains true in the full tree. Manual raw-pointer slave ownership requires cleanup on every path. stats.workerNum decrement must not underflow if cleanup paths change.

## Test Signals
Compile/link tests should catch missing abort implementation if used. Runtime tests should validate status and stats under concurrent enqueue/shutdown.
