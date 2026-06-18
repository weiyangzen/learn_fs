## sources/distributed-fs/beegfs/storage/source/components/chunkfetcher/ChunkFetcher.h

### Purpose
`ChunkFetcher.h` declares the fsck chunk enumeration coordinator. It owns per-target walker threads and a bounded shared queue of `FsckChunk` records.

### Important APIs, Types, And Functions
Public lifecycle methods are `startFetching()`, `stopFetching()`, and `waitForStopFetching()`. Queue and status helpers include `getIsBad()`, `setBad()`, `addChunk()`, `isQueueEmpty()`, `getAndDeleteChunks()`, and `getNumRunning()`. `MAX_CHUNKLIST_SIZE` caps queued chunks at 5000.

### Control Flow, State, And Persistence
`addChunk()` blocks producers when the list exceeds the cap until `getAndDeleteChunks()` splices a batch out and signals. The queue is protected by `chunksListMutex`; slave status is protected by each slave's mutex. No persistent changes are made.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `ChunkFetcherSlave`, `FsckChunk`, `ListTk`, and BeeGFS threading primitives. Integration is with `FetchFsckChunkListMsgEx`, which polls batches and status. Risks include one global queue shared by all targets, condition waits without caller termination checks in `addChunk()`, and target membership captured only at construction. Tests should validate bounded queue behavior, batch splicing order, running count, and bad state.
