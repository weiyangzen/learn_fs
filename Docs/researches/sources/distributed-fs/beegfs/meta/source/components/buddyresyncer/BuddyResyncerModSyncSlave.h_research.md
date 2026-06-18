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
