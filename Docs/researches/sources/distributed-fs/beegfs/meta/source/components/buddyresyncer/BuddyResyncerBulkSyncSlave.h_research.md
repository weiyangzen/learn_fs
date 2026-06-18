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
