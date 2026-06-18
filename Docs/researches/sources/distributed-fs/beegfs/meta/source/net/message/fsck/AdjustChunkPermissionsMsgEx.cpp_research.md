# sources/distributed-fs/beegfs/meta/source/net/message/fsck/AdjustChunkPermissionsMsgEx.cpp

## Purpose
Scans dentries and updates storage chunk owner/group permissions for inlined file inodes.

## Important APIs And Types
processIncoming pages through content directories using hash and content offsets, references or creates a temporary DirInode, lists entries, extracts inlined inode user/group/stripe/path info, calls sendSetAttrMsg, and returns updated cursors plus errorCount. sendSetAttrMsg fans out SetChunkFileAttribsWork to all stripe targets with quota chown enabled.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Updates remote chunk ownership/group on storage targets; local metadata is read except temporary in-memory inode creation.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Cursor handling must be exact or fsck can skip/repeat entries. Temporary inode use allows damaged metadata traversal but may hide parent loss. All stripe target works must succeed for one file to count as success.

## Test Signals
Test paging offsets, missing parent dir temporary inode, inlined vs non-inlined files, storage target failure, buddy-mirrored locks, and quota chown flag.
