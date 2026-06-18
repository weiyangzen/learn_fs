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
