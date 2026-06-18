# sources/distributed-fs/beegfs/meta/source/components/chunkbalancer/ChunkBalancerJob.cpp

## Purpose
Implements the metadata-side chunk balancing job that accepts chunk copy candidates, scales metadata slave workers, tracks locks/statistics, and stops after an idle interval.

## Important APIs And Types
Key APIs are run(), createSyncSlave(), addChunkSyncCandidate(), shutdown(), destructor cleanup, and status/stat mutators. It owns ChunkSyncCandidateStore, a vector of ChunkBalancerMetaSlave pointers, GlobalInodeLockStore pointer, and ChunkBalancerJobStatistics.

## Control Flow
run refuses duplicate RUNNING jobs, resets stats, starts an initial slave, then loops until termination. It updates queue and locked inode stats, starts more slaves when the queue crosses CHUNKBALANCERJOB_MAX_FILE_PER_SLAVE_LIMIT up to four slaves, enters IDLE when the queue is empty, exits SUCCESS after a configurable idle duration, recreates a slave if all died while work remains, periodically sums slave counters, advances inode lock timesteps, and in cleanup terminates/join-waits slaves, marks ERRORS if needed, clears chunk-rebalancing locks, and records endTime. addChunkSyncCandidate enforces the configured queue limit before adding.

## State And Persistence
State is held in job stats under jobStatsMutex, the candidate queue, slave vector, and GlobalInodeLockStore entries for CHUNK_REBALANCING. The job does not copy chunks itself; it schedules slave work that causes storage-server copy operations and inode locks.

## Dependencies And Integration Points
Depends on Program/App, MetaStore and GlobalInodeLockStore, ChunkSyncCandidateStore, storage target mapping/state stores, comm slave queues, CopyChunkFileWork, and chunk-balancer statistics types.

## Risks And Edge Cases
Stats aggregation overwrites totals with summed slave counters each iteration; deleted slave counters can be lost unless captured during cleanup. Busy waiting can occur when slaves see an empty queue. Lock timeout depends on iterationDuration. createSlaveRes is a shared member used across starts.

## Test Signals
Test queue limit behavior, first slave creation failure, scaling to max slaves, idle-to-success timeout, shutdown interruption, dead slave replacement, error aggregation, and lock-store clearing.
