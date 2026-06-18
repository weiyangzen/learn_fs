# sources/distributed-fs/beegfs/meta/source/net/message/fsck/AdjustChunkPermissionsMsgEx.h

## Purpose
Declares the fsck handler for chunk permission adjustment.

## Important APIs And Types
Exports processIncoming and private sendSetAttrMsg(entryID,userID,groupID,pathInfo,pattern).

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
No state beyond inherited request fields.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
The private helper depends on StripePattern and PathInfo lifetime during worker fan-out.

## Test Signals
Compile and handler integration tests cover it.
