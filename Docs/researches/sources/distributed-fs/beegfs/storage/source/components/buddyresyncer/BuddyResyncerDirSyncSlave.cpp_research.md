## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncerDirSyncSlave.cpp

### Purpose
`BuddyResyncerDirSyncSlave.cpp` implements the directory-side worker for buddy resync. It consumes directory candidates for a local target, lists the corresponding buddy mirror directory, discovers locally missing subdirectories for later traversal, and removes stale chunk files from the buddy target when the local side no longer has them.

### Important APIs, Types, And Functions
The thread entry point is `run()`, which initializes counters and calls `syncLoop()`. `syncLoop()` fetches `ChunkSyncCandidateDir` entries from `ChunkSyncCandidateStore` and maps the local target to its buddy target through `MirrorBuddyGroupMapper`. `doSync()` performs one directory reconciliation pass. `getBuddyDirContents()` sends `ListChunkDirIncrementalMsg`; `findChunks()` compares remote names with local paths and manages `ChunkLockStore`; `removeBuddyChunkPaths()` sends `RmChunkPathsMsg`.

### Control Flow, State, And Persistence
The worker runs until termination is requested and the candidate queue is drained, with a special idle-only termination mode. Directory listing is paged in `CHECK_AT_ONCE` chunks. For each page, entries still present locally are erased from the removal list; missing files remain locked until remote deletion completes; missing subdirectories are requeued as additional directory candidates. Persistent effects are remote chunk deletion through the buddy storage node and new in-memory resync candidates.

### Dependencies, Integration Points, Risks, And Test Signals
The code depends on `Program::getApp()`, target/node mappers, `TargetStateStore`, `MessagingTk`, storage target mirror file descriptors, and path helpers. Risks include retry loops delaying shutdown, lock leaks if removal paths change, treating `PATHNOTEXISTS` as benign during listing, and reliance on parallel `names`/`entryTypes` list mutation. Tests should cover paged listing, offline buddy handling, local directory discovery, remote delete failures, chunk locking/unlocking, and termination during retries.
