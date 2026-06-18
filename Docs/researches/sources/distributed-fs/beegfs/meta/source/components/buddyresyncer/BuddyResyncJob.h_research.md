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
