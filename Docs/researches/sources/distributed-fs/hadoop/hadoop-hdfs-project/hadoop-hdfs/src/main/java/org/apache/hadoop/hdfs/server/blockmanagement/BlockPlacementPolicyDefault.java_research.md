# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementPolicyDefault.java

## Purpose

`BlockPlacementPolicyDefault` is the standard HDFS block placement and excess-replica deletion policy. It prefers writer-local placement for the first replica, a remote rack for the second, a local rack relative to the second or writer for the third, and random placement afterward, while honoring storage policies, stale/load/slow-node filtering, rack limits, and client add-block flags.

## Important APIs and types

- Public `chooseTarget` overloads handle normal writes, favored-node writes, preselected replicas, `NO_LOCAL_WRITE` and `NO_LOCAL_RACK`, and explicit `EnumMap<StorageType,Integer>` requests.
- `chooseTargetInOrder`, `chooseLocalOrFavoredStorage`, `chooseLocalRack`, `chooseRemoteRack`, and `chooseRandom` implement the placement strategy.
- `isGoodDatanode` rejects nodes that are out of service, stale, overloaded, over rack limit, or slow.
- `chooseStorage4Block` asks each datanode for an eligible storage with enough remaining space and required storage type.
- `verifyBlockPlacement` enforces the default multi-rack rule.
- `chooseReplicasToDelete`, `chooseReplicaToDelete`, `useDelHint`, `pickupReplicaSet`, and `isMovable` preserve rack diversity during deletion and balancer moves.
- Tunables include `considerLoad`, load-by-storage-type, load-by-volume, local-node preference, peer slow-node exclusion, heartbeat tolerance, stale interval, and minimum blocks required for writes.

## Control flow

Initialization copies NameNode configuration and topology/stat references. Normal target selection first caps requested replicas by cluster size and computes `maxNodesPerRack`. Existing chosen storages are added to the exclusion set. If the caller requested `NO_LOCAL_RACK` or `NO_LOCAL_WRITE`, the method tries a modified exclusion set and only keeps the result if it can satisfy the count; otherwise it falls back to default placement.

The internal chooser derives required storage types from `BlockStoragePolicy`, then calls `chooseTargetInOrder`. If placement fails while stale nodes are being avoided, it retries without stale avoidance and preserves already chosen nodes. If storage types are unavailable, it marks remaining requested types unavailable and retries with policy fallbacks. `chooseRandom` repeatedly asks the topology for a candidate, validates the datanode, selects a matching storage, updates the storage-type counts, and records high-level rejection reasons for logging.

Deletion flow splits replicas by rack, optionally accepts a safe delete hint, otherwise chooses from a preferred set using oldest heartbeat first and least remaining storage as fallback. After each deletion choice it updates rack sets before selecting the next excess replica.

## State and persistence behavior

The policy stores only runtime configuration and references to NameNode-maintained cluster state. It persists nothing itself. Placement mutates provided result, exclusion, and storage-type maps; slow-node data comes from `DatanodeManager`, and load/staleness data comes from current heartbeat-derived state.

## Dependencies and integration points

This policy integrates with `NetworkTopology` and `DFSNetworkTopology`, `FSClusterStats`, `DatanodeDescriptor`, `DatanodeStorageInfo`, `BlockStoragePolicy`, `StorageTypeStats`, `AddBlockFlag`, NameNode configuration keys, datanode slow-node peer stats, replication work scheduling, and balancer/mover safety checks.

## Risks and edge cases

Placement behavior is sensitive to mutable exclusion sets and partial results during retries. Load filtering can starve placement if cluster averages are low or storage-type stats are missing. The policy relies on `DatanodeDescriptor.chooseStorage4Block` to enforce per-storage capacity and minimum block requirements. Debug reason logging uses thread-local builders and maps, so tests should verify no stale diagnostic state leaks between calls. `NO_LOCAL_RACK` only applies when more than two racks exist, and both local-avoidance flags silently fall back if insufficient targets are available.

## Test signals

Strong tests cover replica ordering, rack caps, single-rack and multi-rack verification, storage-policy fallback, favored-node fallback, stale-node retry, overloaded and slow-node exclusion, `NO_LOCAL_WRITE` and `NO_LOCAL_RACK`, deletion hint safety, excess storage-type removal, and balancer `isMovable` cases.
