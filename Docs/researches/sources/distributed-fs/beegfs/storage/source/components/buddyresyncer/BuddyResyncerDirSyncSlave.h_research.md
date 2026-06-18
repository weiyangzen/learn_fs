## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncerDirSyncSlave.h

### Purpose
`BuddyResyncerDirSyncSlave.h` declares the directory reconciliation worker used by buddy resync jobs. It models a `PThread` that drains directory candidates, communicates with buddy targets, and publishes counters for resync progress and errors.

### Important APIs, Types, And Functions
The public constructor binds a local target, shared `ChunkSyncCandidateStore`, and slave ID. Private methods include `syncLoop()`, `doSync()`, `getBuddyDirContents()`, `findChunks()`, and `removeBuddyChunkPaths()`. Public accessors expose running state, idle-only termination, `numDirsSynced`, `numAdditionalDirsMatched`, and `errorCount`. The file also defines list/vector typedefs used by the owning resync job.

### Control Flow, State, And Persistence
State is thread-local except the shared candidate store: `isRunning` is protected by `statusMutex`, termination mode is `AtomicSizeT`, and counters are atomics. The header grants friendship to `BuddyResyncer` and `BuddyResyncJob`, which need direct access to status synchronization fields when stopping workers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on BeeGFS threading, node, storage error, and sync candidate abstractions. The main integration contract is that owners can start, terminate, and wait for `isRunningChangeCond`. Risks are misuse of friend access and confusing `getSelfTerminateNotIdle()` semantics. Tests should verify status transitions, idle-only termination, and counter reads under concurrent worker shutdown.
