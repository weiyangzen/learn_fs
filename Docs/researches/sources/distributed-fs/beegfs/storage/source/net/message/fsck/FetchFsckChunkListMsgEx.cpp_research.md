## sources/distributed-fs/beegfs/storage/source/net/message/fsck/FetchFsckChunkListMsgEx.cpp

### Purpose
`FetchFsckChunkListMsgEx.cpp` handles fsck polling for chunk metadata batches. It starts the chunk fetcher, supports force-restarting an existing run, and returns chunk batches with a run status.

### Important APIs, Types, And Functions
`processIncoming()` gets `ChunkFetcher` from the app. On `FetchFsckChunkListStatus_NOTSTARTED`, it rejects concurrent runs unless `getForceRestart()` is set; a forced restart stops and waits for the old run before calling `startFetching()`. It derives status from `getIsBad()` and `getNumRunning()`, drains up to `getMaxNumChunks()` via `getAndDeleteChunks()`, and sends `FetchFsckChunkListRespMsg`.

### Control Flow, State, And Persistence
State is held by `ChunkFetcher`: running slaves, bad flag, and queued chunk list. This handler is a polling interface and does not modify chunk files.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `ChunkFetcher`, fsck request/response types, and app globals. Risks include starting fetch even if `startFetching()` fails, status computed before draining the queue, and forced restart clearing queued data. Tests should cover first start, concurrent not-forced request, forced restart, read-error status, finished-with-remaining-queue behavior, and batch size limits.
