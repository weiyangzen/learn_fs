# sources/distributed-fs/beegfs/meta/source/net/message/fsck/DeleteDirEntriesMsgEx.cpp

## Purpose
Deletes corrupt or unwanted directory entries during fsck repair.

## Important APIs And Types
processIncoming locks parent/name for buddy-mirrored entries, references parent DirInode, calls removeDir for directories or unlinkDirEntry for files, releases parent, collects failed entries, and responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Mutates local dentry files and directory metadata.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Directory vs file path depends on FsckDirEntryType. Missing parent is a per-entry failure. File unlink uses DirEntry_UNLINK_ID_AND_FILENAME, removing both name and ID links.

## Test Signals
Test file and dir deletion, missing parent, buddy locks, unlink failure, and response failedEntries.
