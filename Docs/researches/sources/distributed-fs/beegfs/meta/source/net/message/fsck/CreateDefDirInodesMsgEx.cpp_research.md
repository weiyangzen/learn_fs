# sources/distributed-fs/beegfs/meta/source/net/message/fsck/CreateDefDirInodesMsgEx.cpp

## Purpose
Creates replacement/default directory inodes for fsck repair.

## Important APIs And Types
processIncoming iterates requested inode IDs and buddy flags, computes owner as local buddy group or local node, builds a root-owned default Raid0Pattern DirInode, stores it as replacement, refreshes metainfo, builds FsckDirInode records for successes, and returns failed IDs plus created inodes.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Persists new directory inode files in the metadata store.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
Default ownership/mode/stripe values are repair approximations, not original metadata. storeAsReplacementFile can overwrite replacement state; buddy-mirrored lock is by inode ID.

## Test Signals
Test creation success/failure, buddy owner group selection, metadata refresh, and response created inode fields.
