# sources/distributed-fs/beegfs/meta/source/net/message/fsck/RemoveInodesMsgEx.cpp

## Purpose
Removes directory or file inodes during fsck cleanup.

## Important APIs And Types
processIncoming iterates item tuples of entryID, DirEntryType, and buddy flag, locks directory or file ID, calls removeDirInode for directories or fsckUnlinkFileInode for files, collects failed IDs, and responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Deletes inode files from metadata storage.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Directory removal and file unlink use different MetaStore paths. Locks are created regardless of buddy flag in the listed code, so non-buddy operations also use the mirrored EntryLockStore object.

## Test Signals
Test file and directory removal, missing inode, buddy/non-buddy behavior, and failed ID response.
