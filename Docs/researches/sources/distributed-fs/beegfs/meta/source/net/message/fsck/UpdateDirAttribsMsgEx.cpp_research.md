# sources/distributed-fs/beegfs/meta/source/net/message/fsck/UpdateDirAttribsMsgEx.cpp

## Purpose
Refreshes directory dynamic attributes for fsck repair.

## Important APIs And Types
processIncoming iterates FsckDirInode records, locks buddy-mirrored dir IDs, references DirInode, calls refreshMetaInfo, releases it, collects failures, and responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Persists refreshed directory metadata derived from content directory state.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Missing directory is a failure. refreshMetaInfo can fail after partial filesystem issues and is reported per inode.

## Test Signals
Test successful refresh, missing dir, refresh failure, buddy lock, and failedInodes response.
