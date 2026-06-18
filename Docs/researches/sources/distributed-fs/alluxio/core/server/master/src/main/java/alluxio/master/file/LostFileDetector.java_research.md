# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/LostFileDetector.java

## Purpose
`LostFileDetector` is a heartbeat executor that consumes lost block reports from `BlockMaster` and marks affected non-persisted files as `LOST` in the file-system master metadata.

## Important APIs, types, and functions
The constructor stores `FileSystemMaster`, `BlockMaster`, and `InodeTree`, and registers the `MASTER_LOST_FILE_COUNT` metric. `heartbeat(long)` iterates `mBlockMaster.getLostBlocksIterator()`, maps each block id to a file id via `BlockId.getContainerId` and `IdUtils.createFileId`, collects candidate files, and journals `UpdateInodeEntry` persistence-state updates. `close()` is a no-op.

## Control flow
The first pass removes lost blocks from the block-master iterator while collecting unique non-persisted file ids. Missing inode paths are ignored. The second pass opens a journal context, write-locks each candidate inode, rechecks that it is not persisted, and updates persistence state to `LOST`.

## State and persistence behavior
The detector mutates persistent inode state through journaled `InodeTree.updateInode` calls. Lost block entries are removed from the block-master lost-block iterator before journal updates are flushed; a comment states this is acceptable because LOST status is currently display-only.

## Dependencies and integration points
It integrates heartbeat scheduling, block-master lost-block tracking, inode locking, file persistence state, journal contexts, and master lost-file metrics.

## Risks
Removing block candidates before journal durability can drop LOST marking after a crash. The second pass adds `fileId` back into `toMarkFiles` while iterating over that set, which is suspicious and could trigger concurrent modification behavior or reflect a simple leftover statement. The code intentionally does not mark persisted files lost. Large lost-block bursts can create large candidate sets in memory.

## Test signals
Tests should cover mapping lost blocks to files, skipping persisted files, missing inode removal, successful journaled LOST updates, unavailable journal handling, and the second-pass set mutation behavior.
