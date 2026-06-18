## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/DefaultBlockStoreMeta.java

### Purpose
`DefaultBlockStoreMeta` is a snapshot implementation of `BlockStoreMeta` built from `BlockMetadataManager`. It reports tier/dir capacity, used bytes, optional block id lists, directory paths, storage tier association, and lost storage.

### Important APIs and Types
- Constructor `DefaultBlockStoreMeta(BlockMetadataManager, boolean shouldIncludeBlockIds)`.
- Capacity/usage getters: `getCapacityBytes`, `getCapacityBytesOnTiers`, `getCapacityBytesOnDirs`, `getUsedBytes`, `getUsedBytesOnTiers`, `getUsedBytesOnDirs`.
- Block lists: `getBlockList`, `getBlockListByStorageLocation`, `getNumberOfBlocks`.
- Topology/loss: `getDirectoryPathsOnTiers`, `getLostStorage`, `getStorageTierAssoc`.

### Control Flow
The constructor walks all tiers and dirs once, accumulating tier totals and dir maps. If full block ids are requested, it also creates tier-level and location-level block id lists. Finally, it copies lost storage paths from tiers into a tier-keyed map.

### State and Persistence
This object is an in-memory snapshot. It does not mutate block metadata or storage files. When `shouldIncludeBlockIds` is false, block-list fields are null and block-list getters enforce non-null via `Preconditions`.

### Dependencies and Integration Points
Created by `BlockMetadataManager.getBlockStoreMeta` and `getBlockStoreMetaFull`; consumed by worker registration, heartbeat metrics gauges, master commit calls, and UI/API metadata responses.

### Risks
- Some returned maps are mutable internal maps, while `getUsedBytesOnTiers` wraps unmodifiable; callers could mutate snapshot fields inconsistently.
- Full metadata snapshots allocate block id lists for every directory and can be expensive/OOM-prone for very large workers.
- Block-list getters throw if called on a non-full snapshot.

### Test Signals
Covered indirectly by `BlockWorkerMetricsTest`, registration tests, and metadata manager/store tests that compare capacity and block lists.
