# sources/distributed-fs/beegfs/meta/source/net/message/fsck/FixInodeOwnersMsgEx.cpp

## Purpose
Updates owner node IDs stored in directory inodes.

## Important APIs And Types
processIncoming iterates FsckDirInode records, locks buddy-mirrored inode ID, references the directory inode, calls setOwnerNodeID(ownerNodeID), releases it, collects failures, and responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Persists directory inode owner changes.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
If referenceDir fails the code logs and continues without adding that inode to failedInodes, which may under-report failures. setOwnerNodeID boolean failure is captured.

## Test Signals
Test successful update, reference failure reporting expectations, buddy locks, and failed response list.
