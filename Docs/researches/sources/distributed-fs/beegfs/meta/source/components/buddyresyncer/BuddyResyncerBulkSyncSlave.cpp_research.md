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
