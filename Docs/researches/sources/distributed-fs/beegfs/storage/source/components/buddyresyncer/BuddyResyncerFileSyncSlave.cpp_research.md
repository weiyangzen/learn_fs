## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncerFileSyncSlave.cpp

### Purpose
`BuddyResyncerFileSyncSlave.cpp` implements the file/chunk-side buddy resync worker. It consumes chunk candidates and delegates the actual block-wise copy or remote removal to the shared `ChunkFileResyncer` base.

### Important APIs, Types, And Functions
The constructor sets `chunkFileResyncerMode` to `CHUNKFILERESYNCER_FLAG_BUDDYMIRROR`, stores the shared `ChunkSyncCandidateStore`, and records the target. `getFD()` returns the target's mirror directory FD, so the base reads from the buddy mirror subtree. `syncLoop()` fetches `ChunkSyncCandidateFile` objects, maps local target IDs to buddy target IDs, and calls `ChunkFileResyncer::doResync()`.

### Control Flow, State, And Persistence
The loop exits only when termination is requested and the file queue is empty, or when non-idle termination is requested. Successful resyncs increment `numChunksSynced`; non-interruption failures increment `errorCount`. Persistent effects are performed by the base: remote `ResyncLocalFileMsg` writes, remote stale chunk deletion, and local chunk locking around reads.

### Dependencies, Integration Points, Risks, And Test Signals
The worker integrates with `BuddyResyncJob`, `MirrorBuddyGroupMapper`, and `ChunkFileResyncer`. Risks are mostly inherited from the base copy path: source chunk deletion races, sparse handling, and buddy target state handling. Tests should enqueue existing, missing, sparse, and concurrently deleted chunks and verify counters plus remote messages.
