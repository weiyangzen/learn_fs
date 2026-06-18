# sources/distributed-fs/beegfs/meta/source/net/message/fsck/RetrieveInodesMsgEx.cpp

## Purpose
Retrieves file and directory inodes incrementally for fsck.

## Important APIs And Types
processIncoming calls MetaStore::getAllInodesIncremental with hashDirNum, lastOffset, maxOutInodes, output lists, newOffset, and buddy flag, then responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Read-only metadata scan of inode files.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
All filtering/pagination correctness is delegated to MetaStore. No explicit buddy-secondary skip appears here, unlike dentry/fsID retrieval.

## Test Signals
Test pagination offsets, buddy and non-buddy scans, empty hash dirs, and mixed file/dir inode output.
