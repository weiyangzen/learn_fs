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
