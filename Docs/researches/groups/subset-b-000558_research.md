# subset-b-000558 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncerDirSyncSlave.cpp -->
## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncerDirSyncSlave.cpp

### Purpose
`BuddyResyncerDirSyncSlave.cpp` implements the directory-side worker for buddy resync. It consumes directory candidates for a local target, lists the corresponding buddy mirror directory, discovers locally missing subdirectories for later traversal, and removes stale chunk files from the buddy target when the local side no longer has them.

### Important APIs, Types, And Functions
The thread entry point is `run()`, which initializes counters and calls `syncLoop()`. `syncLoop()` fetches `ChunkSyncCandidateDir` entries from `ChunkSyncCandidateStore` and maps the local target to its buddy target through `MirrorBuddyGroupMapper`. `doSync()` performs one directory reconciliation pass. `getBuddyDirContents()` sends `ListChunkDirIncrementalMsg`; `findChunks()` compares remote names with local paths and manages `ChunkLockStore`; `removeBuddyChunkPaths()` sends `RmChunkPathsMsg`.

### Control Flow, State, And Persistence
The worker runs until termination is requested and the candidate queue is drained, with a special idle-only termination mode. Directory listing is paged in `CHECK_AT_ONCE` chunks. For each page, entries still present locally are erased from the removal list; missing files remain locked until remote deletion completes; missing subdirectories are requeued as additional directory candidates. Persistent effects are remote chunk deletion through the buddy storage node and new in-memory resync candidates.

### Dependencies, Integration Points, Risks, And Test Signals
The code depends on `Program::getApp()`, target/node mappers, `TargetStateStore`, `MessagingTk`, storage target mirror file descriptors, and path helpers. Risks include retry loops delaying shutdown, lock leaks if removal paths change, treating `PATHNOTEXISTS` as benign during listing, and reliance on parallel `names`/`entryTypes` list mutation. Tests should cover paged listing, offline buddy handling, local directory discovery, remote delete failures, chunk locking/unlocking, and termination during retries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncerDirSyncSlave.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncerDirSyncSlave.h -->
## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncerDirSyncSlave.h

### Purpose
`BuddyResyncerDirSyncSlave.h` declares the directory reconciliation worker used by buddy resync jobs. It models a `PThread` that drains directory candidates, communicates with buddy targets, and publishes counters for resync progress and errors.

### Important APIs, Types, And Functions
The public constructor binds a local target, shared `ChunkSyncCandidateStore`, and slave ID. Private methods include `syncLoop()`, `doSync()`, `getBuddyDirContents()`, `findChunks()`, and `removeBuddyChunkPaths()`. Public accessors expose running state, idle-only termination, `numDirsSynced`, `numAdditionalDirsMatched`, and `errorCount`. The file also defines list/vector typedefs used by the owning resync job.

### Control Flow, State, And Persistence
State is thread-local except the shared candidate store: `isRunning` is protected by `statusMutex`, termination mode is `AtomicSizeT`, and counters are atomics. The header grants friendship to `BuddyResyncer` and `BuddyResyncJob`, which need direct access to status synchronization fields when stopping workers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on BeeGFS threading, node, storage error, and sync candidate abstractions. The main integration contract is that owners can start, terminate, and wait for `isRunningChangeCond`. Risks are misuse of friend access and confusing `getSelfTerminateNotIdle()` semantics. Tests should verify status transitions, idle-only termination, and counter reads under concurrent worker shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncerDirSyncSlave.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncerFileSyncSlave.cpp -->
## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncerFileSyncSlave.cpp

### Purpose
`BuddyResyncerFileSyncSlave.cpp` implements the file/chunk-side buddy resync worker. It consumes chunk candidates and delegates the actual block-wise copy or remote removal to the shared `ChunkFileResyncer` base.

### Important APIs, Types, And Functions
The constructor sets `chunkFileResyncerMode` to `CHUNKFILERESYNCER_FLAG_BUDDYMIRROR`, stores the shared `ChunkSyncCandidateStore`, and records the target. `getFD()` returns the target's mirror directory FD, so the base reads from the buddy mirror subtree. `syncLoop()` fetches `ChunkSyncCandidateFile` objects, maps local target IDs to buddy target IDs, and calls `ChunkFileResyncer::doResync()`.

### Control Flow, State, And Persistence
The loop exits only when termination is requested and the file queue is empty, or when non-idle termination is requested. Successful resyncs increment `numChunksSynced`; non-interruption failures increment `errorCount`. Persistent effects are performed by the base: remote `ResyncLocalFileMsg` writes, remote stale chunk deletion, and local chunk locking around reads.

### Dependencies, Integration Points, Risks, And Test Signals
The worker integrates with `BuddyResyncJob`, `MirrorBuddyGroupMapper`, and `ChunkFileResyncer`. Risks are mostly inherited from the base copy path: source chunk deletion races, sparse handling, and buddy target state handling. Tests should enqueue existing, missing, sparse, and concurrently deleted chunks and verify counters plus remote messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncerFileSyncSlave.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncerFileSyncSlave.h -->
## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncerFileSyncSlave.h

### Purpose
`BuddyResyncerFileSyncSlave.h` declares the buddy resync file worker as a concrete `ChunkFileResyncer`. It specializes the generic chunk copy primitive for the mirror directory of a local target.

### Important APIs, Types, And Functions
The class exposes a constructor/destructor and overrides `syncLoop()` plus `getFD()`. It stores a `ChunkSyncCandidateStore*` supplied by the resync job. Typedefs provide list and vector containers for owners managing multiple workers.

### Control Flow, State, And Persistence
Most state and counters live in `ChunkFileResyncer`; this header adds only the shared queue pointer. The overridden `getFD()` is the key persistence boundary because it chooses whether the base reads from normal chunks or the mirror directory.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `SyncCandidateStore`, storage errors, BeeGFS threading, and `ChunkFileResyncer`. Friend access lets `BuddyResyncer` and `BuddyResyncJob` coordinate worker shutdown. Tests should focus on correct FD selection and base-class status/counter behavior when running as a buddy mirror worker.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncerFileSyncSlave.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncerGatherSlave.cpp -->
## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncerGatherSlave.cpp

### Purpose
`BuddyResyncerGatherSlave.cpp` scans a target's buddy mirror directory and discovers chunk and directory candidates that changed after the last safe buddy communication time. It is the discovery phase that feeds file and directory sync slaves.

### Important APIs, Types, And Functions
`run()` initializes counters and calls `workLoop()`. `workLoop()` fetches root paths from `BuddyResyncerGatherSlaveWorkQueue` and walks them with `nftw()`. `handleDiscoveredEntry()` is the static `nftw` callback; it recovers the current worker from `staticGatherSlaves`, computes the relative path, compares timestamps, and adds `ChunkSyncCandidateDir` or `ChunkSyncCandidateFile` objects.

### Control Flow, State, And Persistence
The worker runs until termination and queue drain. The callback builds `chunksPath` as `<target>/buddymirror`, skips the root, and adjusts `lastBuddyComm` by `sysResyncSafetyThresholdMins` unless the timestamp is an override. Directory `mtime` and file `ctime` are compared against that threshold. State is in counters, the static thread-name map, and the shared candidate store; persistent filesystem state is read-only.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include `StorageTarget`, `Config`, `StorageTkEx`, `nftw`, and the shared candidate store. Risks include stale static map entries because the destructor does not erase them, thread-name lookup failure in the callback, timestamp precision assumptions, and racey online filesystem traversal. Tests should cover threshold behavior, override timestamps, file versus directory counters, empty queue termination, and deletion races during `nftw`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncerGatherSlave.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncerGatherSlave.h -->
## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncerGatherSlave.h

### Purpose
`BuddyResyncerGatherSlave.h` declares the candidate discovery worker and its bounded work queue for buddy resync. It separates path scheduling from filesystem traversal.

### Important APIs, Types, And Functions
`BuddyResyncerGatherSlaveWorkQueue` offers `add()`, `fetch()`, `queueEmpty()`, and `clear()` with a `GATHERSLAVEQUEUE_MAXSIZE` backpressure limit. `BuddyResyncerGatherSlave` exposes `run()`, static `handleDiscoveredEntry()`, `getCounters()`, running-state accessors, and idle-only termination controls.

### Control Flow, State, And Persistence
The queue stores pending scan roots in a `StringList`, tracks length separately to avoid repeated `size()`, and uses two condition variables: one for path arrival and one for fetch completion. Worker state includes atomics for discovered/matched chunks and directories, a static mutex-protected map from thread names to workers for `nftw`, and a reference to the target being scanned.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on BeeGFS logging/threading, sync candidates, and POSIX `ftw.h`. Owners rely on friend access for shutdown waiting. Risks include lock contention/backpressure when many paths are enqueued and static worker-map lifetime. Tests should validate queue blocking/unblocking, termination while waiting, counter snapshots, and callback routing to the correct worker.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncerGatherSlave.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/ChunkFileResyncer.cpp -->
## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/ChunkFileResyncer.cpp

### Purpose
`ChunkFileResyncer.cpp` implements the reusable block-wise chunk copy engine used by buddy resync and chunk balancing. It reads a local chunk file, sends `ResyncLocalFileMsg` blocks to a destination target, handles sparse regions and final attributes, and optionally removes a stale destination chunk when the source disappeared.

### Important APIs, Types, And Functions
`run()` manages thread lifecycle and counters, while concrete subclasses implement `syncLoop()` and `getFD()`. `doResync()` is the copy workhorse. It resolves the destination node, locks the local chunk by basename, opens the chunk with `openat()`, reads up to `SYNC_BLOCK_SIZE`, detects sparse blocks using `RESYNCER_SPARSE_BLOCK_SIZE`, sends `ResyncLocalFileMsg`, and retries while the destination target is not offline. `removeChunkUnlocked()` sends `RmChunkPathsMsg` for missing chunks.

### Control Flow, State, And Persistence
The copy loop advances `offset` until a short read or error. At the last block it uses `fstat()` to attach mode, owner, group, mtime, and atime, and sets truncation flags if a concurrent truncate makes the logical size smaller. Persistent effects occur on the destination target through network messages; local state is chunk locks, file descriptors, offsets, and counters.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include target/node mappers, `ChunkLockStore`, storage target FDs, `MessagingTk`, and resync message types. Risks include `goto` cleanup paths, offset arithmetic when `readRes` is negative, sparse detection only by fixed zero-block comparisons, retry loops during shutdown, and concurrent local truncation/deletion. Tests should cover missing source behavior in buddy versus balancing modes, sparse chunks, short reads, final attribute propagation, destination offline state, and chunk lock release on every path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/ChunkFileResyncer.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/ChunkFileResyncer.h -->
## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/ChunkFileResyncer.h

### Purpose
`ChunkFileResyncer.h` declares the abstract base thread for copying chunk files between storage targets. It centralizes lifecycle, counters, and copy/removal helpers shared by buddy resync and chunk balancing workers.

### Important APIs, Types, And Functions
The `ChunkFileResyncerMode` enum distinguishes buddy mirror copy, normal chunk balance copy, and mirrored chunk balance copy. Subclasses must implement `syncLoop()` and `getFD()`. Protected helpers are `doResync()` and `removeChunkUnlocked()`. Public methods expose idle-only termination, synced chunk count, error count, and running status.

### Control Flow, State, And Persistence
The class owns status synchronization (`statusMutex`, `isRunningChangeCond`), atomic counters, target identifiers, a path string, and an FD field used during copy. Persistence is not in the header itself, but the abstract `getFD()` decides whether copy reads from normal or mirror chunk storage.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on BeeGFS node, storage error, thread, and storage target abstractions. Friend classes (`BuddyResyncer`, `BuddyResyncJob`, `ChunkBalancerJob`) coordinate worker lifecycle. Risks include subclasses sharing mutable base fields, `getIsRunning()` returning `uint64_t` despite exposing a boolean, and mode flag naming that maps enum values to message flags indirectly. Tests should validate subclass mode behavior, status signaling, and counter reset on `run()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/ChunkFileResyncer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/SyncCandidate.h -->
## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/SyncCandidate.h

### Purpose
`SyncCandidate.h` defines the candidate payloads passed through storage resync and chunk balancing queues. A candidate identifies a relative chunk/directory path and the source target, with optional destination and metadata context for balancing.

### Important APIs, Types, And Functions
`ChunkSyncCandidateDir` stores `relativePath`, `targetID`, optional `destinationID`, copied `EntryInfo`, `isBuddyMirrorChunk`, and copied `FileEvent`. Accessors expose these values, including pointers to the embedded `EntryInfo` and `FileEvent`. `ChunkSyncCandidateFile` derives from the directory candidate and adds no additional fields. `ChunkSyncCandidateStore` aliases `SyncCandidateStore<ChunkSyncCandidateDir, ChunkSyncCandidateFile>`.

### Control Flow, State, And Persistence
The default constructor marks an invalid candidate with `targetID == 0`, which consumers use as a sentinel. Constructors that accept pointers immediately copy `EntryInfo` and `FileEvent`, avoiding dependency on caller lifetimes. There is no persistence beyond in-memory queue storage.

### Dependencies, Integration Points, Risks, And Test Signals
This header integrates buddy resync discovery/sync workers and chunk balancing job queues. Risks include uninitialized optional fields when using the simple constructor, pointer accessors exposing mutable embedded state, and relying on `targetID == 0` as the only invalid marker. Tests should cover simple buddy candidates, balancing candidates with metadata/event copies, default invalid candidates, and queue round-trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/SyncCandidate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/chunkbalancer/ChunkBalancerFileSyncSlave.cpp -->
## sources/distributed-fs/beegfs/storage/source/components/chunkbalancer/ChunkBalancerFileSyncSlave.cpp

### Purpose
`ChunkBalancerFileSyncSlave.cpp` implements the worker that migrates chunk files for storage balancing. It copies a chunk to the destination, updates metadata stripe information, removes the original chunk, and handles mirrored chunks through buddy group IDs.

### Important APIs, Types, And Functions
The constructor selects `CHUNKFILERESYNCER_FLAG_CHUNKBALANCE`. `syncLoop()` fetches `ChunkSyncCandidateFile` entries, validates that the basename matches `EntryInfo::getEntryID()`, resolves the owning metadata node, selects mirrored or non-mirrored resync mode, calls `ChunkFileResyncer::doResync()`, sends `UpdateStripePatternMsg`, removes secondary buddy copies via `sendRemoveChunkPathsMessage()`, removes the source with `removeChunk()`, and prunes empty parent chunk dirs.

### Control Flow, State, And Persistence
For mirrored chunks, the worker reads from the mirror FD and converts source/destination target IDs to buddy group IDs before updating metadata. Stripe pattern update happens after copy, even when the copy reports `PATHNOTEXISTS`, so metadata learns the copy result. Persistent effects include destination chunk creation, metadata stripe changes, remote secondary deletion, local unlink, and possible parent directory removal.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `ChunkFileResyncer`, metadata and storage node stores, target mappers, buddy group mappers, `ChunkStore`, and chunk-balancing message types. Risks include orphaned chunks if metadata update or deletion fails, source deletion after partial success, confusing local target ID rewrite for mirrored chunks, and a busy loop when the queue is empty. Tests should cover ID mismatch rejection, mirrored migration, non-mirrored migration, metadata communication failure, source/secondary delete failure, and `PATHNOTEXISTS` handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/chunkbalancer/ChunkBalancerFileSyncSlave.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/chunkbalancer/ChunkBalancerFileSyncSlave.h -->
## sources/distributed-fs/beegfs/storage/source/components/chunkbalancer/ChunkBalancerFileSyncSlave.h

### Purpose
`ChunkBalancerFileSyncSlave.h` declares the concrete `ChunkFileResyncer` used by `ChunkBalancerJob`. It specializes generic resync for chunk migration and metadata stripe update workflows.

### Important APIs, Types, And Functions
The class constructor accepts a target ID, shared candidate store, and slave ID. It overrides `syncLoop()` and `getFD()`, and declares helpers `removeChunk()` and `sendRemoveChunkPathsMessage()`. State includes the shared `ChunkSyncCandidateStore*`, current `targetID`, and `isBuddyMirrorChunk`.

### Control Flow, State, And Persistence
The `isBuddyMirrorChunk` flag controls whether the inherited copy uses the mirror FD or normal chunk FD and whether remote removal is flagged as buddy mirror removal. The header exposes only vector typedefs to owners; lifecycle and counters come from the base class.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on sync candidates, BeeGFS storage errors/threading, and `ChunkFileResyncer`. `ChunkBalancerJob` is a friend because it manages worker internals. Risks include per-candidate mutable `isBuddyMirrorChunk` affecting inherited operations and no public ownership abstraction around the raw candidate-store pointer. Tests should validate FD selection and helper behavior for mirrored and non-mirrored candidates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/chunkbalancer/ChunkBalancerFileSyncSlave.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/chunkbalancer/ChunkBalancerJob.cpp -->
## sources/distributed-fs/beegfs/storage/source/components/chunkbalancer/ChunkBalancerJob.cpp

### Purpose
`ChunkBalancerJob.cpp` implements the controller thread for chunk balancing. It accepts chunk migration candidates, starts and scales worker slaves, tracks job statistics, and shuts down after sustained queue idleness or explicit termination.

### Important APIs, Types, And Functions
`run()` enforces a single running job, creates an initial `ChunkBalancerFileSyncSlave`, monitors queue length, spawns up to `CHUNKBALANCERJOB_MAX_SLAVE_LIMIT`, prunes failed slaves, aggregates counters, and performs cleanup. `createSyncSlave()` starts a worker. `addChunkSyncCandidate()` enforces `tuneChunkBalanceQueueLimit` before queueing. `shutdown()` marks interruption, requests self termination, and wakes waiters.

### Control Flow, State, And Persistence
The main loop alternates between running, idle, scaling, and cleanup states. An empty queue starts an idle timer; after `CHUNKBALANCERJOB_MAX_TIME_LIMIT`, the job terminates slaves and marks success. State is protected by `jobStatsMutex` and stored in `ChunkBalancerJobStatistics`; persistent effects are indirect through worker chunk migration.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include `ChunkSyncCandidateStore`, worker slaves, config queue limits, and `Program::getApp()`. Risks include stats being overwritten rather than accumulated, worker counter double-counting across iterations, manual vector erase/delete patterns, status set to success before final slave error aggregation, and busy or slow scaling behavior. Tests should cover single-run rejection, queue limit, dynamic slave creation, idle shutdown timing, failed worker replacement, shutdown wakeup, and final status with worker errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/chunkbalancer/ChunkBalancerJob.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/chunkbalancer/ChunkBalancerJob.h -->
## sources/distributed-fs/beegfs/storage/source/components/chunkbalancer/ChunkBalancerJob.h

### Purpose
`ChunkBalancerJob.h` declares the storage chunk-balancing controller. It provides the public interface used to add migration candidates, inspect status, and stop the job.

### Important APIs, Types, And Functions
The class derives from `PThread` and exposes `run()`, `getJobStats()`, `getStatus()`, `isRunningStarting()`, `addChunkSyncCandidate()`, and `shutdown()`. Private constants bound scaling behavior: maximum four slaves, 5000 queued files per slave threshold, five-second sleep interval, and 600-second idle shutdown. Private helpers mutate stats under `jobStatsMutex`.

### Control Flow, State, And Persistence
State includes the in-memory candidate store, vector of worker pointers, abort/offline atomics, `createSlaveRes`, and `ChunkBalancerJobStatistics`. Persistence is outside the job itself; it schedules workers that update chunk placement and metadata.

### Dependencies, Integration Points, Risks, And Test Signals
It integrates with `CpChunkPathsMsgEx`, `ChunkBalancerFileSyncSlave`, and `SyncCandidate.h`. Risks include raw worker ownership, counters decremented without guarding underflow, unused or underused abort/offline fields, and tight coupling through friendship. Tests should validate thread-safe stats snapshots, candidate enqueue limits, worker count changes, and shutdown state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/chunkbalancer/ChunkBalancerJob.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/chunkfetcher/ChunkFetcher.cpp -->
## sources/distributed-fs/beegfs/storage/source/components/chunkfetcher/ChunkFetcher.cpp

### Purpose
`ChunkFetcher.cpp` controls a group of per-target chunk walker threads used by fsck to enumerate storage chunks. It starts, stops, and waits for `ChunkFetcherSlave` instances.

### Important APIs, Types, And Functions
The constructor creates one slave per configured storage target. `startFetching()` clears the bad flag and starts any non-running slave. `stopFetching()` requests termination on running slaves. `waitForStopFetching()` wakes consumers, waits for every slave's `isRunning` flag to clear, and clears the shared chunk list.

### Control Flow, State, And Persistence
The component is not a thread itself. It owns a list of slave objects, a shared `FsckChunkList`, a mutex/condition pair for producer-consumer flow, and an `isBad` flag. Persistent state is not modified; slaves only read chunk metadata and queue it for fsck responses.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `StorageTargets`, `ChunkFetcherSlave`, and `PThread` status fields. `FetchFsckChunkListMsgEx` drives this component. Risks include holding slave status locks while waiting, clearing the shared queue inside each slave wait loop, and target list fixed at construction time. Tests should cover restart refusal/force restart through the message layer, startup failure, queue clearing on stop, and bad-flag propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/chunkfetcher/ChunkFetcher.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/chunkfetcher/ChunkFetcher.h -->
## sources/distributed-fs/beegfs/storage/source/components/chunkfetcher/ChunkFetcher.h

### Purpose
`ChunkFetcher.h` declares the fsck chunk enumeration coordinator. It owns per-target walker threads and a bounded shared queue of `FsckChunk` records.

### Important APIs, Types, And Functions
Public lifecycle methods are `startFetching()`, `stopFetching()`, and `waitForStopFetching()`. Queue and status helpers include `getIsBad()`, `setBad()`, `addChunk()`, `isQueueEmpty()`, `getAndDeleteChunks()`, and `getNumRunning()`. `MAX_CHUNKLIST_SIZE` caps queued chunks at 5000.

### Control Flow, State, And Persistence
`addChunk()` blocks producers when the list exceeds the cap until `getAndDeleteChunks()` splices a batch out and signals. The queue is protected by `chunksListMutex`; slave status is protected by each slave's mutex. No persistent changes are made.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `ChunkFetcherSlave`, `FsckChunk`, `ListTk`, and BeeGFS threading primitives. Integration is with `FetchFsckChunkListMsgEx`, which polls batches and status. Risks include one global queue shared by all targets, condition waits without caller termination checks in `addChunk()`, and target membership captured only at construction. Tests should validate bounded queue behavior, batch splicing order, running count, and bad state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/chunkfetcher/ChunkFetcher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/chunkfetcher/ChunkFetcherSlave.cpp -->
## sources/distributed-fs/beegfs/storage/source/components/chunkfetcher/ChunkFetcherSlave.cpp

### Purpose
`ChunkFetcherSlave.cpp` implements one fsck chunk walker per storage target. It recursively scans normal chunk directories and, when this target is the primary of a buddy group, the buddy mirror directory.

### Important APIs, Types, And Functions
`run()` sets running state, registers signal handling, and calls `walkAllChunks()`. `walkAllChunks()` finds the target path, walks `chunks`, determines primary buddy status, and optionally walks `buddymirror` with the buddy group ID. `walkChunkPath()` recursively uses `opendir`, `readdir`, `stat`, and directory recursion; file entries are converted to `FsckChunk` objects and queued through `ChunkFetcher::addChunk()`.

### Control Flow, State, And Persistence
For each file, the relative chunk path is derived from `basePathLen`, `dirname()` supplies the saved path, and stat fields populate size, blocks, ctime, mtime, atime, uid, gid, target ID, and buddy group ID. `ENOENT` after `readdir()` is ignored to tolerate online deletions. The worker sets the fetcher's bad flag on open/stat/read failures or termination.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include POSIX directory APIs, `StorageTargets`, `MirrorBuddyGroupMapper`, `FsckChunk`, and `ChunkFetcher`. Risks include recursion depth, symlink/stat behavior, deprecated `readdir_r` path handling, allocation from `strdup()`, and marking termination as bad. Tests should cover normal and mirrored traversal, online delete races, unreadable directories, recursive paths, queue backpressure, and buddy group ID population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/chunkfetcher/ChunkFetcherSlave.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/chunkfetcher/ChunkFetcherSlave.h -->
## sources/distributed-fs/beegfs/storage/source/components/chunkfetcher/ChunkFetcherSlave.h

### Purpose
`ChunkFetcherSlave.h` declares the per-target fsck chunk enumeration thread. It is managed by `ChunkFetcher`, not started automatically at application startup.

### Important APIs, Types, And Functions
The class derives from `PThread`, stores a `LogContext`, running-state mutex/condition, `isRunning`, and `targetID`. Private methods are `run()`, `walkAllChunks()`, `walkChunkPath()`, and `setIsRunning()`. `ChunkFetcher` is a friend so it can inspect and wait on status internals.

### Control Flow, State, And Persistence
The header provides a status accessor `getIsRunning(bool isRunning)` whose parameter is unused; actual synchronization is through `statusMutex` and `isRunningChangeCond`. The worker stores only target identity and traversal status; chunk records are emitted to the owner.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on BeeGFS logging, component exceptions, `FsckChunk`, and threading. Risks include the odd getter signature, direct friend access, and non-public traversal methods that are only testable through `ChunkFetcher`. Tests should verify status transitions, shutdown wait signaling, and that target-specific logs/status are isolated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/chunkfetcher/ChunkFetcherSlave.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/streamlistenerv2/StorageStreamListenerV2.h -->
## sources/distributed-fs/beegfs/storage/source/components/streamlistenerv2/StorageStreamListenerV2.h

### Purpose
`StorageStreamListenerV2.h` adapts the common stream listener for storage servers that route incoming work to target-specific queues. It is a storage-side subclass of `StreamListenerV2`.

### Important APIs, Types, And Functions
The constructor forwards `listenerID`, `app`, and a null queue to `StreamListenerV2`. The only overridden method is `getWorkQueue(uint16_t targetID)`, which returns `Program::getApp()->getWorkQueue(targetID)`.

### Control Flow, State, And Persistence
The class has no own mutable state. Its behavior is entirely dispatch-oriented: when the base listener needs a work queue for a message target, this subclass looks it up from the storage `App`.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on the storage `App`, global `Program`, and common `StreamListenerV2`. Integration is with the storage worker queue map and message processing. Risks include global app lookup in a const method and missing/null queues for invalid target IDs depending on `App::getWorkQueue()` behavior. Tests should exercise direct and per-target routing with valid, default, and unknown target IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/streamlistenerv2/StorageStreamListenerV2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/worker/StorageBenchWork.cpp -->
## sources/distributed-fs/beegfs/storage/source/components/worker/StorageBenchWork.cpp

### Purpose
`StorageBenchWork.cpp` executes one storage benchmark unit on a worker thread. It reads from or writes to an already-open file descriptor and reports completion or failure to the benchmark operator through a pipe.

### Important APIs, Types, And Functions
`StorageBenchWork::process()` switches on `StorageBenchType_READ` or `StorageBenchType_WRITE`. It uses config tuneables `tuneFileReadSize` and `tuneFileWriteSize` to split `bufLen` into repeated `read()` or `write()` calls. It updates node operation stats for read/write ops and writes either `threadID` or `STORAGEBENCH_ERROR_WORKER_ERROR` to `operatorCommunication`.

### Control Flow, State, And Persistence
The work object owns a file descriptor, buffer pointer, buffer length, target ID, type, virtual thread ID, and pipe. Persistent effects are benchmark reads/writes on the target file and operation counters. Short I/O breaks the loop; only `ioRes == -1` logs the underlying system error.

### Dependencies, Integration Points, Risks, And Test Signals
It integrates with `StorageBenchOperator`, `Work` queues, config tuneables, `NodeOpStats`, and `Pipe`. Risks include treating short positive I/O as success, not retrying interrupted system calls, raw buffer lifetime ownership outside the object, and no target-specific stats beyond counters. Tests should cover read, write, unknown type, pipe notification, short I/O, and system-call failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/worker/StorageBenchWork.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/worker/StorageBenchWork.h -->
## sources/distributed-fs/beegfs/storage/source/components/worker/StorageBenchWork.h

### Purpose
`StorageBenchWork.h` declares the benchmark work item queued to BeeGFS workers. It packages all state needed to perform a read or write benchmark operation.

### Important APIs, Types, And Functions
The constructor records target ID, virtual thread ID, file descriptor, benchmark type, buffer length, operator communication pipe, and buffer pointer. The override `process()` performs the actual I/O in the `.cpp`.

### Control Flow, State, And Persistence
The header stores raw non-owning resources: `fileDescriptor`, `Pipe*`, and `char* buf`. The work item does not own cleanup; it only signals completion through the pipe after processing.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `StorageBench`, `Work`, `Pipe`, and common BeeGFS types. Risks include lifetime/ownership assumptions for the FD, buffer, and pipe, plus no copy/move restrictions despite raw handles. Tests should validate object construction, worker dispatch, and operator communication around success and failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/worker/StorageBenchWork.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/NetMessageFactory.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/NetMessageFactory.cpp

### Purpose
`NetMessageFactory.cpp` is the storage daemon's message type factory. It maps incoming BeeGFS wire message type IDs to concrete storage-side message handler objects.

### Important APIs, Types, And Functions
`NetMessageFactory::createFromMsgType()` switches over `NETMSGTYPE_*` constants and returns a `std::unique_ptr<NetMessage>`. The cases cover control, node, storage, session, monitoring, fsck, benchmark, chunk balancing, and optional NVFS RDMA messages. Unknown IDs produce `SimpleMsg(NETMSGTYPE_Invalid)`.

### Control Flow, State, And Persistence
The factory is stateless. Its control flow is a single switch grouped by message domain. Persistent behavior is indirect: choosing `*MsgEx` classes determines which `processIncoming()` methods can mutate storage state.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on a broad set of common response messages and storage-specific `*MsgEx` includes. Integration is central to message deserialization in the storage app. Risks include missing cases for new protocol messages, accidentally instantiating a common base instead of a storage handler, compile differences under `BEEGFS_NVFS`, and long switch maintenance. Tests should instantiate every expected storage message type, verify invalid fallback, and check RDMA cases under NVFS builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/NetMessageFactory.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/NetMessageFactory.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/NetMessageFactory.h

### Purpose
`NetMessageFactory.h` declares the storage daemon implementation of `AbstractNetMessageFactory`. It provides the type-erased entry point used by the network layer to build message objects.

### Important APIs, Types, And Functions
The class has a trivial constructor and overrides `createFromMsgType(unsigned short) const`, returning `std::unique_ptr<NetMessage>`.

### Control Flow, State, And Persistence
The header has no persistent state. The protected override enforces that all creation flows go through the common factory interface.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `common/Common.h` and `AbstractNetMessageFactory`. Integration is with `App::getNetMessageFactory()` and `MessagingTk` deserialization. Risks are minimal but include ABI/interface drift if the abstract factory signature changes. Tests should compile and instantiate the factory through the base interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/NetMessageFactory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/control/AckMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/control/AckMsgEx.cpp

### Purpose
`AckMsgEx.cpp` handles incoming acknowledgement messages on the storage daemon. It records an ack value in the local acknowledgement store and updates operation statistics.

### Important APIs, Types, And Functions
`AckMsgEx::processIncoming()` logs the ack value, calls `Program::getApp()->getAckStore()->receivedAck(getValue())`, updates `StorageOpCounter_ACK`, and returns true without sending a response.

### Control Flow, State, And Persistence
There is no reply flow because ack messages are terminal notifications. The only state mutation is in `AcknowledgmentStore`; op stats are also updated with peer IP and message user ID.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `Program`, `AcknowledgmentStore`, `ResponseContext`, and node op stats. Risks are low; bad or duplicated ack values are delegated to the store. Tests should verify ack-store notification, no response send, and op-counter update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/control/AckMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/control/AckMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/control/AckMsgEx.h

### Purpose
`AckMsgEx.h` declares the storage-side extension of the common `AckMsg`. It supplies the server processing hook for acknowledgement messages.

### Important APIs, Types, And Functions
`AckMsgEx` inherits `AckMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
The header has no state. Its integration contract is that the factory creates this class for `NETMSGTYPE_Ack` so the storage daemon can update its ack store.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on the common control message type. Risks are limited to ensuring the override remains compatible with the base interface. Tests should confirm factory dispatch and virtual processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/control/AckMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/control/SetChannelDirectMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/control/SetChannelDirectMsgEx.cpp

### Purpose
`SetChannelDirectMsgEx.cpp` processes requests that mark a socket as direct. Direct channels indicate that subsequent messages are definitely processed on this storage server rather than forwarded.

### Important APIs, Types, And Functions
`SetChannelDirectMsgEx::processIncoming()` logs the integer value, calls `ctx.getSocket()->setIsDirect(getValue())`, updates `StorageOpCounter_SETCHANNELDIRECT`, and returns true without sending a response.

### Control Flow, State, And Persistence
The message mutates per-socket state only. No persistent storage is changed and no reply is required by this control message.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on the response context socket, `Program`, and node operation stats. Risks include clients setting the flag unexpectedly and relying on socket lifetime. Tests should verify socket flag mutation, no response, and stats update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/control/SetChannelDirectMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/control/SetChannelDirectMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/control/SetChannelDirectMsgEx.h

### Purpose
`SetChannelDirectMsgEx.h` declares the storage-side handler for `SetChannelDirectMsg`.

### Important APIs, Types, And Functions
The class inherits `SetChannelDirectMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
The header has no data members. All behavior is implemented in the `.cpp`, where the socket's direct flag is changed.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on the common control message class and is instantiated by the storage message factory. Tests should confirm factory dispatch and virtual override behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/control/SetChannelDirectMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/fsck/DeleteChunksMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/fsck/DeleteChunksMsgEx.cpp

### Purpose
`DeleteChunksMsgEx.cpp` handles fsck-driven deletion of chunk files from storage targets. It removes requested chunks and reports which deletions failed.

### Important APIs, Types, And Functions
`processIncoming()` iterates over `FsckChunkList` from `getChunks()`, builds `<savedPath>/<chunkID>`, resolves the target, selects mirror or normal FD based on `buddyGroupID`, calls `unlinkat()`, optionally prunes the empty chunk directory through `ChunkStore::rmdirChunkDirPath()`, and responds with `DeleteChunksRespMsg`.

### Control Flow, State, And Persistence
Unknown targets and unlink failures other than `ENOENT` add the chunk to `failedDeletes`. `ENOENT` is considered already deleted. Successful unlink is persistent and may be followed by directory cleanup.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on fsck message types, `StorageTargets`, `ChunkStore`, and target directory FDs. Risks include deleting mirrored chunks based only on buddy group ID presence, path construction from fsck-provided saved paths, and online races. Tests should cover unknown targets, normal and mirrored deletion, `ENOENT`, unlink errors, failed directory pruning tolerance, and response failure lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/fsck/DeleteChunksMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/fsck/DeleteChunksMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/fsck/DeleteChunksMsgEx.h

### Purpose
`DeleteChunksMsgEx.h` declares the storage-side fsck deletion handler.

### Important APIs, Types, And Functions
`DeleteChunksMsgEx` derives from common `DeleteChunksMsg` and overrides `processIncoming(ResponseContext&)`. It includes both request and response message types.

### Control Flow, State, And Persistence
The header has no state; deletion state and failed chunk lists are local to processing.

### Dependencies, Integration Points, Risks, And Test Signals
It integrates with `NetMessageFactory` for `NETMSGTYPE_DeleteChunks`. Risks are primarily in the `.cpp` deletion semantics. Tests should verify the handler can be constructed and dispatched through the factory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/fsck/DeleteChunksMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/fsck/FetchFsckChunkListMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/fsck/FetchFsckChunkListMsgEx.cpp

### Purpose
`FetchFsckChunkListMsgEx.cpp` handles fsck polling for chunk metadata batches. It starts the chunk fetcher, supports force-restarting an existing run, and returns chunk batches with a run status.

### Important APIs, Types, And Functions
`processIncoming()` gets `ChunkFetcher` from the app. On `FetchFsckChunkListStatus_NOTSTARTED`, it rejects concurrent runs unless `getForceRestart()` is set; a forced restart stops and waits for the old run before calling `startFetching()`. It derives status from `getIsBad()` and `getNumRunning()`, drains up to `getMaxNumChunks()` via `getAndDeleteChunks()`, and sends `FetchFsckChunkListRespMsg`.

### Control Flow, State, And Persistence
State is held by `ChunkFetcher`: running slaves, bad flag, and queued chunk list. This handler is a polling interface and does not modify chunk files.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `ChunkFetcher`, fsck request/response types, and app globals. Risks include starting fetch even if `startFetching()` fails, status computed before draining the queue, and forced restart clearing queued data. Tests should cover first start, concurrent not-forced request, forced restart, read-error status, finished-with-remaining-queue behavior, and batch size limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/fsck/FetchFsckChunkListMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/fsck/FetchFsckChunkListMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/fsck/FetchFsckChunkListMsgEx.h

### Purpose
`FetchFsckChunkListMsgEx.h` declares the storage-side handler for fsck chunk enumeration polling.

### Important APIs, Types, And Functions
The class inherits `FetchFsckChunkListMsg` and overrides `processIncoming(ResponseContext&)`. It includes the common response message type used to return chunks and status.

### Control Flow, State, And Persistence
No state is stored in the handler object beyond the deserialized request. Runtime state is delegated to `ChunkFetcher`.

### Dependencies, Integration Points, Risks, And Test Signals
It is instantiated by `NetMessageFactory` for fsck list requests. Tests should confirm factory construction and response generation through the `.cpp` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/fsck/FetchFsckChunkListMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/fsck/MoveChunkFileMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/fsck/MoveChunkFileMsgEx.cpp

### Purpose
`MoveChunkFileMsgEx.cpp` handles fsck-triggered relocation of a chunk file within a storage target's chunk tree. It can operate on normal or mirrored chunk directories and optionally prevents overwriting an existing destination.

### Important APIs, Types, And Functions
`processIncoming()` responds with `MoveChunkFileRespMsg(moveChunk())`. `moveChunk()` reads chunk name, old/new paths, target ID, overwrite flag, and mirror flag; resolves the target; checks destination existence when overwrite is disabled; creates the destination parent directory with `StorageTk::createPathOnDisk()`; and calls `renameat()` between target-relative paths.

### Control Flow, State, And Persistence
The operation returns `0` on success and `1` on failure. On mirrored moves, success marks the target as needing buddy resync via `setBuddyNeedsResync(true)`. Persistent effects are directory creation and the actual chunk rename.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on target FDs, `StorageTk`, `Path`, and fsck messages. Risks include broad `Log_CRITICAL` logging for request errors, races between destination existence check and rename, path trust from fsck, and mirror resync side effects. Tests should cover unknown target, overwrite false with existing destination, parent creation failure, normal rename, mirrored rename, and `renameat()` failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/fsck/MoveChunkFileMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/fsck/MoveChunkFileMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/fsck/MoveChunkFileMsgEx.h

### Purpose
`MoveChunkFileMsgEx.h` declares the storage-side fsck chunk move handler.

### Important APIs, Types, And Functions
The class derives from `MoveChunkFileMsg`, overrides `processIncoming(ResponseContext&)`, and keeps `moveChunk()` private as the local filesystem operation helper.

### Control Flow, State, And Persistence
The handler has no own state beyond inherited request fields. Persistence is performed by `moveChunk()` in the `.cpp`.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on common fsck move request/response message classes. Tests should verify factory dispatch and direct `processIncoming()` response codes for move success/failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/fsck/MoveChunkFileMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/mon/RequestStorageDataMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/mon/RequestStorageDataMsgEx.cpp

### Purpose
`RequestStorageDataMsgEx.cpp` serves monitoring requests for aggregated storage daemon state. It packages local node identity, target space information, session count, high-resolution stats, work queue sizes, and per-target info.

### Important APIs, Types, And Functions
`processIncoming()` calls `StorageTargets::generateTargetInfoList()`, sums total/free disk space, gets session count, local NICs, hostname, stats since the request timestamp, and indirect/direct work queue sizes across `MultiWorkQueueMap`. It replies with `RequestStorageDataRespMsg` and updates `StorageOpCounter_REQUESTSTORAGEDATA`.

### Control Flow, State, And Persistence
The handler is read-only. It treats `diskSpaceTotal == -1` as a sentinel that stops further summing if any target stat failed. Runtime state is sampled from targets, sessions, stats collector, work queues, and node identity.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include monitoring message types, `StorageTargets`, `StatsCollector`, `MultiWorkQueue`, and node op stats. Risks include aggregate totals when one target reports failure, potentially large stats histories, and queue sizes racing with workers. Tests should cover multi-target aggregation, stat failure sentinel behavior, empty stats history, session count, and queue size summing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/mon/RequestStorageDataMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/mon/RequestStorageDataMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/mon/RequestStorageDataMsgEx.h

### Purpose
`RequestStorageDataMsgEx.h` declares the storage-side monitoring data handler.

### Important APIs, Types, And Functions
`RequestStorageDataMsgEx` derives from `RequestStorageDataMsg` and overrides `processIncoming(ResponseContext&)`. The header includes app, queue, storage info, messaging, response, and program dependencies needed by the implementation.

### Control Flow, State, And Persistence
The class itself has no extra state; it uses inherited request fields such as the last stats timestamp.

### Dependencies, Integration Points, Risks, And Test Signals
It is instantiated for `NETMSGTYPE_RequestStorageData`. Tests should confirm factory routing and that the response can be built with mocked storage target and stats state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/mon/RequestStorageDataMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/GenericDebugMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/GenericDebugMsgEx.cpp

### Purpose
`GenericDebugMsgEx.cpp` implements storage daemon debug commands exposed through `GenericDebugMsg`. It returns textual diagnostics and can alter certain runtime debug controls.

### Important APIs, Types, And Functions
`processIncoming()` logs the command, calls `processCommand()`, responds with `GenericDebugRespMsg`, and updates op stats. `processCommand()` dispatches local commands such as `listopenfiles`, `version`, `msgqueuestats`, `quotaexceeded`, `usedquota`, `resyncqueuelen`, `chunklockstoresize`, `chunklockstore`, and `setrejectionrate`, while delegating common commands to `MsgHelperGenericDebug`. Helper methods inspect sessions, work queues, quota stores/devices, buddy resync queues, chunk locks, and config.

### Control Flow, State, And Persistence
Most commands are read-only snapshots. `setrejectionrate` mutates config runtime state. `usedquota` can query either each target separately or the aggregated quota block device map over a requested ID range. Resync queue and chunk lock commands require a target ID parsed from the command string.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on many app subsystems: sessions, queues, quota, target states, buddy resyncer, chunk locks, node stores, config, and ZFS quota sessions. Risks include weak command parsing, unbounded text output for quota/lock listings, debug commands exposing sensitive state, and runtime mutation through a debug endpoint. Tests should cover every command, invalid/missing arguments, large quota ranges, no resync job, lock-store limits, and op-counter updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/GenericDebugMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/GenericDebugMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/GenericDebugMsgEx.h

### Purpose
`GenericDebugMsgEx.h` declares the storage-side generic debug handler and its command-specific helper methods.

### Important APIs, Types, And Functions
The class derives from `GenericDebugMsg`, overrides `processIncoming()`, and declares private helpers for command dispatch, open-file listing, version, queue stats, quota exceeded, used quota, resync queue length, chunk lock store size/content, and rejection-rate setting.

### Control Flow, State, And Persistence
The handler stores no additional data. Each command uses inherited command string data and samples or mutates global app subsystems.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on the common node debug message and is factory-created for `NETMSGTYPE_GenericDebug`. Risks are mostly in command surface growth and keeping helper declarations aligned with `.cpp` dispatch. Tests should validate command dispatch coverage and unknown command response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/GenericDebugMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/GetClientStatsV2MsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/GetClientStatsV2MsgEx.cpp

### Purpose
`GetClientStatsV2MsgEx.cpp` returns per-client or per-user storage operation statistics for monitoring/control clients.

### Important APIs, Types, And Functions
`processIncoming()` obtains `StorageNodeOpStats`, checks `GETCLIENTSTATSMSG_FLAG_PERUSERSTATS`, calls `mapToUInt128Vec(getCookieIP(), GETCLIENTSTATSRESP_MAX_PAYLOAD_LEN, wantPerUserStats, &opStatsVec)`, and replies with `GetClientStatsV2RespMsg`.

### Control Flow, State, And Persistence
The handler is read-only. The cookie IP selects the continuation/filtering point for stats export, and payload length caps the vector.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `StorageNodeOpStats`, `UInt128` vectors, and common response messages. Risks include payload truncation/continuation correctness and large stats maps changing while exported. Tests should cover per-user flag, cookie continuation, empty stats, max payload boundary, and response serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/GetClientStatsV2MsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/GetClientStatsV2MsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/GetClientStatsV2MsgEx.h

### Purpose
`GetClientStatsV2MsgEx.h` declares the storage-side client statistics request handler.

### Important APIs, Types, And Functions
The class inherits `GetClientStatsV2Msg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
No extra state is defined. The request fields from the base control stats export behavior.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on common storage errors and the common node stats request. Tests should confirm factory creation and stats response behavior through the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/GetClientStatsV2MsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/GetTargetConsistencyStatesMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/GetTargetConsistencyStatesMsgEx.cpp

### Purpose
`GetTargetConsistencyStatesMsgEx.cpp` returns the storage daemon's current consistency state for requested target IDs.

### Important APIs, Types, And Functions
`processIncoming()` obtains `StorageTargets`, transforms `targetIDs` into a `TargetConsistencyStateVec`, maps unknown targets to `TargetConsistencyState_BAD`, and sends `GetTargetConsistencyStatesRespMsg`.

### Control Flow, State, And Persistence
The handler is read-only. It preserves request order in the returned state vector.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `StorageTargets` and common target-state response messages. Risks include treating unknown targets as BAD rather than returning an explicit error, which callers must interpret correctly. Tests should cover known good/needs-resync/bad states, unknown target IDs, empty requests, and response order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/GetTargetConsistencyStatesMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/GetTargetConsistencyStatesMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/GetTargetConsistencyStatesMsgEx.h

### Purpose
`GetTargetConsistencyStatesMsgEx.h` declares the storage-side target consistency state query handler.

### Important APIs, Types, And Functions
The class derives from `GetTargetConsistencyStatesMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
No additional state is introduced; inherited `targetIDs` drive the response.

### Dependencies, Integration Points, Risks, And Test Signals
It is created by the message factory for `NETMSGTYPE_GetTargetConsistencyStates`. Tests should validate virtual dispatch and unknown-target behavior implemented in the `.cpp`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/GetTargetConsistencyStatesMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/HeartbeatMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/HeartbeatMsgEx.cpp

### Purpose
`HeartbeatMsgEx.cpp` handles incoming node heartbeat messages and updates the storage daemon's node stores. It discovers or refreshes meta, management, and storage nodes.

### Important APIs, Types, And Functions
`processIncoming()` builds a `Node` from heartbeat fields and NIC list, applies local NIC capabilities to its connection pool, selects the appropriate `AbstractNodeStore` by node type, calls `addOrUpdateNode()`, logs newly added nodes and RDMA support, acknowledges the message, and updates `StorageOpCounter_HEARTBEAT`.

### Control Flow, State, And Persistence
Invalid node types are logged and still fall through to acknowledgement. Node store membership is persistent runtime cluster state. The method moves the constructed node into the selected store.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on network interface capability helpers, node stores, `Node`, acknowledgement support, and op stats. Risks include acknowledging invalid node types, stale NIC capability assumptions, and node identity conflicts handled by the store. Tests should cover each node type, invalid type, new versus update logging, RDMA NIC detection, and acknowledgement behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/HeartbeatMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/HeartbeatMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/HeartbeatMsgEx.h

### Purpose
`HeartbeatMsgEx.h` declares the storage-side heartbeat handler.

### Important APIs, Types, And Functions
The class inherits `HeartbeatMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
The header defines no additional state. The base message carries node identity and NIC data used during processing.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on the common heartbeat message and the factory maps `NETMSGTYPE_Heartbeat` to this handler. Tests should confirm dispatch and node-store updates through the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/HeartbeatMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/HeartbeatRequestMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/HeartbeatRequestMsgEx.cpp

### Purpose
`HeartbeatRequestMsgEx.cpp` responds to heartbeat requests by sending this storage daemon's current heartbeat information.

### Important APIs, Types, And Functions
`processIncoming()` obtains the local node, local NIC list, and configured storage port, constructs a `HeartbeatMsg` with `NODETYPE_Storage`, sets UDP/TCP ports, sends it as the response, logs the peer IP, and updates heartbeat op stats.

### Control Flow, State, And Persistence
The handler is read-only and sends a full heartbeat response immediately. It does not update node stores because it represents the local node.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on config, local node state, heartbeat messages, and op stats. Risks include stale NIC list or port config at response time. Tests should validate alias, numeric ID, node type, NICs, ports, response send, and stats update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/HeartbeatRequestMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/HeartbeatRequestMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/HeartbeatRequestMsgEx.h

### Purpose
`HeartbeatRequestMsgEx.h` declares the storage-side heartbeat request responder.

### Important APIs, Types, And Functions
The class derives from `HeartbeatRequestMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
No additional state is stored. The handler synthesizes a heartbeat from app-local node/config state.

### Dependencies, Integration Points, Risks, And Test Signals
It is factory-created for `NETMSGTYPE_HeartbeatRequest`. Tests should confirm the response message fields and virtual dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/HeartbeatRequestMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/MapTargetsMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/MapTargetsMsgEx.cpp

### Purpose
`MapTargetsMsgEx.cpp` handles target-to-node mapping updates from management. It maps one or more storage target IDs to a storage node and storage pool.

### Important APIs, Types, And Functions
`processIncoming()` retrieves the requested node ID and target/pool map, calls `TargetMapper::mapTarget()` for each target, stores each `FhgfsOpsErr` in a results map, logs new mappings with non-success results when applicable, and either acknowledges or sends `MapTargetsRespMsg`.

### Control Flow, State, And Persistence
The target mapper is mutated for each requested target. The response path depends on `acknowledge(ctx)`: if the message was not acknowledged, a detailed response is sent.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `TargetMapper`, storage node store, map-target response messages, and acknowledgement behavior. Risks include partial success across targets, logging condition that may be counterintuitive, and caller handling of ack versus response mode. Tests should cover single and multi-target mapping, pool ID propagation, partial failures, ackable requests, and result-map contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/MapTargetsMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/MapTargetsMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/MapTargetsMsgEx.h

### Purpose
`MapTargetsMsgEx.h` declares the storage-side target mapping handler.

### Important APIs, Types, And Functions
The class inherits `MapTargetsMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
No additional handler state is stored; inherited target mappings drive mapper mutations.

### Dependencies, Integration Points, Risks, And Test Signals
It is created for `NETMSGTYPE_MapTargets`. Tests should validate factory routing and mapper updates through the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/MapTargetsMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/PublishCapacitiesMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/PublishCapacitiesMsgEx.cpp

### Purpose
`PublishCapacitiesMsgEx.cpp` handles a management request to force capacity publication from the storage daemon.

### Important APIs, Types, And Functions
`processIncoming()` retrieves `InternodeSyncer`, calls `setForcePublishCapacities()`, acknowledges the request, and returns true.

### Control Flow, State, And Persistence
The handler mutates syncer scheduling state only; the actual capacity publication occurs asynchronously in the internode syncer.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `InternodeSyncer` and acknowledgement semantics. Risks are low; repeated requests only set a force flag. Tests should verify the force flag and acknowledgement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/PublishCapacitiesMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/PublishCapacitiesMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/PublishCapacitiesMsgEx.h

### Purpose
`PublishCapacitiesMsgEx.h` declares the storage-side handler for capacity publication triggers.

### Important APIs, Types, And Functions
It derives from `PublishCapacitiesMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
No additional state is stored; processing sets a flag in `InternodeSyncer`.

### Dependencies, Integration Points, Risks, And Test Signals
It is factory-created for `NETMSGTYPE_PublishCapacities`. Tests should validate dispatch and ack behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/PublishCapacitiesMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/RefreshTargetStatesMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/RefreshTargetStatesMsgEx.cpp

### Purpose
`RefreshTargetStatesMsgEx.cpp` handles requests to force a target state refresh.

### Important APIs, Types, And Functions
`processIncoming()` obtains `InternodeSyncer`, calls `setForceTargetStatesUpdate()`, acknowledges the message, and returns true.

### Control Flow, State, And Persistence
The method only changes scheduler state in the syncer. Target state fetching and persistence happen later in internode sync logic.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `InternodeSyncer` and common acknowledgement support. Tests should verify the force-update flag and acknowledgement behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/RefreshTargetStatesMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/RefreshTargetStatesMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/RefreshTargetStatesMsgEx.h

### Purpose
`RefreshTargetStatesMsgEx.h` declares the storage-side target-state refresh trigger.

### Important APIs, Types, And Functions
The class inherits `RefreshTargetStatesMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
The header has no state; the implementation sets an internode syncer flag.

### Dependencies, Integration Points, Risks, And Test Signals
It is created by the message factory for `NETMSGTYPE_RefreshTargetStates`. Tests should cover dispatch and ack.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/RefreshTargetStatesMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/RemoveBuddyGroupMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/RemoveBuddyGroupMsgEx.cpp

### Purpose
`RemoveBuddyGroupMsgEx.cpp` processes requests to remove a storage mirror buddy group mapping from this node, optionally checking that the mirror chunk directory is empty first.

### Important APIs, Types, And Functions
The file defines recursive helper `checkChunkDirRemovable(int dirFD)`, which walks a directory FD and returns success only if it contains no non-directory entries. `processIncoming()` validates storage node type, determines whether the local node owns the primary or secondary target of the group, opens the target mirror directory, runs the removability check, honors `force` and `checkOnly`, and calls `MirrorBuddyGroupMapper::unmapMirrorBuddyGroup()`.

### Control Flow, State, And Persistence
If the directory is empty, or not empty but `force` is set, the handler returns success and may unmap the group unless `checkOnly` is set. Persistent state mutation is the buddy group unmapping; chunk files are not deleted here.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on mirror buddy mappers, target mapper, storage targets, directory FDs, and `RemoveBuddyGroupRespMsg`. Risks include recursive FD handling, not closing nested `openat()` FDs before recursion returns, forced unmap with remaining chunks, and local ownership resolution if mapper data is stale. Tests should cover non-storage type, group not mapped locally, missing target, empty tree, nonempty tree, force, checkOnly, and stat/open failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/RemoveBuddyGroupMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/RemoveBuddyGroupMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/RemoveBuddyGroupMsgEx.h

### Purpose
`RemoveBuddyGroupMsgEx.h` declares the storage-side mirror buddy group removal handler.

### Important APIs, Types, And Functions
The class derives from `RemoveBuddyGroupMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
The handler has no additional data members; inherited fields such as group ID, node type, force, and check-only drive processing.

### Dependencies, Integration Points, Risks, And Test Signals
It is factory-created for `NETMSGTYPE_RemoveBuddyGroup`. Tests should validate response codes and mapper changes through the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/RemoveBuddyGroupMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/RemoveNodeMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/RemoveNodeMsgEx.cpp

### Purpose
`RemoveNodeMsgEx.cpp` handles requests to remove a node from the storage daemon's runtime node store. The implementation only acts on storage nodes.

### Important APIs, Types, And Functions
`processIncoming()` logs the numeric node ID, references and deletes the node from `StorageNodes` when `getNodeType() == NODETYPE_Storage`, logs cluster node counts on success, acknowledges or sends `RemoveNodeRespMsg(0)`, and updates `StorageOpCounter_REMOVENODE`.

### Control Flow, State, And Persistence
Runtime cluster membership in `NodeStoreServers` is mutated. Non-storage node types are effectively acknowledged without store deletion.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on storage node store, common remove response, acknowledgement behavior, and op stats. Risks include dereferencing `node` in the success log if `referenceNode()` failed but `deleteNode()` returned true, and ignoring meta/mgmt removals. Tests should cover storage deletion success/failure, non-storage request, ack versus response mode, and op stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/RemoveNodeMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/RemoveNodeMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/RemoveNodeMsgEx.h

### Purpose
`RemoveNodeMsgEx.h` declares the storage-side node removal handler.

### Important APIs, Types, And Functions
The class inherits `RemoveNodeMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
No additional state is defined. Processing mutates node stores based on inherited node type and numeric ID fields.

### Dependencies, Integration Points, Risks, And Test Signals
It is instantiated for `NETMSGTYPE_RemoveNode`. Tests should verify factory dispatch and storage-node removal semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/RemoveNodeMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/SetMirrorBuddyGroupMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/SetMirrorBuddyGroupMsgEx.cpp

### Purpose
`SetMirrorBuddyGroupMsgEx.cpp` handles storage mirror buddy group mapping updates from management.

### Important APIs, Types, And Functions
`processIncoming()` ignores non-storage node type requests by returning success, then maps storage buddy groups with `MirrorBuddyGroupMapper::mapMirrorBuddyGroup(buddyGroupID, primaryTargetID, secondaryTargetID, localNodeID, allowUpdate, &newBuddyGroupID)`. It acknowledges or sends `SetMirrorBuddyGroupRespMsg`.

### Control Flow, State, And Persistence
The storage buddy group mapper is mutated for storage-node requests. The response includes the map result and possibly assigned new group ID.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `MirrorBuddyGroupMapper`, local node ID, common response message, and acknowledgement support. Risks include silently succeeding for meta buddy group requests on storage and caller interpretation of updated group IDs. Tests should cover initial map, allowed update, disallowed update, non-storage request, ackable request, and invalid target pairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/SetMirrorBuddyGroupMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/SetMirrorBuddyGroupMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/SetMirrorBuddyGroupMsgEx.h

### Purpose
`SetMirrorBuddyGroupMsgEx.h` declares the storage-side mirror buddy group mapping handler.

### Important APIs, Types, And Functions
The class derives from `SetMirrorBuddyGroupMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
The handler has no additional state; inherited group/target fields drive mapper updates.

### Dependencies, Integration Points, Risks, And Test Signals
It is factory-created for `NETMSGTYPE_SetMirrorBuddyGroup`. Tests should validate mapper mutation and response semantics in the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/SetMirrorBuddyGroupMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/SetTargetConsistencyStatesMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/SetTargetConsistencyStatesMsgEx.cpp

### Purpose
`SetTargetConsistencyStatesMsgEx.cpp` applies requested consistency states to local storage targets.

### Important APIs, Types, And Functions
`processIncoming()` validates that `getTargetIDs()` and `getStates()` have equal length, iterates them with `ZipIterRange`, resolves each `StorageTarget`, calls `target->setState(TargetConsistencyState(...))`, and replies with `SetTargetConsistencyStatesRespMsg`.

### Control Flow, State, And Persistence
The operation is sequential and stops at the first list-size mismatch or unknown target. Runtime target consistency state is mutated; persistence depends on `StorageTarget::setState()` internals outside this file.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `StorageTargets`, common response messages, and `ZipIterator`. Risks include partial updates before a later unknown target, no validation that state byte values are valid enum members, and all-or-first-error response semantics. Tests should cover length mismatch, unknown target, multiple target update, invalid state value, and response result codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/SetTargetConsistencyStatesMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/SetTargetConsistencyStatesMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/SetTargetConsistencyStatesMsgEx.h

### Purpose
`SetTargetConsistencyStatesMsgEx.h` declares the storage-side consistency-state setter.

### Important APIs, Types, And Functions
The class derives from `SetTargetConsistencyStatesMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
No extra state is declared. Inherited target and state lists determine the update sequence.

### Dependencies, Integration Points, Risks, And Test Signals
It is factory-created for `NETMSGTYPE_SetTargetConsistencyStates`. Tests should validate dispatch and target state mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/SetTargetConsistencyStatesMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/StorageBenchControlMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/StorageBenchControlMsgEx.cpp

### Purpose
`StorageBenchControlMsgEx.cpp` handles remote control of the storage benchmark operator. It starts, stops, queries, or cleans up benchmark runs.

### Important APIs, Types, And Functions
`processIncoming()` switches on `getAction()`: `START` calls `initAndStartStorageBench()`, `STOP` calls `stopBenchmark()`, `STATUS` fills results through `getStatusWithResults()`, and `CLEANUP` calls `cleanup()`. It chooses an error code from the command result or the operator's last run error, then replies with `StorageBenchControlMsgResp`.

### Control Flow, State, And Persistence
The handler mutates benchmark operator state and may create/delete benchmark files through operator methods. Status requests are read-only. Unknown actions only log an error and still send a response using operator status and last error.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `StorageBenchOperator`, benchmark request/response types, and target lists. Risks include unknown actions not setting an explicit command error, concurrent benchmark commands, and result map size for large target sets. Tests should cover each action, command failure versus last-run error precedence, unknown action, and response status/type fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/StorageBenchControlMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/StorageBenchControlMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/StorageBenchControlMsgEx.h

### Purpose
`StorageBenchControlMsgEx.h` declares the storage-side benchmark control handler.

### Important APIs, Types, And Functions
The class derives from `StorageBenchControlMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
The header stores no state. Action fields from the base request control benchmark operator mutations.

### Dependencies, Integration Points, Risks, And Test Signals
It is created for `NETMSGTYPE_StorageBenchControlMsg`. Tests should verify factory routing and all action responses through the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/StorageBenchControlMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/storagepools/RefreshStoragePoolsMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/storagepools/RefreshStoragePoolsMsgEx.cpp

### Purpose
`RefreshStoragePoolsMsgEx.cpp` handles management requests to force storage pool information refresh.

### Important APIs, Types, And Functions
`processIncoming()` calls `Program::getApp()->getInternodeSyncer()->setForceStoragePoolsUpdate()` and acknowledges the request.

### Control Flow, State, And Persistence
Only internode syncer scheduling state is changed. Actual storage pool data refresh occurs asynchronously.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `InternodeSyncer` and acknowledgement behavior. The comment notes it should only arrive as an acknowledgement-capable message from management. Tests should verify force flag setting and ack path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/storagepools/RefreshStoragePoolsMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/storagepools/RefreshStoragePoolsMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/nodes/storagepools/RefreshStoragePoolsMsgEx.h

### Purpose
`RefreshStoragePoolsMsgEx.h` declares the storage-side storage-pool refresh trigger.

### Important APIs, Types, And Functions
The class inherits `RefreshStoragePoolsMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
No additional state exists; processing sets a force-refresh flag in the internode syncer.

### Dependencies, Integration Points, Risks, And Test Signals
It is factory-created for `NETMSGTYPE_RefreshStoragePools`. Tests should validate dispatch and acknowledgement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/nodes/storagepools/RefreshStoragePoolsMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/session/FSyncLocalFileMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/session/FSyncLocalFileMsgEx.cpp

### Purpose
`FSyncLocalFileMsgEx.cpp` handles fsync requests for open local chunk file sessions. It optionally performs cache-loss session checks and supports buddy mirror target resolution.

### Important APIs, Types, And Functions
`processIncoming()` replies with `FSyncLocalFileRespMsg(fsync())`. `fsync()` resolves mirror buddy group targets when `FSYNCLOCALFILEMSG_FLAG_BUDDYMIRROR` is set, references or creates the client session, looks up `SessionLocalFile`, calls `MsgHelperIO::fsync()` unless `FSYNCLOCALFILEMSG_FLAG_NO_SYNC` is set, and returns storage-crash errors when session checks indicate lost state.

### Control Flow, State, And Persistence
Non-mirror messages can use `FSYNCLOCALFILEMSG_FLAG_SESSION_CHECK`; mirror sessions skip that check. Persistent effects are the filesystem sync of an open FD and possible session creation. Missing session is only an error when session check is enabled.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on sessions, mirror buddy mapper, `SessionLocalFileStore`, and `MsgHelperIO`. Risks include creating sessions for fsync-only requests, invalid mirror groups flowing to failed lookup, and treating closed/missing files as success without session check. Tests should cover normal fsync, no-sync flag, mirror primary/secondary resolution, missing session with/without session check, crashed sessions, and fsync failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/session/FSyncLocalFileMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/session/FSyncLocalFileMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/session/FSyncLocalFileMsgEx.h

### Purpose
`FSyncLocalFileMsgEx.h` declares the storage-side fsync handler for local chunk file sessions.

### Important APIs, Types, And Functions
The class derives from `FSyncLocalFileMsg`, overrides `processIncoming(ResponseContext&)`, and has a private `fsync()` helper returning `FhgfsOpsErr`.

### Control Flow, State, And Persistence
The handler has no additional data members. Inherited session, handle, target, and feature flags drive fsync behavior.

### Dependencies, Integration Points, Risks, And Test Signals
It is factory-created for `NETMSGTYPE_FSyncLocalFile`. Tests should validate response codes and session lookup behavior implemented in the `.cpp`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/session/FSyncLocalFileMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/session/opening/CloseChunkFileMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/session/opening/CloseChunkFileMsgEx.cpp

### Purpose
`CloseChunkFileMsgEx.cpp` handles closing a chunk file session and returning dynamic chunk attributes. For buddy mirrored chunks, it forwards the close to the secondary before closing locally.

### Important APIs, Types, And Functions
`processIncoming()` calls `close(ctx)`, sends `CloseChunkFileRespMsg` unless a communication error response was already sent, and updates close op stats. `close()` resolves mirror target IDs, calls `forwardToSecondary()`, removes the session from `SessionLocalFileStore`, closes the FD when the session is no longer shared, and collects dynamic attributes either by FD or by path. `getDynamicAttribsByFD()` and `getDynamicAttribsByPath()` lock `SyncedStoragePaths` to pair file stats with a storage version.

### Control Flow, State, And Persistence
If the request is for the primary of a mirrored group, `forwardToSecondary()` reuses the same message with the secondary flag set and sends it through `MessagingTk::requestResponseTarget()`. Offline secondary is tolerated; other forwarding errors send a `GenericResponseMsg`. Persistent effects are closing session FDs, releasing session state, and possibly changing secondary session state.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include sessions, mirror mappers, target state/store routing, `StorageTkEx`, `SessionTk`, and synchronized storage paths. Risks include reusing and mutating `this` for forwarding, races when collecting path attributes for still-open files, early versus late stat differences, and GenericResponse communication semantics. Tests should cover local close, shared session virtual close, early/late stat config, no dynamic attribs flag, primary-to-secondary forwarding, offline secondary, secondary errors, and storage version locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/session/opening/CloseChunkFileMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/session/opening/CloseChunkFileMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/session/opening/CloseChunkFileMsgEx.h

### Purpose
`CloseChunkFileMsgEx.h` declares the storage-side close handler for chunk file sessions and its dynamic attribute response helpers.

### Important APIs, Types, And Functions
The class derives from `CloseChunkFileMsg` and overrides `processIncoming(ResponseContext&)`. Private `DynamicAttribs` carries size, allocated blocks, mtime, atime, and storage version. Helpers include `forwardToSecondary()`, `getDynamicAttribsByFD()`, `getDynamicAttribsByPath()`, and `close()`.

### Control Flow, State, And Persistence
The handler stores no persistent members; dynamic attributes are local to one request. The helper split reflects the two close paths: network mirror forwarding and local session/file cleanup.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on common close message definitions and storage implementation details in the `.cpp`. Tests should validate helper-return response behavior, especially communication errors that suppress the normal close response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/session/opening/CloseChunkFileMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/session/rw/ReadLocalFileRDMAMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/session/rw/ReadLocalFileRDMAMsgEx.h

### Purpose
`ReadLocalFileRDMAMsgEx.h` defines the NVFS/RDMA read specialization for the shared read-message template. It reads local chunk data and writes it directly into client-provided RDMA buffers.

### Important APIs, Types, And Functions
When `BEEGFS_NVFS` is enabled, `ReadLocalFileRDMAMsgSender` derives from `ReadLocalFileRDMAMsg` and defines `ReadState` with `RdmaInfo*`, remote buffer address, length, and offset. Template hooks include `sendLengthInfo()`, `readStateSendData()`, `getReadLength()`, `readStateInit()`, `readStateNext()`, and `getBuffers()`. The typedef `ReadLocalFileRDMAMsgEx` binds the sender to `ReadLocalFileMsgExBase`.

### Control Flow, State, And Persistence
The base read state machine performs file open/read/offset handling. This RDMA specialization obtains remote buffer descriptors via `RdmaInfo::next()`, caps each transfer to the current RDMA buffer and worker buffer size, writes data through `Socket::write()` with remote key, and sends final length over the socket.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on NVFS build flags, RDMA-capable sockets, `ReadLocalFileV2MsgEx.h`, and worker buffer sizes. Risks include remote buffer exhaustion, partial RDMA writes, alignment/length boundaries, and final length signaling after RDMA data. Tests require NVFS builds with valid/empty/multiple RDMA buffers, short remote writes, buffer boundary transitions, and fallback compile checks when NVFS is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/session/rw/ReadLocalFileRDMAMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/session/rw/ReadLocalFileV2MsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/session/rw/ReadLocalFileV2MsgEx.cpp

### Purpose
`ReadLocalFileV2MsgEx.cpp` implements the storage-side chunk read protocol. It opens or reuses a session-local file, reads requested ranges incrementally, sends length-framed data, updates session offsets before client-visible completion, and optionally triggers read-ahead.

### Important APIs, Types, And Functions
`ReadLocalFileMsgExBase::processIncoming()` resolves mirror targets, manages sessions, opens the chunk through `openFile()`, and calls `incrementalReadStatefulAndSendV2()`. `ReadLocalFileV2MsgSender::getBuffers()` reserves protocol space around the worker buffer. `incrementalReadStatefulAndSendV2()` calculates buffer-limited read lengths, uses `MsgHelperIO::pread()` unless disabled, sends data through template hooks, updates read counters and stats, and handles EOF/error length markers. `checkAndStartReadAhead()` uses sequential read counters.

### Control Flow, State, And Persistence
Session state includes FD, current offset, direct I/O flag, read counter, and last read-ahead trigger. Mirrored reads on non-good targets or unknown mirror targets return communication-style errors so clients can retry elsewhere. Persistent filesystem state is read-only; runtime counters and op stats are updated.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include sessions, mirror mappers, storage targets, `MsgHelperIO`, `StorageTkEx`, sockets, worker buffers, and optional RDMA linkage. Risks include offset races if updates happen after sends, protocol buffer size assumptions, handling `DISABLE_IO`, EOF framing, and read-ahead thresholds. Tests should cover existing/missing chunks, sequential and random reads, tiny buffers, EOF partial reads, disabled IO, direct IO, mirror target consistency failures, socket exceptions, and RDMA forced linkage builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/session/rw/ReadLocalFileV2MsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/session/rw/ReadLocalFileV2MsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/session/rw/ReadLocalFileV2MsgEx.h

### Purpose
`ReadLocalFileV2MsgEx.h` declares the generic read state machine and the TCP V2 read protocol specialization.

### Important APIs, Types, And Functions
`ReadStateBase` stores log context, remaining bytes, session file pointer, and last read result. `ReadLocalFileMsgExBase<Msg, ReadState>` provides common `processIncoming()`, `openFile()`, read-ahead, and incremental read/send helpers, delegating protocol-specific hooks to `Msg`. `ReadLocalFileV2MsgSender` implements length-framed socket sending and buffer layout. The typedef `ReadLocalFileV2MsgEx` binds them.

### Control Flow, State, And Persistence
The CRTP-like design lets TCP V2 and RDMA variants share session and file I/O behavior while customizing data transport. The V2 protocol sends an int64 length before each chunk and a zero final length marker after the last chunk.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on common read message definitions, `SessionLocalFileStore`, storage errors, and storage targets. Risks include template interface drift, inline delegation hiding compile errors until instantiation, and protocol framing assumptions. Tests should instantiate both TCP and RDMA variants where available, verify length framing, and exercise invalid message checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/session/rw/ReadLocalFileV2MsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/session/rw/WriteLocalFileMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/session/rw/WriteLocalFileMsgEx.cpp

### Purpose
`WriteLocalFileMsgEx.cpp` implements storage-side chunk writes. It receives client data incrementally, enforces quota, opens/creates chunk files, forwards mirrored writes to the secondary, writes locally, handles retries at safe points, and returns byte counts or negative BeeGFS errors.

### Important APIs, Types, And Functions
`WriteLocalFileMsgExBase::processIncoming()` validates the message, calls `write()`, sends a protocol-specific response, and updates write op stats. `write()` resolves mirror targets, manages `SessionLocalFile`, checks session-crash state, enforces quota, locks chunks during buddy resync, opens files through `openFile()`, prepares mirroring through `prepareMirroring()`, performs `incrementalRecvAndWriteStateful()`, and calls `finishMirroring()`. Helpers include `doWrite()`, `incrementalRecvPadding()`, `sendToMirror()`, and `doSessionCheck()`.

### Control Flow, State, And Persistence
Data is received in buffer-sized chunks, optionally forwarded to the mirror before local `pwrite()`, and then written at tracked offsets. On early errors, the handler drains the remaining client payload to keep the stream protocol aligned. Mirroring prepares a secondary write message and can retry only before any client payload is irrecoverably consumed. Persistent effects are chunk creation/writes, quota-aware creation, target buddy-needs-resync marking, and session offset/counter state.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include sessions, chunk locks, quota stores, storage targets, mirror mappers, target states, `MessagingTk`, sockets, and `MsgHelperIO`. Risks are high: mirror retry boundaries, partial writes, quota race/error mapping, chunk lock release, stream padding after failures, session-crash signaling, and `mirrorToSock` lifecycle. Tests should cover local writes, quota exceeded, missing/unknown targets, mirrored secondary online/offline/unclear, mirror partial write, socket exceptions, disabled IO, direct IO buffer sizing, short `pwrite()`, and payload draining.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/session/rw/WriteLocalFileMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/session/rw/WriteLocalFileMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/session/rw/WriteLocalFileMsgEx.h

### Purpose
`WriteLocalFileMsgEx.h` declares the generic write state machine and TCP write protocol specialization for storage chunk writes.

### Important APIs, Types, And Functions
`WriteStateBase` stores receive sizing, remaining bytes, write offset, and session file pointer. `WriteLocalFileMsgExBase<Msg, WriteState>` owns `mirrorToSock`, `mirrorRetriesLeft`, and shared write helpers: `write()`, `doWrite()`, `openFile()`, mirroring setup/send/finish, session checking, incremental receive/write, and receive-padding. `WriteLocalFileMsgSender` implements TCP receive and `WriteLocalFileRespMsg` response hooks. The typedef `WriteLocalFileMsgEx` binds the TCP sender to the base.

### Control Flow, State, And Persistence
The CRTP design shares file/session/mirror logic between TCP and RDMA variants. `WRITEMSG_MIRROR_RETRIES_NUM` allows one mirror retry, but the implementation limits retry to safe pre-payload points.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on common write message/response classes, `SessionLocalFile`, storage errors, and sockets. Risks include template hook mismatch, raw socket pointer lifetime, integer sign conversions for negative error responses, and stateful retry counters per handler object. Tests should instantiate TCP/RDMA variants, validate response encoding, receive chunk sizing, and mirror retry counter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/session/rw/WriteLocalFileMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/session/rw/WriteLocalFileRDMAMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/session/rw/WriteLocalFileRDMAMsgEx.h

### Purpose
`WriteLocalFileRDMAMsgEx.h` defines the NVFS/RDMA write specialization. It reads client data from remote RDMA buffers and feeds the shared local write/mirror state machine.

### Important APIs, Types, And Functions
When `BEEGFS_NVFS` is enabled, `WriteLocalFileRDMAMsgSender` derives from `WriteLocalFileRDMAMsg` and defines `WriteState` with RDMA descriptor state plus original receive size. Hooks include `recvPadding()`, `sendResponse()` using `WriteLocalFileRDMARespMsg`, `writeStateInit()`, `writeStateRecvData()`, and `writeStateNext()`. The typedef `WriteLocalFileRDMAMsgEx` binds it to `WriteLocalFileMsgExBase`.

### Control Flow, State, And Persistence
The RDMA specialization advances through `RdmaInfo` remote buffers, caps each read to remaining request bytes, remaining RDMA buffer bytes, and `WORKER_BUFIN_SIZE`, and signals an error if RDMA buffers are exhausted before all data is received. Local persistence is handled by the shared base write path.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on NVFS build flags, RDMA socket read support, common RDMA messages/responses, and the write base template. Risks include RDMA buffer exhaustion, partial RDMA reads, inconsistent `recvSize` accounting, and compile-only coverage when NVFS is disabled. Tests should cover empty/multiple RDMA buffers, buffer-boundary transitions, short RDMA reads, response codes, and normal non-NVFS builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/session/rw/WriteLocalFileRDMAMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/GetHighResStatsMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/GetHighResStatsMsgEx.cpp

### Purpose
`GetHighResStatsMsgEx.cpp` serves high-resolution storage statistics history since a caller-provided timestamp.

### Important APIs, Types, And Functions
`processIncoming()` reads `lastStatsMS` from `getValue()`, calls `StatsCollector::getStatsSince(lastStatsMS, statsHistory)`, and sends `GetHighResStatsRespMsg`.

### Control Flow, State, And Persistence
The handler is read-only. It snapshots stats history from the collector into a response list.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `StatsCollector` and common high-res stats response messages. Risks include large responses if the timestamp is old and concurrent stats rotation. Tests should cover empty, partial, and full history windows plus serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/GetHighResStatsMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/GetHighResStatsMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/GetHighResStatsMsgEx.h

### Purpose
`GetHighResStatsMsgEx.h` declares the storage-side high-resolution stats query handler.

### Important APIs, Types, And Functions
The class derives from `GetHighResStatsMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
No additional state is declared; the base value acts as the last-stat timestamp.

### Dependencies, Integration Points, Risks, And Test Signals
It is factory-created for `NETMSGTYPE_GetHighResStats`. Tests should validate stats response construction through the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/GetHighResStatsMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/StatStoragePathMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/StatStoragePathMsgEx.cpp

### Purpose
`StatStoragePathMsgEx.cpp` handles statfs-style requests for a storage target path. It returns total/free bytes and inode counts.

### Important APIs, Types, And Functions
`processIncoming()` calls `statStoragePath()` and responds with `StatStoragePathRespMsg`, then updates `StorageOpCounter_STATSTORAGEPATH`. `statStoragePath()` resolves the target, calls `StorageTk::statStoragePath()`, applies manual free-space override through `StorageTk::statStoragePathOverride()`, and returns a BeeGFS error code.

### Control Flow, State, And Persistence
The handler is read-only except op counters. Unknown targets return `UNKNOWNTARGET`; statfs failures return `INTERNAL`. Override files can change reported free space/inodes without changing the actual filesystem.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `StorageTargets`, `StorageTk`, response messages, and op stats. Risks include override semantics, statfs failure handling, and path lifetime from target configuration. Tests should cover valid target stats, unknown target, statfs failure, override file behavior, and op-counter updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/StatStoragePathMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/StatStoragePathMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/StatStoragePathMsgEx.h

### Purpose
`StatStoragePathMsgEx.h` declares the storage-side statfs target path handler.

### Important APIs, Types, And Functions
The class inherits `StatStoragePathMsg`, overrides `processIncoming(ResponseContext&)`, and declares private helper `statStoragePath()` for byte/inode outputs.

### Control Flow, State, And Persistence
The handler has no member state. It fills caller-provided output pointers during request handling.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on common storage errors and stat request messages. Tests should validate helper result codes and response field population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/StatStoragePathMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/TruncLocalFileMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/TruncLocalFileMsgEx.cpp

### Purpose
`TruncLocalFileMsgEx.cpp` handles chunk truncation and extension requests. It supports normal and buddy-mirrored chunks, creates missing chunks when extending, forwards primary mirror operations to the secondary, and returns dynamic attributes with storage versions.

### Important APIs, Types, And Functions
`processIncoming()` resolves target IDs and FDs, validates mirrored consistency through `getTargetFD()`, forwards to secondary with `forwardToSecondary()`, builds chunk paths via `StorageTk::getChunkDirChunkFilePath()`, calls `truncFile()`, and returns `TruncLocalFileRespMsg`. `truncFile()` uses `MsgHelperIO::truncateAt()`, creates missing files through `ChunkStore::openChunkFile()` with quota info, retries chmod for quota owner issues, and calls `ftruncate()`. Attribute helpers use `SyncedStoragePaths`.

### Control Flow, State, And Persistence
For mirrored primary requests, the message is reused with the secondary flag set. If the secondary is offline or reports unknown target, local truncation proceeds and the target is marked needing resync. If buddy resync is in progress, the chunk is locked around forwarding/local work. Persistent effects include truncating or creating chunk files, setting buddy-needs-resync, and possible quota-aware directory/file creation.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include storage targets, mirror mappers, target states, chunk store, quota stores, synchronized paths, and `MessagingTk`. Risks include reused message mutation, complex response suppression for `GenericResponseMsg`, lock release on all branches, zero-size missing-file fake attributes, and partial success when secondary differs from primary. Tests should cover normal shrink/extend, missing zero-size truncation, create-and-truncate, quota errors, mirrored secondary online/offline/unknown, non-good primary consistency, resync chunk locking, and dynamic attribute storage versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/TruncLocalFileMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/TruncLocalFileMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/TruncLocalFileMsgEx.h

### Purpose
`TruncLocalFileMsgEx.h` declares the storage-side truncation handler and helpers for mirrored forwarding, local truncation, and dynamic attribute responses.

### Important APIs, Types, And Functions
The class derives from `TruncLocalFileMsg` and overrides `processIncoming(ResponseContext&)`. `DynamicAttribs` initializes size, block count, timestamps, and storage version to zero. Helpers include `truncFile()`, `getTargetFD()`, `getDynamicAttribsByPath()`, `getFakeDynAttribs()`, and `forwardToSecondary()`.

### Control Flow, State, And Persistence
The header stores no request-independent state. Helper signatures show the operation's phases: target FD validation, local filesystem mutation, attribute collection, and mirror forwarding.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on common truncation messages, storage errors, paths, and `StorageTarget`. Tests should validate each helper branch through the `.cpp`, especially response suppression and storage version generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/TruncLocalFileMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/attribs/GetChunkFileAttribsMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/attribs/GetChunkFileAttribsMsgEx.cpp

### Purpose
`GetChunkFileAttribsMsgEx.cpp` handles requests for dynamic attributes of a chunk file: size, allocated blocks, modification/access times, and storage version.

### Important APIs, Types, And Functions
`processIncoming()` resolves mirror buddy group targets, handles unknown targets, validates mirrored target consistency with `getTargetFD()`, builds the chunk path with `StorageTk::getFileChunkPath()`, locks the path through `SyncedStoragePaths::lockPath()`, calls `fstatat()`, and replies with `GetChunkFileAttribsRespMsg`. `getTargetFD()` chooses normal or mirror FD and can send `GenericResponseMsg` for non-good mirrored primaries.

### Control Flow, State, And Persistence
The handler is read-only except for path storage-version locking and op stats. Missing files are not treated as errors; the response has zero storage version, so metadata should avoid updating from absent data.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on storage targets, mirror mappers, target consistency state, synchronized storage paths, `StorageTk`, and op stats. Risks include response suppression after `GenericResponseMsg`, correctness of storage version with concurrent truncation/write, and non-error missing-file semantics. Tests should cover existing file, missing file, unknown normal target, unknown mirror target, non-good mirror primary, secondary flag, stat errors, and storage version locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/attribs/GetChunkFileAttribsMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/attribs/GetChunkFileAttribsMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/attribs/GetChunkFileAttribsMsgEx.h

### Purpose
`GetChunkFileAttribsMsgEx.h` declares the storage-side chunk dynamic attribute query handler.

### Important APIs, Types, And Functions
The class derives from `GetChunkFileAttribsMsg`, overrides `processIncoming(ResponseContext&)`, and declares private helper `getTargetFD(const StorageTarget&, ResponseContext&, bool*)`.

### Control Flow, State, And Persistence
No state is stored in the handler. The helper's `outResponseSent` contract supports early `GenericResponseMsg` replies when mirrored target consistency is unsuitable.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on common get-attribs message definitions and `StorageTarget`. Tests should validate normal response, early response suppression, and target FD selection for normal and mirrored chunks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/attribs/GetChunkFileAttribsMsgEx.h -->
