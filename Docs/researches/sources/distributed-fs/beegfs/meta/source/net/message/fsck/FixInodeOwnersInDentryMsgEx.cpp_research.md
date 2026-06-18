# sources/distributed-fs/beegfs/meta/source/net/message/fsck/FixInodeOwnersInDentryMsgEx.cpp

## Purpose
Updates owner node IDs stored in directory entries.

## Important APIs And Types
processIncoming walks dentries and owner IDs in parallel, optionally locks parent/name, references or temporarily creates parent DirInode, calls setOwnerNodeID(entryName, owner), records failed dentries, releases/deletes parent inode, and responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Persists owner field changes in dentry files when parent exists; temporary inode path can edit dentry files by path if possible.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
The dentries and owners lists must have matching lengths. Temporary inode repair is best-effort. Missing failures for parent temporary construction could hide broader corruption.

## Test Signals
Test matched/mismatched list lengths, missing parent, setOwner failure, buddy locks, and response failures.
