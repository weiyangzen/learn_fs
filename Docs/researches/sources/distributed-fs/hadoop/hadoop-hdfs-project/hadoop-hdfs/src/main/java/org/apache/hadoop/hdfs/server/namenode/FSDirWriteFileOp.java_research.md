# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirWriteFileOp.java

## Purpose
`FSDirWriteFileOp` owns Namenode namespace/block operations for file creation, block allocation, block abandonment, open-file persistence, add-block retry handling, file completion, and edit-log file-add replay.

## Important APIs, Types, And Functions
- Creation: `resolvePathForStartFile`, `startFile`, `addFileForEditLog`, private `addFile`, and `newINodeFile`.
- Block lifecycle: `validateAddBlock`, `chooseTargetForNewBlock`, `storeAllocatedBlock`, `saveAllocatedBlock`, `addBlock`, `abandonBlock`, `unprotectedRemoveBlock`, `persistBlocks`, and `persistNewBlock`.
- Completion: `completeFile` and `completeFileInternal`.
- Supporting types: `ValidateAddBlockResult`, `FileState`, `BlockInfoContiguous`, `BlockInfoStriped`, `DatanodeStorageInfo`, `ErasureCodingPolicy`, and `FileEncryptionInfo`.

## Control Flow
Start-file resolution checks ancestor write permission, existing directory/file state, overwrite permission, create-parent requirements, and create/overwrite flags. `startFile` deletes an existing inode on overwrite or attempts lease recovery before throwing on non-overwrite, checks object limits, creates missing parents, chooses contiguous or striped layout based on EC policy and `shouldReplicate`, creates an under-construction `INodeFile`, adds a lease, writes encryption info if present, applies lazy-persist or copy-on-create storage policy, logs `logOpenFile`, and returns status. Add-block is split into validation and storage: validation under read lock checks lease, safe mode, object/block limits, previous block identity, retry cases, replication progress, block size/type/targets, and EC layout; target choice calls block placement; storage rechecks state under write lock, commits the previous block, creates a new block, adds it to inode and block map, logs `logAddBlock`, and returns a write-token `LocatedBlock`. Completion validates lease and retry close cases, checks file progress, commits/completes the last block, queues committed blocks, and finalizes the under-construction inode.

## State And Persistence Behavior
The file mutates namespace inodes, under-construction file features, leases, block lists, block maps, scheduled block counters, quotas, encryption XAttrs, storage policy IDs, and pending replication/commit state. Edit-log records include open-file, update-blocks, add-block, and replayed file creation. Block tokens are generated for returned write locations.

## Dependencies And Integration Points
It is one of the densest integration points: `FSNamesystem`, `FSDirectory`, `BlockManager`, `DatanodeManager`, `LeaseManager`, `FSDirDeleteOp`, `FSDirMkdirOp`, `FSDirEncryptionZoneOp`, `FSDirErasureCodingOp`, `FSDirStatAndListingOp`, ACL/XAttr storage, network topology resolution, and HDFS client create/addBlock/complete protocols all meet here.

## Risks And Edge Cases
Add-block retry detection is subtle and protects against duplicate empty blocks, HA retries, and bogus previous-block IDs. Validation must be repeated after block placement because locks were released. Overwrite must clean leases and collect blocks correctly. Striped files use EC target counts and `BlockInfoStriped`; contiguous files use replication. Lazy-persist storage policy can be disabled. Encryption info must be written after inode creation and before open-file edit persistence semantics are relied on.

## Test Signals
Tests should cover create/overwrite flag matrix, parent creation, lease recovery on existing files, encrypted file creation and retry when zone changes, EC striped file creation/add-block, lazy-persist disabled behavior, add-block retry cases for previous/penultimate/empty block, target choice with excluded/favored/locality flags, abandon block quota/scheduled-counter updates, complete-file retry after successful close, max blocks per file, edit-log replay of open files with ACL/XAttrs/storage/EC policy, and quota updates on add/remove block.
