# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirStatAndListingOp.java

## Purpose
`FSDirStatAndListingOp` builds read-side HDFS metadata responses: directory listings, file status, file-closed checks, content summaries, quota usage, and block location responses.

## Important APIs, Types, And Functions
- Entry points include `getListingInt`, `getFileInfo`, `isFileClosed`, `getContentSummary`, `getBlockLocations`, and `getQuotaUsage`.
- Status builders include `createFileStatusForEditLog` and private `createFileStatus` overloads.
- Listing helpers include `getListing`, `getSnapshotsListing`, and `getReservedListing`.
- `GetBlockLocationsResult` returns located blocks plus whether atime should be updated.

## Control Flow
Listings resolve the path, normalize reserved `startAfter` inode paths, check read/execute permission on directories, and under a read lock return reserved, snapshot, single-file, or partial directory listings. Directory listing enforces `lsLimit` and a location budget when locations are requested. File info handles a superuser compatibility case where permission exceptions become null, resolves symlinks according to the caller flag, and builds an `HdfsFileStatus`. Block locations validate nonnegative ranges, resolve without early access checks, check unreadable-by-superuser and read permission, computes snapshot/non-UC file size, gets encryption info and EC policy, asks `BlockManager` for located blocks, and signals atime update if precision allows.

## State And Persistence Behavior
Most functions are read-only. The only state effect is indirect: `getBlockLocations` returns `updateAccessTime=true` so the caller can persist access-time changes elsewhere. Status creation reads inode attributes, ACL flags, encryption-zone membership, EC policy, symlinks, children count, and optionally block locations with a block-manager read lock.

## Dependencies And Integration Points
The file ties together `FSDirectory`, `BlockManager`, `FSDirEncryptionZoneOp`, `FSDirErasureCodingOp`, snapshot features, `ContentSummaryComputationContext`, `HdfsFileStatus.Builder`, `LocatedBlocks`, `DirectoryListing`, and permission enforcement. It is a central response builder for `FSNamesystem` RPCs and edit-log status generation.

## Risks And Edge Cases
Nested read locks occur because status creation calls encryption/EC helpers that also read-lock; the code relies on lock reentrancy/ordering. Snapshot paths must not expose UC state beyond snapshot file size. Location-budget logic must account for EC internal block count, not just block count. Content summary can yield locks based on configured limits, so callers must tolerate long-running computations.

## Test Signals
Tests should cover reserved and `.snapshot` listings, `startAfter` reserved inode normalization, lsLimit/location budget behavior including EC files, superuser null compatibility path, unreadable-by-superuser block-location denial, snapshot block ranges, encrypted file status including `FileEncryptionInfo`, ACL/encrypted/EC/snapshottable flags, quota usage fallback to content summary, and atime update signaling.
