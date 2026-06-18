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
