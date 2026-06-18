# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirSatisfyStoragePolicyOp.java

## Purpose
`FSDirSatisfyStoragePolicyOp` marks files/directories for asynchronous storage-policy satisfaction and feeds the Storage Policy Satisfier queue.

## Important APIs, Types, And Functions
- `satisfyStoragePolicy` is the checked entry point.
- `unprotectedSatisfyStoragePolicy` queues an inode during replay/XAttr application.
- `removeSPSXattr` removes the marker XAttr after SPS processing.
- `inodeHasSatisfyXAttr` detects duplicate file requests.

## Control Flow
The checked path asserts the FS write lock, resolves the path under the directory write lock, checks write permission, skips zero-block files, warns on duplicate satisfy XAttr for files, otherwise builds `XATTR_SATISFY_STORAGE_POLICY`, inserts it through `FSDirXAttrOp.setINodeXAttrs`, logs `logSetXAttrs`, and adds the inode ID to `StoragePolicySatisfyManager` if present. Replay/helper flow avoids empty files and only queues the path ID. Removal reads inode XAttrs, removes the SPS marker, updates XAttr storage, and logs `logRemoveXAttrs`.

## State And Persistence Behavior
The persistent request marker is an inode XAttr. In-memory state is the SPS manager pending path queue. Completion/removal persists by removing the XAttr. The operation itself does not move blocks; it schedules asynchronous movement.

## Dependencies And Integration Points
It depends on `FSDirectory`, `BlockManager.getSPSManager`, `StoragePolicySatisfyManager`, `FSDirXAttrOp`, `XAttrStorage`, `XAttrHelper`, and HDFS server constants. `FSDirXAttrOp.unprotectedSetXAttrs` also queues SPS when it sees the marker XAttr during replay.

## Risks And Edge Cases
Zero-block files are skipped because there is nothing to move. Duplicate detection only checks files in `inodeHasSatisfyXAttr`; directories can be re-marked according to the current helper behavior. SPS manager may be null, so persisted XAttrs can exist without immediate queueing if SPS is disabled. Removal mutates a list returned from storage, so tests should catch list mutability assumptions.

## Test Signals
Tests should cover permission checks, zero-block file skip, duplicate marker warning/no duplicate create, directory queueing, null SPS manager behavior, replay queueing from XAttr, marker removal edit logging, and eventual XAttr cleanup after SPS completion.
