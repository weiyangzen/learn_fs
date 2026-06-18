## sources/distributed-fs/beegfs/storage/source/components/chunkfetcher/ChunkFetcherSlave.h

### Purpose
`ChunkFetcherSlave.h` declares the per-target fsck chunk enumeration thread. It is managed by `ChunkFetcher`, not started automatically at application startup.

### Important APIs, Types, And Functions
The class derives from `PThread`, stores a `LogContext`, running-state mutex/condition, `isRunning`, and `targetID`. Private methods are `run()`, `walkAllChunks()`, `walkChunkPath()`, and `setIsRunning()`. `ChunkFetcher` is a friend so it can inspect and wait on status internals.

### Control Flow, State, And Persistence
The header provides a status accessor `getIsRunning(bool isRunning)` whose parameter is unused; actual synchronization is through `statusMutex` and `isRunningChangeCond`. The worker stores only target identity and traversal status; chunk records are emitted to the owner.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on BeeGFS logging, component exceptions, `FsckChunk`, and threading. Risks include the odd getter signature, direct friend access, and non-public traversal methods that are only testable through `ChunkFetcher`. Tests should verify status transitions, shutdown wait signaling, and that target-specific logs/status are isolated.
