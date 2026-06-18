# Research Group subset-b-000551

This grouped report covers the 80 source files assigned to `subset-b-000551`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncJob.cpp -->
# sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncJob.cpp

## Purpose
Implements the metadata buddy resync job thread. It coordinates a full resync of the local metadata mirror subtree to the buddy metadata node, captures concurrent mirrored mutations, resyncs mirrored sessions, and finally publishes the buddy consistency result.

## Important APIs And Types
Key APIs are the constructor, run(), abort(), startGatherSlaves(), startSyncSlaves(), stopAllWorkersOn(), getJobStats(), newBuddyState(), informBuddy(), and informMgmtd(). The constructor resolves the buddy node, sizes bulk sync slaves from tuneNumResyncSlaves, and creates gather, bulk, modification, and session-store resync helpers. threadCount tracks mirrored request handlers that have registered in-flight changesets.

## Control Flow
run() clears candidates, resolves the buddy, optionally triggers debug termination, blocks all workers with BarrierWork, sends StorageResyncStartedMsg, transitions to RUNNING, marks InternodeSyncer resync-in-progress, starts gather and sync slaves, releases the initial worker barrier, joins the gatherer, lets bulk syncers drain, conditionally blocks workers again for session quiescence, drains the modification sync slave, performs session-store sync, collects errors, clears the needs-resync marker, informs buddy and management of GOOD or BAD, restarts workers, and on errors drains pending modification candidates so waiting workers can complete. abort() marks INTERRUPTED, terminates slaves, and optionally waits for registered worker operations while signaling queued changesets.

## State And Persistence
State lives in BuddyResyncJobState guarded by stateMutex plus start/end timestamps, sync candidate queues, per-slave atomic counters, session sync counters, and the meta-path needs-resync marker. The job persists no new object itself, but it drives remote raw-inode/session replacement and target consistency state changes on the buddy and management services.

## Dependencies And Integration Points
Depends on Program/App singletons, InternodeSyncer, MetaStore paths under the buddy mirror subtree, EntryLockStore locking, SyncCandidateStore queues, MessagingTk request/response, ResyncRawInodes/ResyncSessionStore messages, target state stores, and worker barriers.

## Risks And Edge Cases
The barrier choreography is deadlock-sensitive: workers must be stopped only where no mod-sync queue waiters can block forever. abort(true) depends on threadCount and queue signaling to unblock mirrored operations. A communication failure before StorageResyncStarted or during final state updates can leave the buddy needing another resync. Statistics aggregation assumes slave counters are stable after isRunning clears.

## Test Signals
Exercise successful resync, missing buddy node, StorageResyncStarted failure, bulk sync failure, mod sync failure, abort(false/true), worker barrier release, session sync failure, and final GOOD/BAD propagation. Debug variables BEEGFS_RESYNC_DIE_AT_N and BEEGFS_DEBUG_FAIL_MODSYNC are useful fault-injection signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncJob.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncJob.h -->
# sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncJob.h

## Purpose
Declares the PThread that owns one metadata buddy resync lifecycle and exposes status, abort, enqueue, and statistics access to the BuddyResyncer and mirrored message layer.

## Important APIs And Types
Exports BuddyResyncJob, run(), abort(bool), getJobStats(), isRunning(), getState(), enqueue(MetaSyncCandidateFile,PThread*), registerOps(), unregisterOps(), and private helper declarations for slave startup, state publication, and worker barriers. The class owns MetaSyncCandidateStore plus unique_ptr gather, bulk, mod, and SessionStoreResyncer helpers.

## Control Flow
Callers start the thread once, enqueue modification candidates while it is running, and may abort or query stats. Private helpers are used only by run() and the slave orchestration path.

## State And Persistence
The header defines the ownership and concurrency surface: state is Mutex-protected, threadCount is atomic, timestamps are integral, and candidate queues bridge worker operations to resync slaves. It does not persist data directly.

## Dependencies And Integration Points
Depends on Program/App singletons, InternodeSyncer, MetaStore paths under the buddy mirror subtree, EntryLockStore locking, SyncCandidateStore queues, MessagingTk request/response, ResyncRawInodes/ResyncSessionStore messages, target state stores, and worker barriers.

## Risks And Edge Cases
getResyncJob callers receive a raw pointer owned by BuddyResyncer; the pointer must not outlive the job. registerOps()/unregisterOps() must stay balanced or abort(true) can wait until retry exhaustion. enqueue relies on the caller-provided PThread for candidate-store blocking semantics.

## Test Signals
Compile coverage should verify forward declarations and ownership types. Behavioral tests should check state transitions, balanced op registration around mirrored requests, and that stats can be queried during and after a job.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncJob.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncer.cpp -->
# sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncer.cpp

## Purpose
Implements the manager for metadata buddy resync jobs and the thread-local modification changeset bridge used by mirrored request processing.

## Important APIs And Types
Key APIs are startResync(), shutdown(), destructor cleanup, commitThreadChangeSet(), and the __thread currentThreadChangeSet storage. startResync creates or replaces BuddyResyncJob instances while guarding with jobMutex. commitThreadChangeSet transfers the current thread-local MetaSyncCandidateFile into the active job and waits on a Barrier until the mod-sync slave has processed it.

## Control Flow
startResync refuses new starts after shutdown, returns INUSE while a job is NOTSTARTED/RUNNING or still cannot join quickly, deletes completed jobs, and starts a fresh one. shutdown atomically detaches the job pointer, disables new jobs, aborts, and joins. commitThreadChangeSet validates a changeset exists, prepares a two-party barrier, enqueues it, and waits for the mod-sync path to signal completion.

## State And Persistence
State consists of the raw job pointer, noNewResyncs flag, jobMutex, and TLS changeset pointer. Persistent metadata is affected indirectly through queued changesets during resync.

## Dependencies And Integration Points
Depends on Program/App singletons, InternodeSyncer, MetaStore paths under the buddy mirror subtree, EntryLockStore locking, SyncCandidateStore queues, MessagingTk request/response, ResyncRawInodes/ResyncSessionStore messages, target state stores, and worker barriers.

## Risks And Edge Cases
The raw pointer is protected only by jobMutex at access time; users must avoid keeping it beyond safe contexts. commitThreadChangeSet assumes an active job exists and will signal the prepared barrier. The destructor aborts without waiting for completion-specific cleanup beyond join.

## Test Signals
Tests should cover duplicate start attempts, restart after a completed job, shutdown racing with start, TLS changeset registration/abandon/commit, and barrier signaling by the mod-sync path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncer.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncer.h -->
# sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncer.h

## Purpose
Declares the non-thread component that owns the currently active metadata BuddyResyncJob and exposes static TLS helpers for mirrored operations to collect changes while resync is active.

## Important APIs And Types
Important APIs are startResync(), shutdown(), getResyncJob(), commitThreadChangeSet(), registerSyncChangeset(), abandonSyncChangeset(), and getSyncChangeset(). The class intentionally disallows copying.

## Control Flow
External code starts or shuts down the current job through this facade. MirroredMessage registers a MetaSyncCandidateFile in TLS, operation implementations add modifications/deletions to it, and finish paths either commit or abandon it.

## State And Persistence
The job pointer is manager-owned and guarded by jobMutex. The TLS changeset is per worker thread and must be cleared on all exits. No durable state is written here.

## Dependencies And Integration Points
Depends on Program/App singletons, InternodeSyncer, MetaStore paths under the buddy mirror subtree, EntryLockStore locking, SyncCandidateStore queues, MessagingTk request/response, ResyncRawInodes/ResyncSessionStore messages, target state stores, and worker barriers.

## Risks And Edge Cases
The manager exposes a raw job pointer; lifetime is safe only if callers follow existing locking/lifecycle assumptions. Forgetting to abandon a changeset leaks memory and can duplicate resync records; double registration is guarded by BEEGFS_BUG_ON.

## Test Signals
Unit or integration tests should include resync start lifecycle, shutdown idempotency, and mirrored-operation changeset cleanup on success, non-mutating responses, and early exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncer.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncerBulkSyncSlave.cpp -->
# sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncerBulkSyncSlave.cpp

## Purpose
Implements the bulk metadata sync slave that streams whole directory/hash-directory contents from the local buddy-mirror tree to the secondary during resync.

## Important APIs And Types
Key APIs are syncLoop(), resyncDirectory(), and streamCandidateDir(). It consumes MetaSyncCandidateDir objects, uses HashDirLock/FileIDLock/ParentNameLock as appropriate, and relies on SyncSlaveBase helpers to stream inode and dentry packets over ResyncRawInodes.

## Control Flow
syncLoop fetches directory candidates until termination. Hash directory candidates are locked by hash tuple and synced directly. Content directories lock the owning directory inode, skip cleanly if the directory disappeared, sync the #fSiDs# directory first, then sync the content directory. streamCandidateDir opens the candidate directory, iterates entries, ignores dot entries and ENOENT races, validates file/dir types, streams content-directory dentries under ParentNameLock, and streams inode hash entries under FileIDLock. It ends each stream with an empty packet.

## State And Persistence
Updates atomic counters for directories/files synced and dir/file errors. It does not mutate local metadata except lock state, but it causes remote raw inode/dentry replacement on the buddy.

## Dependencies And Integration Points
Depends on Program/App singletons, InternodeSyncer, MetaStore paths under the buddy mirror subtree, EntryLockStore locking, SyncCandidateStore queues, MessagingTk request/response, ResyncRawInodes/ResyncSessionStore messages, target state stores, and worker barriers.

## Risks And Edge Cases
Path parsing for hash locks assumes the expected two-level hex layout. Directory disappearance is tolerated only in selected cases. Any stream failure aborts the parent job. Long-running whole-directory streams have no timeout through SyncSlaveBase.

## Test Signals
Test with inode hash dirs, dentry hash dirs, content dirs with #fSiDs#, vanished entries, non-regular/non-directory entries, xattr-enabled metadata, and simulated ResyncRawInodesResp failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncerBulkSyncSlave.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncerBulkSyncSlave.h -->
# sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncerBulkSyncSlave.h

## Purpose
Declares the bulk resync slave used by BuddyResyncJob to process queued directory candidates and stream raw metadata to a buddy node.

## Important APIs And Types
Exports constructor, Stats, getStats(), syncLoop(), resyncDirectory(), streamCandidateDir(), and a static stream callback adapter. It inherits SyncSlaveBase and owns only a pointer to the shared MetaSyncCandidateStore plus atomic counters.

## Control Flow
The parent starts the thread, the thread fetches directories, and ResyncRawInodes uses streamCandidateDir as the streamout callback.

## State And Persistence
State is limited to queue pointer and four AtomicUInt64 counters. The class relies on parent-job lifetime for the queue and buddy node ID.

## Dependencies And Integration Points
Depends on Program/App singletons, InternodeSyncer, MetaStore paths under the buddy mirror subtree, EntryLockStore locking, SyncCandidateStore queues, MessagingTk request/response, ResyncRawInodes/ResyncSessionStore messages, target state stores, and worker barriers.

## Risks And Edge Cases
The static callback casts a void* tuple context, so type/ lifetime must match resyncDirectory. Queue ownership remains external. Counters are aggregate signals only; they do not identify failed paths.

## Test Signals
Compile tests should cover callback signature compatibility. Runtime tests should verify getStats after successful and failed directory streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncerBulkSyncSlave.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncerGatherSlave.cpp -->
# sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncerGatherSlave.cpp

## Purpose
Implements the gather phase of metadata buddy resync. It crawls the local buddy-mirror inode and dentry hash trees and queues directory candidates for bulk sync.

## Important APIs And Types
Key APIs are run(), workLoop(), and crawlDir(). The constructor records the meta buddy path. crawlDir performs recursive directory traversal and calls addCandidate from the header for second-level hash dirs and content dirs.

## Control Flow
run sets isRunning, installs signal handling, and calls workLoop. workLoop crawls inodes and dentries. crawlDir opens the path, reads entries, skips dot entries, stats children, reports unexpected non-directories, recurses from level 0 to level 1, queues level-1 hash dirs, recurses into dentry hash dirs at level 1, and queues content directories at level 2 while counting discovered dirs.

## State And Persistence
State consists of metaBuddyPath, queue pointer, isRunning condition, and atomic discovered/error counters. It only observes local directories and enqueues relative paths; it does not alter metadata.

## Dependencies And Integration Points
Depends on Program/App singletons, InternodeSyncer, MetaStore paths under the buddy mirror subtree, EntryLockStore locking, SyncCandidateStore queues, MessagingTk request/response, ResyncRawInodes/ResyncSessionStore messages, target state stores, and worker barriers.

## Risks And Edge Cases
Crawl semantics are tied to the on-disk layout of buddymir/inodes and buddymir/dentries. ENOENT is tolerated only for second-level dentry hash content dirs; other stat/open/read failures increment errors. A gather error drives final resync ERRORS state.

## Test Signals
Test empty trees, normal two-level hash trees, disappearing content dirs, non-directory entries, permission/open failures, and selfTerminate during traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncerGatherSlave.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncerGatherSlave.h -->
# sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncerGatherSlave.h

## Purpose
Declares the gatherer thread that discovers metadata resync directory candidates for BuddyResyncJob.

## Important APIs And Types
Exports constructor, workLoop(), getIsRunning(), Stats/getStats(), run(), crawlDir(), setIsRunning(), and addCandidate(). addCandidate converts absolute paths under metaBuddyPath to relative MetaSyncCandidateDir entries.

## Control Flow
BuddyResyncJob starts and joins the gatherer, waits on isRunningChangeCond during cleanup, and reads discovered/error counters for job stats.

## State And Persistence
The class stores thread running state under Mutex/Condition and counters as atomics. Candidate data is persisted only in the shared SyncCandidateStore.

## Dependencies And Integration Points
Depends on Program/App singletons, InternodeSyncer, MetaStore paths under the buddy mirror subtree, EntryLockStore locking, SyncCandidateStore queues, MessagingTk request/response, ResyncRawInodes/ResyncSessionStore messages, target state stores, and worker barriers.

## Risks And Edge Cases
addCandidate depends on path prefix correctness. The class gives BuddyResyncJob friend access to its synchronization internals. A missing or stale metaBuddyPath makes all relative candidates invalid.

## Test Signals
Tests should validate relative path conversion, running-state signaling, stats increments, and clean shutdown during crawl.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncerGatherSlave.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncerModSyncSlave.cpp -->
# sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncerModSyncSlave.cpp

## Purpose
Implements the modification resync slave that streams concurrent mirrored metadata changes captured while the bulk resync is running.

## Important APIs And Types
Key APIs are syncLoop(), streamCandidates(), CandidateSignaler, and resyncElemCmp(). It consumes MetaSyncCandidateFile changesets and uses SyncSlaveBase stream/delete helpers for inodes, directories, and dentries.

## Control Flow
syncLoop waits for file candidates and invokes resyncAt with wholeDirectory=false. streamCandidates drains queued changesets, wraps each candidate in a signaler so the waiting worker is released, sorts elements so deletions precede updates and inodes precede dentries, strips the buddymir prefix from paths, dispatches deletion/update by MetaSyncFileType, counts successes, and aborts the parent job on any stream failure or debug failure injection. Each stream is terminated with an empty packet.

## State And Persistence
State consists of queue pointer and atomic object/error counters. It serializes captured changes to the secondary and synchronizes worker progress through candidate barriers.

## Dependencies And Integration Points
Depends on Program/App singletons, InternodeSyncer, MetaStore paths under the buddy mirror subtree, EntryLockStore locking, SyncCandidateStore queues, MessagingTk request/response, ResyncRawInodes/ResyncSessionStore messages, target state stores, and worker barriers.

## Risks And Edge Cases
Sort order is correctness-critical for recreate/delete cases and dentry links to newly-created inodes. If path prefixes are malformed, itemPath is wrong. abort(true) from inside a stream can wait for other worker operations; CandidateSignaler is essential to avoid blocked request threads.

## Test Signals
Test deletion-before-update ordering, inode-before-dentry ordering, dentry/inode/directory update and deletion packets, worker barrier signaling, debug failure injection, and queue drain on termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncerModSyncSlave.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncerModSyncSlave.h -->
# sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncerModSyncSlave.h

## Purpose
Declares the modification resync slave for queued MetaSyncCandidateFile changesets captured by mirrored operations during resync.

## Important APIs And Types
Exports constructor, Stats/getStats(), syncLoop(), streamCandidates(Socket&), and a static callback adapter. It inherits SyncSlaveBase and stores a candidate queue pointer plus atomic counters.

## Control Flow
The parent job starts it alongside bulk slaves. ResyncRawInodes uses its static callback to stream file-level modification packets.

## State And Persistence
No durable state is held in the header; counters and queue linkage are runtime-only.

## Dependencies And Integration Points
Depends on Program/App singletons, InternodeSyncer, MetaStore paths under the buddy mirror subtree, EntryLockStore locking, SyncCandidateStore queues, MessagingTk request/response, ResyncRawInodes/ResyncSessionStore messages, target state stores, and worker barriers.

## Risks And Edge Cases
The queue is externally owned and must outlive the slave. The callback uses a raw void* context. Stats give only totals, not failed changeset details.

## Test Signals
Compile and integration tests should cover callback binding and stats after successful and failed modification sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncerModSyncSlave.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/SessionStoreResyncer.cpp -->
# sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/SessionStoreResyncer.cpp

## Purpose
Implements mirrored session-store resync after metadata bulk and modification sync have drained and workers are quiesced.

## Important APIs And Types
The main API is doSync(). It reads mirrored SessionStore size, serializes the store to a buffer, sends ResyncSessionStoreMsg to the buddy node with streamout hook registration, waits for ResyncSessionStoreRespMsg, and updates counters/errors.

## Control Flow
doSync obtains App, mirrored sessions, and meta node store; records the number of sessions to sync; serializes the complete session store; fails if serialization returns zero bytes; sends a request/response to the buddyNodeID; treats communication or non-success response as errors; and on success records all sessions synced.

## State And Persistence
State is the buddy node ID plus atomic session counts and one error flag. The operation replaces/updates remote session persistence on the buddy; local session state is read-only during this step.

## Dependencies And Integration Points
Depends on Program/App singletons, InternodeSyncer, MetaStore paths under the buddy mirror subtree, EntryLockStore locking, SyncCandidateStore queues, MessagingTk request/response, ResyncRawInodes/ResyncSessionStore messages, target state stores, and worker barriers.

## Risks And Edge Cases
The caller must ensure client operations are stopped or session state can change while being serialized. A zero-length serialized buffer is interpreted as failure, so an actually empty valid serialization must not use size zero. Response casting assumes the expected type from requestResponseNode.

## Test Signals
Test empty and non-empty session stores, serialization failure, communication failure, non-success response, and stats before/after doSync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/SessionStoreResyncer.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/SessionStoreResyncer.h -->
# sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/SessionStoreResyncer.h

## Purpose
Declares the helper that serializes and transfers mirrored session-store state during a metadata buddy resync.

## Important APIs And Types
Exports constructor, Stats/getStats(), and private doSync() for BuddyResyncJob. Stats include sessionsToSync, sessionsSynced, and errors.

## Control Flow
BuddyResyncJob invokes doSync only after bulk/modification sync phases and worker quiescence.

## State And Persistence
Runtime state is a NumNodeID and atomic counters. No ownership of SessionStore is taken.

## Dependencies And Integration Points
Depends on Program/App singletons, InternodeSyncer, MetaStore paths under the buddy mirror subtree, EntryLockStore locking, SyncCandidateStore queues, MessagingTk request/response, ResyncRawInodes/ResyncSessionStore messages, target state stores, and worker barriers.

## Risks And Edge Cases
Only friend classes can call doSync, so tests may need job-level integration. The error flag is coarse and records only one failure condition.

## Test Signals
Test stats initialization, successful transfer counts, and error flag on failed serialization or request.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/SessionStoreResyncer.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/SyncCandidate.h -->
# sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/SyncCandidate.h

## Purpose
Defines metadata resync candidate value types for directory bulk sync and file-level modification sync.

## Important APIs And Types
Important types are MetaSyncDirType, MetaSyncCandidateDir, MetaSyncFileType, SerializeAs<MetaSyncFileType>, MetaSyncCandidateFile::Element, and MetaSyncCandidateStore typedef. MetaSyncCandidateFile supports move semantics, addModification(), addDeletion(), releaseElements(), prepareSignal(), and signal().

## Control Flow
Gather slaves enqueue MetaSyncCandidateDir. Mirrored operations collect MetaSyncCandidateFile elements in TLS, prepare a barrier signal, enqueue to the job, and wait until the mod-sync slave signals completion.

## State And Persistence
Candidates are in-memory queue records. The Barrier pointer is non-owning and exists only to synchronize a worker with modification resync completion.

## Dependencies And Integration Points
Depends on Program/App singletons, InternodeSyncer, MetaStore paths under the buddy mirror subtree, EntryLockStore locking, SyncCandidateStore queues, MessagingTk request/response, ResyncRawInodes/ResyncSessionStore messages, target state stores, and worker barriers.

## Risks And Edge Cases
signal() assumes prepareSignal() has been called and barrier is non-null. releaseElements() moves the vector, making the candidate empty. Element path/type/isDeletion order semantics are enforced by the mod-sync slave, not by this data class.

## Test Signals
Test move construction/assignment, vector release, addModification/addDeletion values, enum serialization as uint8_t, and barrier signaling behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/SyncCandidate.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/SyncSlaveBase.cpp -->
# sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/SyncSlaveBase.cpp

## Purpose
Implements shared resync streaming behavior for buddy resync and chunk-balancer slave threads.

## Important APIs And Types
Key APIs are run(), receiveAck(), resyncAt(), streamDentry(), streamInode(), deleteDentry(), and deleteInode(). It creates ResyncRawInodesMsgEx requests and serializes raw dentry/inode packets plus optional user xattrs.

## Control Flow
run marks isRunning, registers signal handling, calls subclass syncLoop, catches component exceptions, and clears isRunning. resyncAt sets the base path under buddymir, sends ResyncRawInodesMsgEx with optional stream callback and no timeout, and returns the response result. streamDentry reads a DirEntry file and sends link or full dentry packets. streamInode gathers metadata attributes for file inodes, sends inode info, streams user xattrs if configured, and waits for ack. delete helpers send deletion packets and wait for ack.

## State And Persistence
Runtime state includes basePath and isRunning signaling. It reads local metadata files and xattrs and causes remote resync writes through the secondary message handler.

## Dependencies And Integration Points
Depends on Program/App singletons, InternodeSyncer, MetaStore paths under the buddy mirror subtree, EntryLockStore locking, SyncCandidateStore queues, MessagingTk request/response, ResyncRawInodes/ResyncSessionStore messages, target state stores, and worker barriers.

## Risks And Edge Cases
No timeout is used for resync communication. streamInode treats metadata xattr enumeration/read errors as fatal. Directory inode packets send empty metadata maps. receiveAck assumes every packet receives a ResyncRawInodesResp; mismatches are communication errors.

## Test Signals
Test packet serialization for link/full dentries, file/directory inodes, deletions, xattr-enabled and disabled modes, ack mismatch, allocation failure, and long resync response handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/SyncSlaveBase.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/SyncSlaveBase.h -->
# sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/SyncSlaveBase.h

## Purpose
Declares the abstract PThread base for resync-style slave threads and the packet serialization helpers used to stream metadata to a peer.

## Important APIs And Types
Important APIs are getIsRunning(), setOnlyTerminateIfIdle(), getOnlyTerminateIfIdle(), run(), syncLoop(), resyncAt(), streamDentry(), streamInode(), deleteDentry(), deleteInode(), sendResyncPacket(), and receiveAck(). It also defines tuple packet shapes for link dentries, full dentries, and inodes.

## Control Flow
Subclasses implement syncLoop and use protected helpers to create stream callbacks over sockets. The parent job observes isRunningChangeCond during cleanup.

## State And Persistence
Holds non-owning parent job pointers, buddyNodeID for buddy resync, running state, termination mode, and current basePath. sendResyncPacket allocates an in-memory buffer per packet.

## Dependencies And Integration Points
Depends on Program/App singletons, InternodeSyncer, MetaStore paths under the buddy mirror subtree, EntryLockStore locking, SyncCandidateStore queues, MessagingTk request/response, ResyncRawInodes/ResyncSessionStore messages, target state stores, and worker barriers.

## Risks And Edge Cases
Two constructors initialize different parent pointers; users must only access the one matching the subclass. sendResyncPacket does not check socket.send return value. The tuple serialization format must stay compatible with ResyncRawInodesMsgEx receiver code.

## Test Signals
Compile tests should cover subclass construction. Integration tests should verify termination modes, running-state signaling, and stream packet compatibility with the receiver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/SyncSlaveBase.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/chunkbalancer/ChunkBalancerJob.cpp -->
# sources/distributed-fs/beegfs/meta/source/components/chunkbalancer/ChunkBalancerJob.cpp

## Purpose
Implements the metadata-side chunk balancing job that accepts chunk copy candidates, scales metadata slave workers, tracks locks/statistics, and stops after an idle interval.

## Important APIs And Types
Key APIs are run(), createSyncSlave(), addChunkSyncCandidate(), shutdown(), destructor cleanup, and status/stat mutators. It owns ChunkSyncCandidateStore, a vector of ChunkBalancerMetaSlave pointers, GlobalInodeLockStore pointer, and ChunkBalancerJobStatistics.

## Control Flow
run refuses duplicate RUNNING jobs, resets stats, starts an initial slave, then loops until termination. It updates queue and locked inode stats, starts more slaves when the queue crosses CHUNKBALANCERJOB_MAX_FILE_PER_SLAVE_LIMIT up to four slaves, enters IDLE when the queue is empty, exits SUCCESS after a configurable idle duration, recreates a slave if all died while work remains, periodically sums slave counters, advances inode lock timesteps, and in cleanup terminates/join-waits slaves, marks ERRORS if needed, clears chunk-rebalancing locks, and records endTime. addChunkSyncCandidate enforces the configured queue limit before adding.

## State And Persistence
State is held in job stats under jobStatsMutex, the candidate queue, slave vector, and GlobalInodeLockStore entries for CHUNK_REBALANCING. The job does not copy chunks itself; it schedules slave work that causes storage-server copy operations and inode locks.

## Dependencies And Integration Points
Depends on Program/App, MetaStore and GlobalInodeLockStore, ChunkSyncCandidateStore, storage target mapping/state stores, comm slave queues, CopyChunkFileWork, and chunk-balancer statistics types.

## Risks And Edge Cases
Stats aggregation overwrites totals with summed slave counters each iteration; deleted slave counters can be lost unless captured during cleanup. Busy waiting can occur when slaves see an empty queue. Lock timeout depends on iterationDuration. createSlaveRes is a shared member used across starts.

## Test Signals
Test queue limit behavior, first slave creation failure, scaling to max slaves, idle-to-success timeout, shutdown interruption, dead slave replacement, error aggregation, and lock-store clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/chunkbalancer/ChunkBalancerJob.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/chunkbalancer/ChunkBalancerJob.h -->
# sources/distributed-fs/beegfs/meta/source/components/chunkbalancer/ChunkBalancerJob.h

## Purpose
Declares the PThread job that manages metadata chunk balancing candidate queues and worker slaves.

## Important APIs And Types
Important APIs are run(), abort() declaration, addChunkSyncCandidate(), shutdown(), getStatus(), isRunningStarting(), getJobStats(), createSyncSlave(), and private stats mutators. Constants cap slaves, queue-per-slave threshold, and sleep interval.

## Control Flow
External message handlers enqueue candidates and query status/stats. The job internally starts ChunkBalancerMetaSlave threads and shuts them down when idle or interrupted.

## State And Persistence
State includes jobStatsMutex-protected ChunkBalancerJobStatistics, a ChunkSyncCandidateStore, slave vector, abort/offline atomics, createSlaveRes, and a GlobalInodeLockStore pointer.

## Dependencies And Integration Points
Depends on Program/App, MetaStore and GlobalInodeLockStore, ChunkSyncCandidateStore, storage target mapping/state stores, comm slave queues, CopyChunkFileWork, and chunk-balancer statistics types.

## Risks And Edge Cases
abort() is declared but not implemented in the listed source, so callers should use shutdown if that remains true in the full tree. Manual raw-pointer slave ownership requires cleanup on every path. stats.workerNum decrement must not underflow if cleanup paths change.

## Test Signals
Compile/link tests should catch missing abort implementation if used. Runtime tests should validate status and stats under concurrent enqueue/shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/chunkbalancer/ChunkBalancerJob.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/chunkbalancer/ChunkBalancerMetaSlave.cpp -->
# sources/distributed-fs/beegfs/meta/source/components/chunkbalancer/ChunkBalancerMetaSlave.cpp

## Purpose
Implements a metadata slave that consumes chunk balancing candidates, locks the file inode, validates stripe-pattern constraints, and schedules a storage-side chunk copy.

## Important APIs And Types
The main API is syncLoop(). It uses ChunkSyncCandidateFile fields, MetaStore directory references, GlobalInodeLockStore insert/release, StripePattern target lists, CopyChunkFileWork, and SynchronizedCounter.

## Control Flow
The loop skips empty queues and targetID 0, detects group IDs as mirrored chunks, references the parent directory, takes the MetaStore write lock while checking unlinkability and inserting the inode into the chunk-rebalancing lock store, releases the parent dir, validates that the source target is present and destination absent in the stripe pattern, submits CopyChunkFileWork to the comm slave queue, waits for completion, releases the inode lock on copy start failures, and increments errors or chunks synced.

## State And Persistence
State is per-slave atomic numChunksSynced/errorCount plus queue pointer. Persistent state is the temporary inode lock in GlobalInodeLockStore and remote storage copy scheduling; stripe pattern update appears to be handled elsewhere after copy completion.

## Dependencies And Integration Points
Depends on Program/App, MetaStore and GlobalInodeLockStore, ChunkSyncCandidateStore, storage target mapping/state stores, comm slave queues, CopyChunkFileWork, and chunk-balancer statistics types.

## Risks And Edge Cases
If copy scheduling succeeds, the inode lock is intentionally retained for later balancing workflow; failures release it. Missing parent dirs, unlinkability, stale stripe patterns, and queue-full responses are handled as errors. The empty-queue continue path can spin until the parent job sleeps or terminates.

## Test Signals
Test mirrored and non-mirrored candidates, invalid target 0, missing parent dir, unlinkable file, duplicate destination target, missing source target, storage queue full (AGAIN), communication failure, and lock retention/release behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/chunkbalancer/ChunkBalancerMetaSlave.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/chunkbalancer/ChunkBalancerMetaSlave.h -->
# sources/distributed-fs/beegfs/meta/source/components/chunkbalancer/ChunkBalancerMetaSlave.h

## Purpose
Declares the metadata chunk-balancing slave thread derived from SyncSlaveBase.

## Important APIs And Types
Exports constructor, destructor, getNumChunksSynced(), getErrorCount(), and syncLoop(). Stores queue pointer, targetID, inodeLockStore pointer, and atomic counters.

## Control Flow
ChunkBalancerJob creates these slaves and reads their counters while managing the candidate queue.

## State And Persistence
Runtime state is non-owning with respect to the candidate store and parent job. Counters are atomic and used for job stats.

## Dependencies And Integration Points
Depends on Program/App, MetaStore and GlobalInodeLockStore, ChunkSyncCandidateStore, storage target mapping/state stores, comm slave queues, CopyChunkFileWork, and chunk-balancer statistics types.

## Risks And Edge Cases
targetID and inodeLockStore members are not initialized in the constructor shown; targetID appears unused, but future use would require initialization. Queue lifetime is owned by the job.

## Test Signals
Compile tests should flag unused/uninitialized member use if warnings are enabled. Integration tests should verify counters and thread state through the parent job.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/chunkbalancer/ChunkBalancerMetaSlave.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/chunkbalancer/SyncCandidate.h -->
# sources/distributed-fs/beegfs/meta/source/components/chunkbalancer/SyncCandidate.h

## Purpose
Defines chunk-balancer candidate value types describing a chunk to copy from one target/group to another for a file entry.

## Important APIs And Types
Important types are IdType, ChunkSyncCandidateDir, ChunkSyncCandidateFile, and ChunkSyncCandidateStore. Candidates carry idType, relativePath, targetID, destinationID, EntryInfo copy, and FileEvent copy.

## Control Flow
Producers construct candidates from balancing requests; ChunkBalancerJob queues them; ChunkBalancerMetaSlave fetches file candidates and uses their entry/event data to lock metadata and submit CopyChunkFileWork.

## State And Persistence
Candidates are in-memory queue records. EntryInfo and FileEvent are stored by value to avoid depending on caller lifetime.

## Dependencies And Integration Points
Depends on Program/App, MetaStore and GlobalInodeLockStore, ChunkSyncCandidateStore, storage target mapping/state stores, comm slave queues, CopyChunkFileWork, and chunk-balancer statistics types.

## Risks And Edge Cases
The constructor casts an IdType parameter that is already IdType, but invalid numeric values can still be represented. getFileEvent() always returns a pointer to the internal event despite the comment about nullptr. Pool IDs are defined but not handled by the listed slave logic.

## Test Signals
Test value-copy behavior, default construction, invalid ID handling, group-ID mirrored path, and queue fetch/add semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/chunkbalancer/SyncCandidate.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/BarrierWork.h -->
# sources/distributed-fs/beegfs/meta/source/components/worker/BarrierWork.h

## Purpose
Declares a small Work item used to park all worker threads at a two-phase Barrier.

## Important APIs And Types
BarrierWork::process waits once to signal that the worker is blocked, then waits a second time for release, with debug logging.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
It holds only a non-owning Barrier pointer and no persistent state.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
Deadlock occurs if the barrier participant count is wrong or the releasing thread never reaches the second wait.

## Test Signals
Test with N worker personal queues plus coordinator wait/release and interruption during shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/BarrierWork.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/CloseChunkFileWork.cpp -->
# sources/distributed-fs/beegfs/meta/source/components/worker/CloseChunkFileWork.cpp

## Purpose
Implements remote CloseChunkFileMsg execution against one storage target and optional dynamic attribute capture.

## Important APIs And Types
process calls communicate, stores FhgfsOpsErr, and increments the caller counter. communicate sets buddy-mirror and second-mirror flags, suppresses dynamic attrs for secondaries, sends via RequestResponseTarget, copies DynamicFileAttribs from the response, and returns/logs remote result.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
It mutates caller-provided outResult/outDynAttribs and closes remote chunk session state.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
INUSE is logged at debug level; response attrs are copied even on error with storageVersion 0 semantics.

## Test Signals
Test communication failure, INUSE, buddy mirror primary/secondary flags, dynamic attr output, and user-id propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/CloseChunkFileWork.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/CloseChunkFileWork.h -->
# sources/distributed-fs/beegfs/meta/source/components/worker/CloseChunkFileWork.h

## Purpose
Declares Work wrapper for closing a chunk file on a storage target.

## Important APIs And Types
Constructor captures sessionID, fileHandleID, StripePattern, target, PathInfo, optional DynamicFileAttribs, result pointer, and counter; setters control msg user ID and mirror-second mode.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
Holds non-owning pattern/path/result/counter pointers.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
Caller must keep referenced objects alive until process completes.

## Test Signals
Compile and async lifetime tests should cover optional outDynAttribs and mirror-second setter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/CloseChunkFileWork.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/CopyChunkFileWork.cpp -->
# sources/distributed-fs/beegfs/meta/source/components/worker/CopyChunkFileWork.cpp

## Purpose
Implements the storage request that starts a chunk copy for chunk balancing.

## Important APIs And Types
communicate builds CpChunkPathsMsg with event flag, validates mirrored source/destination as buddy group IDs, sets mirror routing, sends to the source target, and returns CpChunkPathsRespMsg result.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
It records only outResult/counter locally; remote storage begins copy work.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
Mirrored files with non-group IDs return INTERRUPTED. Communication failures are normalized to COMMUNICATION. The copy may only be started, not completed, by this response.

## Test Signals
Test mirrored ID validation, non-mirrored copy, storage queue full/AGAIN, communication failure, and file-event serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/CopyChunkFileWork.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/CopyChunkFileWork.h -->
# sources/distributed-fs/beegfs/meta/source/components/worker/CopyChunkFileWork.h

## Purpose
Declares Work wrapper for chunk-balancer CpChunkPathsMsg.

## Important APIs And Types
Constructor copies source/destination IDs, relative path, EntryInfo, mirrored flag, result pointer, counter, and FileEvent. Private isTargetIDMirrored validates group IDs.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
State is per-work-item and mostly by value except result/counter pointers.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
EntryInfo/FileEvent are copied, so caller mutations after construction are not reflected.

## Test Signals
Test constructor copy behavior and target mirror validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/CopyChunkFileWork.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/GetChunkFileAttribsWork.cpp -->
# sources/distributed-fs/beegfs/meta/source/components/worker/GetChunkFileAttribsWork.cpp

## Purpose
Implements remote GetChunkFileAttribsMsg execution and dynamic attribute extraction.

## Important APIs And Types
communicate sets buddy mirror flags, routes through RequestResponseTarget, validates GetChunkFileAttribsRespMsg result, and fills DynamicFileAttribs with storage version, size, blocks, mtime, and atime.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
Writes caller-provided result and outDynAttribs; reads remote chunk file state.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
outDynAttribs is assumed non-null on success. Buddy mirror second routing must match target mapper state.

## Test Signals
Test successful stat, failed target communication, non-success storage response, buddy primary/secondary flags, and user-id propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/GetChunkFileAttribsWork.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/GetChunkFileAttribsWork.h -->
# sources/distributed-fs/beegfs/meta/source/components/worker/GetChunkFileAttribsWork.h

## Purpose
Declares Work wrapper for fetching chunk dynamic attributes from a storage target.

## Important APIs And Types
Constructor captures entryID, StripePattern, targetID, PathInfo, DynamicFileAttribs*, result pointer, and counter; setters control user ID and mirror second.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
All pointers are non-owning and must remain valid through processing.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
The implementation expects outDynAttribs to be valid when success occurs.

## Test Signals
Compile/lifetime tests plus mirror-second request tests are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/GetChunkFileAttribsWork.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/LockEntryNotificationWork.cpp -->
# sources/distributed-fs/beegfs/meta/source/components/worker/LockEntryNotificationWork.cpp

## Purpose
Implements UDP lock-grant notification and ack handling for entry/append locks.

## Important APIs And Types
process builds wait-ack IDs, registers them with AcknowledgmentStore, repeatedly sends LockGrantedMsg to clients through DatagramListener, waits for acks, unregisters waiters, and if acks are missing references the loaded inode, unlocks unacknowledged waiters, and cancels all waiters when multiple acks are missing. Helper methods unlock append/flock waiters and increment a static ack counter.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
State is transient waitAcks/receivedAcks plus the static ack counter. It mutates in-memory FileInode lock queues on missed acknowledgments.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
notifyList elements back waitAck privateData, so the list must not change during processing. Missing client nodes do not remove waiters until ack timeout. Multiple missing acks trigger broad cancellation.

## Test Signals
Test all acks received, unknown client, partial acks, no acks, append vs flock behavior, cancel-all threshold, and ack ID uniqueness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/LockEntryNotificationWork.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/LockEntryNotificationWork.h -->
# sources/distributed-fs/beegfs/meta/source/components/worker/LockEntryNotificationWork.h

## Purpose
Declares Work wrapper for notifying clients about granted entry or append locks.

## Important APIs And Types
Defines LockEntryNotifyList and stores lock type, parentEntryID, entryID, buddy-mirror flag, owned notifyList, static ack counter, and helper declarations.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
The work item owns the notification list by move and mutates inode lock state only when process runs.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
Caller must pass a list whose EntryLockDetails remain valid as list nodes. Static ackCounter is process-wide and mutex-protected but can wrap.

## Test Signals
Tests should cover move ownership and correct dispatch by LockEntryNotifyType.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/LockEntryNotificationWork.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/LockRangeNotificationWork.cpp -->
# sources/distributed-fs/beegfs/meta/source/components/worker/LockRangeNotificationWork.cpp

## Purpose
Implements UDP lock-grant notification and ack handling for byte-range locks.

## Important APIs And Types
process mirrors the entry-lock workflow: register wait acks, resend LockGrantedMsg up to configured retries, unregister, then for missing acks reference the loaded file inode, set each RangeLockDetails to unlock, call flockRange, and cancel all waiters if multiple acks are missing.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
State is transient ack maps and static counter; missed notifications mutate in-memory range-lock queues.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
The code intentionally parallels LockEntryNotificationWork and can drift from it. Missing acks can revoke granted locks and cancel waiters, so timeout tuning affects client-visible lock behavior.

## Test Signals
Test full/partial/missing acks, disconnected clients, range unlock behavior, cancel-all path, retry timing, and ack ID uniqueness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/LockRangeNotificationWork.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/LockRangeNotificationWork.h -->
# sources/distributed-fs/beegfs/meta/source/components/worker/LockRangeNotificationWork.h

## Purpose
Declares Work wrapper for range-lock grant notifications.

## Important APIs And Types
Defines LockRangeNotifyList and stores parentEntryID, entryID, buddy-mirror flag, owned notifyList, static ack counter, and DatagramListener mutex helper.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
Runtime state is per-work notification data plus process-wide counter.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
Caller must not use notifyList after moving it into the work item.

## Test Signals
Test construction ownership and process behavior through LockRangeNotificationWork.cpp integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/LockRangeNotificationWork.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/SetChunkFileAttribsWork.cpp -->
# sources/distributed-fs/beegfs/meta/source/components/worker/SetChunkFileAttribsWork.cpp

## Purpose
Implements remote SetLocalAttrMsg execution for chunk attributes on storage targets.

## Important APIs And Types
communicate sets buddy mirror and quota-chown flags, user ID, target state/mirror routing, sends SetLocalAttrMsg, checks SetLocalAttrRespMsg, and optionally copies dynamic attributes when response flag HAS_ATTRS is set.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
Mutates remote chunk file metadata and caller-provided result/outDynamicAttribs.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
Quota flag changes storage-side accounting semantics. Dynamic attrs are present only if the response advertises them. enableCreation can create missing chunks depending on storage behavior.

## Test Signals
Test chown/quota path, enableCreation, buddy mirror primary/secondary, response with and without dynamic attrs, and communication failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/SetChunkFileAttribsWork.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/SetChunkFileAttribsWork.h -->
# sources/distributed-fs/beegfs/meta/source/components/worker/SetChunkFileAttribsWork.h

## Purpose
Declares Work wrapper for setting chunk file attributes on one storage target.

## Important APIs And Types
Constructor captures entryID, validAttribs, SettableFileAttribs pointer, creation flag, StripePattern, targetID, PathInfo, optional DynamicFileAttribs, result pointer, and counter; setters control quota chown, user ID, and mirror second.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
Pointer fields are non-owning. The remote storage target persists the attribute changes.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
attribs/pathInfo/pattern must outlive the work. quotaChown must be set deliberately for ownership changes from fsck.

## Test Signals
Compile/lifetime tests and fsck AdjustChunkPermissions integration tests should cover this class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/SetChunkFileAttribsWork.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/TruncChunkFileWork.cpp -->
# sources/distributed-fs/beegfs/meta/source/components/worker/TruncChunkFileWork.cpp

## Purpose
Implements remote TruncLocalFileMsg execution for truncating a chunk on storage.

## Important APIs And Types
communicate sets mirror flags, disables dynamic attrs for mirror-second, optionally includes quota user/group data, sends request, copies response dynamic attrs, suppresses warning for TOOBIG, and returns the response result.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
Mutates remote chunk length and caller-provided result/dynamic attrs.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
filesize is already target-local size; callers must precompute stripe-local truncation correctly. TOOBIG is intentionally passed through to clients without warning.

## Test Signals
Test quota and non-quota truncation, TOOBIG, mirror primary/secondary, dynamic attrs, and communication failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/TruncChunkFileWork.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/TruncChunkFileWork.h -->
# sources/distributed-fs/beegfs/meta/source/components/worker/TruncChunkFileWork.h

## Purpose
Declares Work wrapper for truncating a chunk file on one storage target.

## Important APIs And Types
Constructor captures entryID, local filesize, StripePattern, targetID, PathInfo, optional DynamicFileAttribs, result pointer, and counter. Setters configure quota user/group, message user ID, and mirror-second mode.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
Holds non-owning references and writes result outputs during process.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
Uninitialized userID/groupID are used only when useQuota is set. Caller lifetime for pattern/path/counter is critical.

## Test Signals
Tests should cover setter combinations and optional dynamic attribute output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/TruncChunkFileWork.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/UnlinkChunkFileWork.cpp -->
# sources/distributed-fs/beegfs/meta/source/components/worker/UnlinkChunkFileWork.cpp

## Purpose
Implements remote UnlinkLocalFileMsg execution for deleting a chunk file on storage.

## Important APIs And Types
communicate sets buddy mirror flags and message user ID, routes through RequestResponseTarget, validates UnlinkLocalFileRespMsg, logs failures, and returns the storage result.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
Mutates remote storage by unlinking a chunk and writes caller result/counter.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
Unlink failures can leave orphaned chunks or metadata/storage mismatch requiring higher-level recovery. Buddy mirror second routing must match the intended target half.

## Test Signals
Test successful unlink, missing target communication, storage non-success, buddy mirror primary/secondary, and user ID propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/UnlinkChunkFileWork.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/UnlinkChunkFileWork.h -->
# sources/distributed-fs/beegfs/meta/source/components/worker/UnlinkChunkFileWork.h

## Purpose
Declares Work wrapper for unlinking a chunk file from one storage target.

## Important APIs And Types
Constructor captures entryID, StripePattern, targetID, PathInfo, result pointer, and counter; setters control message user ID and mirror-second mode.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
All referenced objects are non-owning; result/counter are caller synchronization outputs.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
Caller must preserve PathInfo and StripePattern lifetimes until completion.

## Test Signals
Compile/lifetime tests and unlink integration tests should exercise both mirror modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/worker/UnlinkChunkFileWork.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/MirroredMessage.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/MirroredMessage.h

## Purpose
Defines the template base for metadata operations that may execute locally, forward to a metadata buddy, participate in sequence-number replay protection, and record changes for buddy resync.

## Important APIs And Types
Important virtual hooks are processSecondaryResponse(), mirrorLogContext(), executeLocally(), isMirrored(), lock(), forwardToSecondary(), and prepareMirrorRequestArgs(). Concrete helpers include processIncoming(), earlyComplete(), buddyResyncNotify(), finishOperation(), notifySecondaryOfACK(), sendToSecondary(), timestamp fixers, updateNodeOp(), and setBuddyNeedsResync().

## Control Flow
processIncoming optionally locks mirrored metadata, references a mirrored session, handles sequence-number zero by returning a new base, acquires/reuses MirrorStateSlot for duplicate request handling, registers a resync changeset and op when a resync is in progress, executes locally, and finishes or early-completes. finishOperation forwards observable changes to the secondary or sends AckNotify, records response state for replay, commits/abandons resync changesets, unregisters the resync op, sends the client response, and releases locks. sendToSecondary rejects forwarding during resync, validates secondary online/good state, sets needs-resync on unsuitable state or communication/result mismatch, copies sequence/requestor/user fields, and routes to the secondary mirror target.

## State And Persistence
State includes resyncJob pointer, lockState RAII object, shared MirrorStateSlot, mirrored sessions sequence stores, per-thread BuddyResyncer changesets, buddy needs-resync marker, operation counters, and optional timestamp mirroring updates on inodes.

## Dependencies And Integration Points
Depends on NetMessage base classes, Program/App service registries, MessagingTk, node/session/target stores, generated common message classes, and operation statistics counters.

## Risks And Edge Cases
This is a central correctness point. Lock ordering must be obeyed by every subclass. Response replay relies on memory barriers and one active request per client/sequence. If forwarding fails after local success, rollback is intentionally not attempted and needs-resync is set. resyncJob is reacquired in finishOperation and must remain valid long enough for unregisterOps. A typo in AckNotifiy names follows existing class names.

## Test Signals
Test duplicate sequence replay, sequence zero base negotiation, selective ack, local-only non-mutating operations, observable forwarding success/failure, secondary result mismatch, resync-in-progress changeset commit/abandon, earlyComplete socket release, timestamp mirroring, and lock-order deadlock scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/MirroredMessage.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/NetMessageFactory.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/NetMessageFactory.cpp

## Purpose
Implements the metadata server message factory that maps NETMSGTYPE_* IDs to concrete common response messages or meta-side *MsgEx request handlers.

## Important APIs And Types
The key API is createFromMsgType(unsigned short). It covers control, node, storage, session, monitoring, fsck, and chunk-balancing message groups and returns std::unique_ptr<NetMessage>. Unknown types become SimpleMsg(NETMSGTYPE_Invalid).

## Control Flow
Incoming serialized messages are parsed by AbstractNetMessageFactory, which calls this factory by type. Response-only types instantiate common response classes; request types instantiate server-side Ex handlers with processIncoming implementations.

## State And Persistence
The factory is stateless. Its mappings define the runtime dispatch table for all metadata network message processing.

## Dependencies And Integration Points
Depends on NetMessage base classes, Program/App service registries, MessagingTk, node/session/target stores, generated common message classes, and operation statistics counters.

## Risks And Edge Cases
A missing mapping makes valid wire messages invalid on this service. Mapping a request to a response class or vice versa can silently break processing. The long switch must stay synchronized with message type definitions and included headers.

## Test Signals
Test createFromMsgType for every listed NETMSGTYPE, invalid type fallback, compile coverage for all includes, and smoke tests that representative request handlers process through the listener path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/NetMessageFactory.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/NetMessageFactory.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/NetMessageFactory.h

## Purpose
Declares the metadata NetMessageFactory subclass used by the app to instantiate message handlers from wire message type IDs.

## Important APIs And Types
Exports a default constructor and overrides createFromMsgType(unsigned short) from AbstractNetMessageFactory.

## Control Flow
The app-level networking layer owns or references this factory and delegates type-specific construction to the cpp switch.

## State And Persistence
The class holds no state.

## Dependencies And Integration Points
Depends on NetMessage base classes, Program/App service registries, MessagingTk, node/session/target stores, generated common message classes, and operation statistics counters.

## Risks And Edge Cases
Any signature drift from AbstractNetMessageFactory would break dispatch. Constructor currently does no initialization.

## Test Signals
Compile tests and a dispatch smoke test are sufficient for the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/NetMessageFactory.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/control/AckMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/control/AckMsgEx.cpp

## Purpose
Processes incoming acknowledgement messages for async waiters such as lock-grant notification work.

## Important APIs And Types
processIncoming logs the ack value in debug builds, calls AcknowledgmentStore::receivedAck(getValue()), updates node operation stats with MetaOpCounter_ACK, and returns true without sending a response.

## Control Flow
The control flow is single-step: consume ack, update stats, no response.

## State And Persistence
Mutates the in-memory AcknowledgmentStore and operation counters. No durable state is written.

## Dependencies And Integration Points
Depends on NetMessage base classes, Program/App service registries, MessagingTk, node/session/target stores, generated common message classes, and operation statistics counters.

## Risks And Edge Cases
Malformed or unexpected ack values are delegated to AcknowledgmentStore behavior. The message is intentionally one-way, so clients must not wait for a response.

## Test Signals
Test ack delivery to registered waiters, unknown ack IDs, op-stat update, and no-response listener behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/control/AckMsgEx.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/control/AckMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/control/AckMsgEx.h

## Purpose
Declares the metadata-side AckMsg handler.

## Important APIs And Types
Exports processIncoming(ResponseContext&) override on top of common AckMsg.

## Control Flow
Factory creates this handler for NETMSGTYPE_Ack.

## State And Persistence
No state beyond inherited AckMsg value.

## Dependencies And Integration Points
Depends on NetMessage base classes, Program/App service registries, MessagingTk, node/session/target stores, generated common message classes, and operation statistics counters.

## Risks And Edge Cases
Header depends on common AckMsg semantics used by AcknowledgeableMsg.

## Test Signals
Compile and factory mapping tests cover this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/control/AckMsgEx.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/control/SetChannelDirectMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/control/SetChannelDirectMsgEx.cpp

## Purpose
Processes requests that toggle direct-channel mode on the current socket.

## Important APIs And Types
processIncoming logs the value in debug builds, calls ctx.getSocket()->setIsDirect(getValue()), updates node operation stats with MetaOpCounter_SETCHANNELDIRECT, and returns true.

## Control Flow
The handler mutates socket state immediately and sends no explicit response in this implementation.

## State And Persistence
State is per-socket directness plus operation counters.

## Dependencies And Integration Points
Depends on NetMessage base classes, Program/App service registries, MessagingTk, node/session/target stores, generated common message classes, and operation statistics counters.

## Risks And Edge Cases
A peer can change how the socket is classified; authentication and caller restrictions must be enforced elsewhere if required. No response means caller protocol must know this is fire-and-forget.

## Test Signals
Test direct flag true/false, op-stat update, and connection behavior after toggling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/control/SetChannelDirectMsgEx.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/control/SetChannelDirectMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/control/SetChannelDirectMsgEx.h

## Purpose
Declares the metadata-side SetChannelDirectMsg handler.

## Important APIs And Types
Exports processIncoming(ResponseContext&) override on common SetChannelDirectMsg.

## Control Flow
Factory creates this handler for NETMSGTYPE_SetChannelDirect.

## State And Persistence
No additional state beyond inherited message value.

## Dependencies And Integration Points
Depends on NetMessage base classes, Program/App service registries, MessagingTk, node/session/target stores, generated common message classes, and operation statistics counters.

## Risks And Edge Cases
Protocol behavior depends on the common message value representation.

## Test Signals
Compile and factory mapping tests cover this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/control/SetChannelDirectMsgEx.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/AdjustChunkPermissionsMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/AdjustChunkPermissionsMsgEx.cpp

## Purpose
Scans dentries and updates storage chunk owner/group permissions for inlined file inodes.

## Important APIs And Types
processIncoming pages through content directories using hash and content offsets, references or creates a temporary DirInode, lists entries, extracts inlined inode user/group/stripe/path info, calls sendSetAttrMsg, and returns updated cursors plus errorCount. sendSetAttrMsg fans out SetChunkFileAttribsWork to all stripe targets with quota chown enabled.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Updates remote chunk ownership/group on storage targets; local metadata is read except temporary in-memory inode creation.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Cursor handling must be exact or fsck can skip/repeat entries. Temporary inode use allows damaged metadata traversal but may hide parent loss. All stripe target works must succeed for one file to count as success.

## Test Signals
Test paging offsets, missing parent dir temporary inode, inlined vs non-inlined files, storage target failure, buddy-mirrored locks, and quota chown flag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/AdjustChunkPermissionsMsgEx.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/AdjustChunkPermissionsMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/AdjustChunkPermissionsMsgEx.h

## Purpose
Declares the fsck handler for chunk permission adjustment.

## Important APIs And Types
Exports processIncoming and private sendSetAttrMsg(entryID,userID,groupID,pathInfo,pattern).

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
No state beyond inherited request fields.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
The private helper depends on StripePattern and PathInfo lifetime during worker fan-out.

## Test Signals
Compile and handler integration tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/AdjustChunkPermissionsMsgEx.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/CheckAndRepairDupInodeMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/CheckAndRepairDupInodeMsgEx.cpp

## Purpose
Repairs duplicate file inode situations reported by fsck.

## Important APIs And Types
processIncoming iterates duplicate inode records, locks parent and file IDs for buddy-mirrored metadata, builds EntryInfo, references the parent directory, calls MetaStore::checkAndRepairDupFileInode, collects failed IDs, and responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Mutates local metadata when MetaStore repairs duplicate inode/dentry state.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
It assumes referenceDir succeeds; dereferencing parentDir on failure would be unsafe unless inputs guarantee existence. Lock order parent then file must remain consistent.

## Test Signals
Test successful repair, missing parent directory, buddy-mirrored and non-mirrored items, and failed repair response list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/CheckAndRepairDupInodeMsgEx.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/CheckAndRepairDupInodeMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/CheckAndRepairDupInodeMsgEx.h

## Purpose
Declares the duplicate-inode fsck repair handler.

## Important APIs And Types
Exports processIncoming override.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
No added state.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Depends on common CheckAndRepairDupInodeMsg fields.

## Test Signals
Factory and repair integration tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/CheckAndRepairDupInodeMsgEx.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/CreateDefDirInodesMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/CreateDefDirInodesMsgEx.cpp

## Purpose
Creates replacement/default directory inodes for fsck repair.

## Important APIs And Types
processIncoming iterates requested inode IDs and buddy flags, computes owner as local buddy group or local node, builds a root-owned default Raid0Pattern DirInode, stores it as replacement, refreshes metainfo, builds FsckDirInode records for successes, and returns failed IDs plus created inodes.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Persists new directory inode files in the metadata store.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Default ownership/mode/stripe values are repair approximations, not original metadata. storeAsReplacementFile can overwrite replacement state; buddy-mirrored lock is by inode ID.

## Test Signals
Test creation success/failure, buddy owner group selection, metadata refresh, and response created inode fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/CreateDefDirInodesMsgEx.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/CreateDefDirInodesMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/CreateDefDirInodesMsgEx.h

## Purpose
Declares the default directory inode creation fsck handler.

## Important APIs And Types
Exports processIncoming override and includes Raid0Pattern and response types.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
No extra state.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Behavior depends on inherited items list.

## Test Signals
Compile and fsck repair tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/CreateDefDirInodesMsgEx.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/CreateEmptyContDirsMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/CreateEmptyContDirsMsgEx.cpp

## Purpose
Creates missing empty content directories and #fSiDs# directories for fsck repair.

## Important APIs And Types
processIncoming builds the dentry path for each dir ID, mkdirs the content dir and dirEntryID subdir, locks buddy-mirrored IDs, references the directory inode, refreshes metadata, collects failed IDs, and responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Persists directories in the metadata dentry tree and updates directory dynamic metadata.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
mkdir failure on existing directories is treated as failure; partial success can leave content dir created without #fSiDs#. Missing DirInode after mkdir is also failure.

## Test Signals
Test successful creation, EEXIST handling, #fSiDs# mkdir failure, missing inode, buddy-mirrored path selection, and refresh failure logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/CreateEmptyContDirsMsgEx.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/CreateEmptyContDirsMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/CreateEmptyContDirsMsgEx.h

## Purpose
Declares the empty content directory creation fsck handler.

## Important APIs And Types
Exports processIncoming override.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
No extra state.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Depends on inherited items tuple.

## Test Signals
Compile and repair integration tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/CreateEmptyContDirsMsgEx.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/DeleteDirEntriesMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/DeleteDirEntriesMsgEx.cpp

## Purpose
Deletes corrupt or unwanted directory entries during fsck repair.

## Important APIs And Types
processIncoming locks parent/name for buddy-mirrored entries, references parent DirInode, calls removeDir for directories or unlinkDirEntry for files, releases parent, collects failed entries, and responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Mutates local dentry files and directory metadata.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Directory vs file path depends on FsckDirEntryType. Missing parent is a per-entry failure. File unlink uses DirEntry_UNLINK_ID_AND_FILENAME, removing both name and ID links.

## Test Signals
Test file and dir deletion, missing parent, buddy locks, unlink failure, and response failedEntries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/DeleteDirEntriesMsgEx.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/DeleteDirEntriesMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/DeleteDirEntriesMsgEx.h

## Purpose
Declares the fsck directory-entry deletion handler.

## Important APIs And Types
Exports processIncoming override.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
No extra state.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Depends on common DeleteDirEntriesMsg list.

## Test Signals
Compile and factory mapping tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/DeleteDirEntriesMsgEx.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/FixInodeOwnersInDentryMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/FixInodeOwnersInDentryMsgEx.cpp

## Purpose
Updates owner node IDs stored in directory entries.

## Important APIs And Types
processIncoming walks dentries and owner IDs in parallel, optionally locks parent/name, references or temporarily creates parent DirInode, calls setOwnerNodeID(entryName, owner), records failed dentries, releases/deletes parent inode, and responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Persists owner field changes in dentry files when parent exists; temporary inode path can edit dentry files by path if possible.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
The dentries and owners lists must have matching lengths. Temporary inode repair is best-effort. Missing failures for parent temporary construction could hide broader corruption.

## Test Signals
Test matched/mismatched list lengths, missing parent, setOwner failure, buddy locks, and response failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/FixInodeOwnersInDentryMsgEx.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/FixInodeOwnersInDentryMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/FixInodeOwnersInDentryMsgEx.h

## Purpose
Declares the dentry owner repair handler.

## Important APIs And Types
Exports processIncoming override.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
No extra state.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Requires inherited dentry and owner lists.

## Test Signals
Compile and list-length integration tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/FixInodeOwnersInDentryMsgEx.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/FixInodeOwnersMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/FixInodeOwnersMsgEx.cpp

## Purpose
Updates owner node IDs stored in directory inodes.

## Important APIs And Types
processIncoming iterates FsckDirInode records, locks buddy-mirrored inode ID, references the directory inode, calls setOwnerNodeID(ownerNodeID), releases it, collects failures, and responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Persists directory inode owner changes.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
If referenceDir fails the code logs and continues without adding that inode to failedInodes, which may under-report failures. setOwnerNodeID boolean failure is captured.

## Test Signals
Test successful update, reference failure reporting expectations, buddy locks, and failed response list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/FixInodeOwnersMsgEx.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/FixInodeOwnersMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/FixInodeOwnersMsgEx.h

## Purpose
Declares the directory inode owner repair handler.

## Important APIs And Types
Exports processIncoming override.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
No added state.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Depends on common FixInodeOwnersMsg.

## Test Signals
Compile and repair tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/FixInodeOwnersMsgEx.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/FsckSetEventLoggingMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/FsckSetEventLoggingMsgEx.cpp

## Purpose
Enables or disables fsck modification event logging.

## Important APIs And Types
processIncoming gets ModificationEventFlusher, enables logging with UDP port/NIC list/forceRestart or disables logging, reports result/loggingEnabled/missedEvents, and responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Mutates event flusher runtime state and exposes whether fsck missed events while disabled.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Enable path always returns result=true and missedEvents ignored, so callers must interpret fields by loggingEnabled. Force restart can reset existing logging.

## Test Signals
Test enable, disable, force restart, missed-events reporting, and response fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/FsckSetEventLoggingMsgEx.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/FsckSetEventLoggingMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/FsckSetEventLoggingMsgEx.h

## Purpose
Declares the fsck event logging control handler.

## Important APIs And Types
Exports processIncoming override.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
No added state.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Depends on common request fields for port/NIC list/force flag.

## Test Signals
Compile and flusher integration tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/FsckSetEventLoggingMsgEx.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/LinkToLostAndFoundMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/LinkToLostAndFoundMsgEx.cpp

## Purpose
Links orphaned directory inodes into lost+found during fsck repair.

## Important APIs And Types
processIncoming supports directory entries only, calls linkDirInodes, and returns failed inode and created dentry lists. linkDirInodes references lost+found, creates DirEntry records named by entryID, sets buddy feature for mirrored inodes, stats created dentry files for device/inode, records FsckDirEntry results, refreshes lost+found metadata, and releases it.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Persists new dentry links under lost+found and refreshes lost+found attributes.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Non-directory requests return false; declared file helper/deleteInode are unused here. makeDirEntry failure after stat attempts may produce critical logs. Existing names in lost+found can fail repair.

## Test Signals
Test missing lost+found, successful directory link, duplicate lost+found names, buddy-mirrored entries, stat failure, and non-directory request rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/LinkToLostAndFoundMsgEx.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/LinkToLostAndFoundMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/LinkToLostAndFoundMsgEx.h

## Purpose
Declares lost+found linking repair handler.

## Important APIs And Types
Exports processIncoming plus private linkDirInodes, linkFileInodes, and deleteInode declarations.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
No added data beyond inherited request fields.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
linkFileInodes/deleteInode are declared but not implemented in the listed cpp, so usage would require link coverage elsewhere.

## Test Signals
Compile/link tests should catch unused missing definitions if called; directory repair tests cover implemented behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/LinkToLostAndFoundMsgEx.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/RecreateDentriesMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/RecreateDentriesMsgEx.cpp

## Purpose
Recreates missing dentry-by-name links from existing dentry-by-ID files.

## Important APIs And Types
processIncoming iterates FsckFsID records, chooses local owner ID, builds ID and name paths, locks parent/name for mirrored entries, references parent dir, hard-links ID file to a name equal to the entry ID, reads the created DirEntry, builds FsckDirEntry and inlined FsckFileInode records if inode data is present, releases parent, and responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Persists hard links in the dentry namespace and reports reconstructed fsck objects.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
The original file name is lost and replaced with the ID. link failure can happen if target exists. Inlined inode data is expected because the ID file exists, but absence is only logged.

## Test Signals
Test successful recreation, missing parent, existing name, link failure, no inlined inode data, buddy-mirrored paths, and created inode fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/RecreateDentriesMsgEx.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/RecreateDentriesMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/RecreateDentriesMsgEx.h

## Purpose
Declares the dentry recreation fsck handler.

## Important APIs And Types
Exports processIncoming override.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
No extra state.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Depends on FsckFsID request list.

## Test Signals
Compile and repair tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/RecreateDentriesMsgEx.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/RecreateFsIDsMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/RecreateFsIDsMsgEx.cpp

## Purpose
Recreates dentry-by-ID hard links from existing dentry-by-name files.

## Important APIs And Types
processIncoming iterates FsckDirEntry records, computes ID and name paths, locks parent/name/file IDs, unlinks any old ID link unless ENOENT, creates a hard link from name to ID, collects failed entries, and responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Persists hard links under #fSiDs# directories.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
The code locks even non-buddy entries using entryLockStore, unlike many fsck handlers that lock only mirrored entries. A missing name file fails recreation. Removing an old faulty link is destructive but intended.

## Test Signals
Test successful relink, old ID link absent/present, unlink error, name link missing, buddy and non-buddy entries, and response failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/RecreateFsIDsMsgEx.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/RecreateFsIDsMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/RecreateFsIDsMsgEx.h

## Purpose
Declares the fsID recreation handler.

## Important APIs And Types
Exports processIncoming override.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
No added state.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Depends on common RecreateFsIDsMsg entries.

## Test Signals
Compile and hard-link repair tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/RecreateFsIDsMsgEx.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/RemoveInodesMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/RemoveInodesMsgEx.cpp

## Purpose
Removes directory or file inodes during fsck cleanup.

## Important APIs And Types
processIncoming iterates item tuples of entryID, DirEntryType, and buddy flag, locks directory or file ID, calls removeDirInode for directories or fsckUnlinkFileInode for files, collects failed IDs, and responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Deletes inode files from metadata storage.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Directory removal and file unlink use different MetaStore paths. Locks are created regardless of buddy flag in the listed code, so non-buddy operations also use the mirrored EntryLockStore object.

## Test Signals
Test file and directory removal, missing inode, buddy/non-buddy behavior, and failed ID response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/RemoveInodesMsgEx.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/RemoveInodesMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/RemoveInodesMsgEx.h

## Purpose
Declares the inode removal fsck handler.

## Important APIs And Types
Exports processIncoming override.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
No added state.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Depends on inherited item tuples.

## Test Signals
Compile and removal tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/RemoveInodesMsgEx.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/RetrieveDirEntriesMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/RetrieveDirEntriesMsgEx.cpp

## Purpose
Retrieves content directories, dentries, and inlined file inodes incrementally for fsck.

## Important APIs And Types
processIncoming uses hash/content offsets and currentContDirID to page through content dirs, skips buddy-mirrored retrieval on secondary/local group 0, references or temporarily creates DirInode, lists names, builds FsckDirEntry records with stat device/inode data, builds FsckFileInode records for inlined files including dynamic stat refresh fallback, emits contDir records when advancing dirs, and responds with cursors.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Read-only except temporary in-memory inode objects. It observes metadata dentries, inlined inode data, dynamic attribs, and stat device/inode numbers.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
readOutEntries is updated only when advancing to the next content dir, so maxOutEntries enforcement depends on entryNames size and loop structure. Damaged entries may be skipped with warnings. Secondary buddy nodes intentionally return empty.

## Test Signals
Test pagination across dirs, currentContDir resume, secondary buddy skip, missing parent temp inode, dynamic attribs outdated fallback, stat failure, inlined and non-inlined entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/RetrieveDirEntriesMsgEx.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/RetrieveDirEntriesMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/RetrieveDirEntriesMsgEx.h

## Purpose
Declares the directory-entry retrieval fsck handler.

## Important APIs And Types
Exports processIncoming override.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
No added state.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Depends on common cursor fields.

## Test Signals
Compile and pagination tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/RetrieveDirEntriesMsgEx.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/RetrieveFsIDsMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/RetrieveFsIDsMsgEx.cpp

## Purpose
Retrieves dentry-by-ID files incrementally for fsck.

## Important APIs And Types
processIncoming pages through content dirs and #fSiDs# directories, skips buddy-mirrored retrieval on secondary/local group 0, references or temporarily creates DirInode, calls listIDFilesIncremental, stats each ID file, builds FsckFsID records, advances cursors, and responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Read-only except temporary in-memory inode creation. Observes #fSiDs# hard links and stat metadata.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
readOutIDs controls maxOutIDs. listRes errors are logged but already-read names are still processed. Secondary buddy skip must match fsck coordinator expectations.

## Test Signals
Test pagination, missing parent temp inode, list error, stat failure, buddy secondary skip, and cursor resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/RetrieveFsIDsMsgEx.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/RetrieveFsIDsMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/RetrieveFsIDsMsgEx.h

## Purpose
Declares the fsID retrieval handler.

## Important APIs And Types
Exports processIncoming override.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
No added state.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Depends on common RetrieveFsIDsMsg cursor fields.

## Test Signals
Compile and pagination tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/RetrieveFsIDsMsgEx.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/RetrieveInodesMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/RetrieveInodesMsgEx.cpp

## Purpose
Retrieves file and directory inodes incrementally for fsck.

## Important APIs And Types
processIncoming calls MetaStore::getAllInodesIncremental with hashDirNum, lastOffset, maxOutInodes, output lists, newOffset, and buddy flag, then responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Read-only metadata scan of inode files.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
All filtering/pagination correctness is delegated to MetaStore. No explicit buddy-secondary skip appears here, unlike dentry/fsID retrieval.

## Test Signals
Test pagination offsets, buddy and non-buddy scans, empty hash dirs, and mixed file/dir inode output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/RetrieveInodesMsgEx.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/RetrieveInodesMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/RetrieveInodesMsgEx.h

## Purpose
Declares the inode retrieval fsck handler.

## Important APIs And Types
Exports processIncoming override.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
No added state.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Depends on common RetrieveInodesMsg fields.

## Test Signals
Compile and MetaStore scan tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/RetrieveInodesMsgEx.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/UpdateDirAttribsMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/UpdateDirAttribsMsgEx.cpp

## Purpose
Refreshes directory dynamic attributes for fsck repair.

## Important APIs And Types
processIncoming iterates FsckDirInode records, locks buddy-mirrored dir IDs, references DirInode, calls refreshMetaInfo, releases it, collects failures, and responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Persists refreshed directory metadata derived from content directory state.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Missing directory is a failure. refreshMetaInfo can fail after partial filesystem issues and is reported per inode.

## Test Signals
Test successful refresh, missing dir, refresh failure, buddy lock, and failedInodes response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/UpdateDirAttribsMsgEx.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/UpdateDirAttribsMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/UpdateDirAttribsMsgEx.h

## Purpose
Declares the directory attribute update fsck handler.

## Important APIs And Types
Exports processIncoming override.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
No added state.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Depends on common UpdateDirAttribsMsg list.

## Test Signals
Compile and refresh tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/UpdateDirAttribsMsgEx.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/UpdateFileAttribsMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/UpdateFileAttribsMsgEx.cpp

## Purpose
Refreshes file dynamic attributes and hardlink count for fsck repair.

## Important APIs And Types
processIncoming builds EntryInfo for each FsckFileInode, locks buddy-mirrored file ID, references the file inode, updates num hardlinks persistently via updateInodeOnDisk, calls MsgHelperStat::refreshDynAttribs, releases the file, collects failures, and responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Persists hardlink count and refreshed dynamic file attributes in metadata.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
EntryInfo uses a dummy file name and must contain correct parent/inlined/buddy flags. refreshDynAttribs may reference the same inode, so release is intentionally delayed. Missing inode is a failure.

## Test Signals
Test inlined and non-inlined file inodes, buddy flags, hardlink update, refresh failure, missing inode, and response failed list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/UpdateFileAttribsMsgEx.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/UpdateFileAttribsMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/fsck/UpdateFileAttribsMsgEx.h

## Purpose
Declares the file attribute update fsck handler.

## Important APIs And Types
Exports processIncoming override.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
No added state.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Depends on common UpdateFileAttribsMsg list.

## Test Signals
Compile and refresh tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/fsck/UpdateFileAttribsMsgEx.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/mon/RequestMetaDataMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/mon/RequestMetaDataMsgEx.cpp

## Purpose
Implements monitoring metadata snapshot responses for the monitoring service.

## Important APIs And Types
processIncoming gathers local node alias/hostname/ID/NICs, root ownership flag, indirect/direct work queue sizes, normal plus mirrored session counts, and high-resolution stats since the request value, then sends RequestMetaDataRespMsg and updates MetaOpCounter_REQUESTMETADATA.

## Control Flow
The flow is read-only: collect App state, query StatsCollector history, build response, send response, update op stats.

## State And Persistence
No durable state is changed. It observes session stores, work queues, local node configuration, and stats history.

## Dependencies And Integration Points
Depends on NetMessage base classes, Program/App service registries, MessagingTk, node/session/target stores, generated common message classes, and operation statistics counters.

## Risks And Edge Cases
Large stats histories can grow response size depending on lastStatsMS. Session count merges regular and mirrored stores. Root ownership is a boolean comparison of meta root owner and local node ID.

## Test Signals
Test empty and populated stats history, root/non-root node, session counts including mirrored sessions, queue sizes, NIC serialization, and op-stat update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/mon/RequestMetaDataMsgEx.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/mon/RequestMetaDataMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/mon/RequestMetaDataMsgEx.h

## Purpose
Declares the metadata monitoring request handler.

## Important APIs And Types
Exports processIncoming(ResponseContext&) override on common RequestMetaDataMsg and includes the matching response type.

## Control Flow
Factory creates this handler for NETMSGTYPE_RequestMetaData.

## State And Persistence
No additional state beyond inherited request value.

## Dependencies And Integration Points
Depends on NetMessage base classes, Program/App service registries, MessagingTk, node/session/target stores, generated common message classes, and operation statistics counters.

## Risks And Edge Cases
Header includes App and logging dependencies used by the implementation.

## Test Signals
Compile and factory mapping tests cover this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/mon/RequestMetaDataMsgEx.h -->
