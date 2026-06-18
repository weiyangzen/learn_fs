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
