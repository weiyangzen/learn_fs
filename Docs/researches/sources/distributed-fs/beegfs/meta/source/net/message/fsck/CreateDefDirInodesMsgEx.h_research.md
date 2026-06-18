# sources/distributed-fs/beegfs/meta/source/net/message/fsck/CreateDefDirInodesMsgEx.h

## Purpose
Declares the default directory inode creation fsck handler.

## Important APIs And Types
Exports processIncoming override and includes Raid0Pattern and response types.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
No extra state.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Behavior depends on inherited items list.

## Test Signals
Compile and fsck repair tests cover it.
