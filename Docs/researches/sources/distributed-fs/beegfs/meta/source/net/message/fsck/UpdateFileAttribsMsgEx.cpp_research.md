# sources/distributed-fs/beegfs/meta/source/net/message/fsck/UpdateFileAttribsMsgEx.cpp

## Purpose
Refreshes file dynamic attributes and hardlink count for fsck repair.

## Important APIs And Types
processIncoming builds EntryInfo for each FsckFileInode, locks buddy-mirrored file ID, references the file inode, updates num hardlinks persistently via updateInodeOnDisk, calls MsgHelperStat::refreshDynAttribs, releases the file, collects failures, and responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Persists hardlink count and refreshed dynamic file attributes in metadata.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
EntryInfo uses a dummy file name and must contain correct parent/inlined/buddy flags. refreshDynAttribs may reference the same inode, so release is intentionally delayed. Missing inode is a failure.

## Test Signals
Test inlined and non-inlined file inodes, buddy flags, hardlink update, refresh failure, missing inode, and response failed list.
