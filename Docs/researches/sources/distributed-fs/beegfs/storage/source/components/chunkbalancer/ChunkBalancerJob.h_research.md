## sources/distributed-fs/beegfs/storage/source/components/chunkbalancer/ChunkBalancerJob.h

### Purpose
`ChunkBalancerJob.h` declares the storage chunk-balancing controller. It provides the public interface used to add migration candidates, inspect status, and stop the job.

### Important APIs, Types, And Functions
The class derives from `PThread` and exposes `run()`, `getJobStats()`, `getStatus()`, `isRunningStarting()`, `addChunkSyncCandidate()`, and `shutdown()`. Private constants bound scaling behavior: maximum four slaves, 5000 queued files per slave threshold, five-second sleep interval, and 600-second idle shutdown. Private helpers mutate stats under `jobStatsMutex`.

### Control Flow, State, And Persistence
State includes the in-memory candidate store, vector of worker pointers, abort/offline atomics, `createSlaveRes`, and `ChunkBalancerJobStatistics`. Persistence is outside the job itself; it schedules workers that update chunk placement and metadata.

### Dependencies, Integration Points, Risks, And Test Signals
It integrates with `CpChunkPathsMsgEx`, `ChunkBalancerFileSyncSlave`, and `SyncCandidate.h`. Risks include raw worker ownership, counters decremented without guarding underflow, unused or underused abort/offline fields, and tight coupling through friendship. Tests should validate thread-safe stats snapshots, candidate enqueue limits, worker count changes, and shutdown state transitions.
