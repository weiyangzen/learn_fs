# sources/distributed-fs/beegfs/meta/source/net/message/fsck/FixInodeOwnersInDentryMsgEx.h

## Purpose
Declares the dentry owner repair handler.

## Important APIs And Types
Exports processIncoming override.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
No extra state.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Requires inherited dentry and owner lists.

## Test Signals
Compile and list-length integration tests cover it.
