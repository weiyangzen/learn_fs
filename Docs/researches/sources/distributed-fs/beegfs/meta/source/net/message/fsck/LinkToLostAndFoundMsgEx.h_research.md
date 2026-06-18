# sources/distributed-fs/beegfs/meta/source/net/message/fsck/LinkToLostAndFoundMsgEx.h

## Purpose
Declares lost+found linking repair handler.

## Important APIs And Types
Exports processIncoming plus private linkDirInodes, linkFileInodes, and deleteInode declarations.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
No added data beyond inherited request fields.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
linkFileInodes/deleteInode are declared but not implemented in the listed cpp, so usage would require link coverage elsewhere.

## Test Signals
Compile/link tests should catch unused missing definitions if called; directory repair tests cover implemented behavior.
