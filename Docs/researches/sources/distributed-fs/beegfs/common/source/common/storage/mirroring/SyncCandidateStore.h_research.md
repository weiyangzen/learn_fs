<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/mirroring/SyncCandidateStore.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/mirroring/SyncCandidateStore.h

Purpose: Provides a templated producer/consumer queue for metadata or storage resync candidates, split into separate directory and file queues.

Important APIs/types: `SyncCandidateStore<SyncCandidateDir, SyncCandidateFile>` exposes overloaded `add` and `fetch` for file and directory candidates, `waitForFiles`, `waitForFilesWithResult`, `waitForDirs`, emptiness/size accessors, `clear`, and `notifyFilesAdded`. Internally it uses `Mutex` and `Condition` wrappers and tracks `numQueuedFiles`/`numQueuedDirs` with a `MAX_QUEUE_SIZE` of 50000.

Control flow/state/persistence: Producers block on queue-size limits until consumers signal fetched items, unless the caller `PThread` has a self-terminate request. Consumers wait with timed condition waits and return default-constructed candidates on shutdown. No data is persisted; all state is in memory.

Dependencies/integration: Used by buddy resync workers to coordinate gather/sync stages. Integrates with BeeGFS thread termination conventions through `PThread::getSelfTerminate`.

Risks/test signals: `waitForDirs(0)` uses a single wait rather than a spurious-wakeup loop, unlike file waits. Tests should stress multiple producers/consumers, shutdown while queues are full/empty, clear during idle periods, and timeout result correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/mirroring/SyncCandidateStore.h -->
