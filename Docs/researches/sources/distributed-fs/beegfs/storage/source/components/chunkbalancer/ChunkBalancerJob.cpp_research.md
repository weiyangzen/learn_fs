## sources/distributed-fs/beegfs/storage/source/components/chunkbalancer/ChunkBalancerJob.cpp

### Purpose
`ChunkBalancerJob.cpp` implements the controller thread for chunk balancing. It accepts chunk migration candidates, starts and scales worker slaves, tracks job statistics, and shuts down after sustained queue idleness or explicit termination.

### Important APIs, Types, And Functions
`run()` enforces a single running job, creates an initial `ChunkBalancerFileSyncSlave`, monitors queue length, spawns up to `CHUNKBALANCERJOB_MAX_SLAVE_LIMIT`, prunes failed slaves, aggregates counters, and performs cleanup. `createSyncSlave()` starts a worker. `addChunkSyncCandidate()` enforces `tuneChunkBalanceQueueLimit` before queueing. `shutdown()` marks interruption, requests self termination, and wakes waiters.

### Control Flow, State, And Persistence
The main loop alternates between running, idle, scaling, and cleanup states. An empty queue starts an idle timer; after `CHUNKBALANCERJOB_MAX_TIME_LIMIT`, the job terminates slaves and marks success. State is protected by `jobStatsMutex` and stored in `ChunkBalancerJobStatistics`; persistent effects are indirect through worker chunk migration.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include `ChunkSyncCandidateStore`, worker slaves, config queue limits, and `Program::getApp()`. Risks include stats being overwritten rather than accumulated, worker counter double-counting across iterations, manual vector erase/delete patterns, status set to success before final slave error aggregation, and busy or slow scaling behavior. Tests should cover single-run rejection, queue limit, dynamic slave creation, idle shutdown timing, failed worker replacement, shutdown wakeup, and final status with worker errors.
