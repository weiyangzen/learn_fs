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
