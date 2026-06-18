# sources/distributed-fs/beegfs/meta/source/net/message/fsck/LinkToLostAndFoundMsgEx.cpp

## Purpose
Links orphaned directory inodes into lost+found during fsck repair.

## Important APIs And Types
processIncoming supports directory entries only, calls linkDirInodes, and returns failed inode and created dentry lists. linkDirInodes references lost+found, creates DirEntry records named by entryID, sets buddy feature for mirrored inodes, stats created dentry files for device/inode, records FsckDirEntry results, refreshes lost+found metadata, and releases it.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Persists new dentry links under lost+found and refreshes lost+found attributes.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Non-directory requests return false; declared file helper/deleteInode are unused here. makeDirEntry failure after stat attempts may produce critical logs. Existing names in lost+found can fail repair.

## Test Signals
Test missing lost+found, successful directory link, duplicate lost+found names, buddy-mirrored entries, stat failure, and non-directory request rejection.
