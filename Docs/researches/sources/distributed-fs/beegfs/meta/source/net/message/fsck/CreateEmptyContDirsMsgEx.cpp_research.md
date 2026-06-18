# sources/distributed-fs/beegfs/meta/source/net/message/fsck/CreateEmptyContDirsMsgEx.cpp

## Purpose
Creates missing empty content directories and #fSiDs# directories for fsck repair.

## Important APIs And Types
processIncoming builds the dentry path for each dir ID, mkdirs the content dir and dirEntryID subdir, locks buddy-mirrored IDs, references the directory inode, refreshes metadata, collects failed IDs, and responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Persists directories in the metadata dentry tree and updates directory dynamic metadata.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
mkdir failure on existing directories is treated as failure; partial success can leave content dir created without #fSiDs#. Missing DirInode after mkdir is also failure.

## Test Signals
Test successful creation, EEXIST handling, #fSiDs# mkdir failure, missing inode, buddy-mirrored path selection, and refresh failure logging.
