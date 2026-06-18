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
