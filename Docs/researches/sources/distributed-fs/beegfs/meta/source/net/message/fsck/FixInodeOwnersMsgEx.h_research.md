# sources/distributed-fs/beegfs/meta/source/net/message/fsck/FixInodeOwnersMsgEx.h

## Purpose
Declares the directory inode owner repair handler.

## Important APIs And Types
Exports processIncoming override.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
No added state.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Depends on common FixInodeOwnersMsg.

## Test Signals
Compile and repair tests cover it.
