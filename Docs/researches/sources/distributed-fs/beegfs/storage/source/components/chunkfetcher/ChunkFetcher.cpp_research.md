## sources/distributed-fs/beegfs/storage/source/components/chunkfetcher/ChunkFetcher.cpp

### Purpose
`ChunkFetcher.cpp` controls a group of per-target chunk walker threads used by fsck to enumerate storage chunks. It starts, stops, and waits for `ChunkFetcherSlave` instances.

### Important APIs, Types, And Functions
The constructor creates one slave per configured storage target. `startFetching()` clears the bad flag and starts any non-running slave. `stopFetching()` requests termination on running slaves. `waitForStopFetching()` wakes consumers, waits for every slave's `isRunning` flag to clear, and clears the shared chunk list.

### Control Flow, State, And Persistence
The component is not a thread itself. It owns a list of slave objects, a shared `FsckChunkList`, a mutex/condition pair for producer-consumer flow, and an `isBad` flag. Persistent state is not modified; slaves only read chunk metadata and queue it for fsck responses.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `StorageTargets`, `ChunkFetcherSlave`, and `PThread` status fields. `FetchFsckChunkListMsgEx` drives this component. Risks include holding slave status locks while waiting, clearing the shared queue inside each slave wait loop, and target list fixed at construction time. Tests should cover restart refusal/force restart through the message layer, startup failure, queue clearing on stop, and bad-flag propagation.
