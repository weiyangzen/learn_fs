# sources/distributed-fs/beegfs/meta/source/net/message/fsck/CheckAndRepairDupInodeMsgEx.cpp

## Purpose
Repairs duplicate file inode situations reported by fsck.

## Important APIs And Types
processIncoming iterates duplicate inode records, locks parent and file IDs for buddy-mirrored metadata, builds EntryInfo, references the parent directory, calls MetaStore::checkAndRepairDupFileInode, collects failed IDs, and responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Mutates local metadata when MetaStore repairs duplicate inode/dentry state.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
It assumes referenceDir succeeds; dereferencing parentDir on failure would be unsafe unless inputs guarantee existence. Lock order parent then file must remain consistent.

## Test Signals
Test successful repair, missing parent directory, buddy-mirrored and non-mirrored items, and failed repair response list.
