<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/SetMetadataMirroringMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/SetMetadataMirroringMsgEx.cpp

## Purpose
Enables metadata buddy mirroring for the root directory by moving root metadata into buddy-mirror storage paths, setting the root inode mirror flag, and changing root owner to the local buddy group.

## Important APIs, Types, and Functions
`processIncoming()` verifies the local node belongs to a buddy group, is primary, and owns the root directory, then calls `setMirroring()` and sends `SetMetadataMirroringRespMsg`. `setMirroring()` serializes callers through a static mutex, no-ops when already mirrored, moves the root inode and root directory, persists `DirInode::setAndStoreIsBuddyMirrored(true)`, sets owner node ID to the buddy group, and updates `MetaRoot`. `moveRootInode()` and `moveRootDirectory()` rename paths between normal and buddy-mirror metadata trees, with revert support.

## Control Flow, State, and Persistence
This mutates on-disk metadata layout with POSIX `rename()`, updates the root `DirInode` on disk, changes in-memory root owner/mirror state, and tries to roll back file moves on intermediate failures. The mirror flag is deliberately written after moving files because it changes path calculation inside `DirInode`.

## Dependencies and Integration Points
Depends on `MirrorBuddyGroupMapper`, `RootDir`, `MetaStorageTk`, app metadata paths, `StorageTk::createPathOnDisk`, `DirInode`, `MetaRoot`, and common set-mirroring response messages. `ResyncRawInodesMsgEx` also calls `setMirroring()` during root resync bootstrap.

## Risks and Test Signals
Risks include partial rename failures, rollback failures that can corrupt root metadata, concurrent bulk-resync callers, and mismatch between local node primary status and root ownership. Tests should cover already mirrored root, non-group node, secondary node, not-owner root, successful path moves, each rollback branch, and persistent root owner/mirror flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/SetMetadataMirroringMsgEx.cpp -->
