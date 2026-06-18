# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementPolicy.java

## Purpose

`BlockPlacementPolicy` is the abstract contract for HDFS replica placement. It defines how the NameNode chooses target `DatanodeStorageInfo` instances for new blocks and reconstruction, validates whether existing replicas satisfy placement rules, chooses excess replicas for deletion, and decides whether balancer moves preserve placement policy.

## Important APIs and types

- `chooseTarget(...)` is the primary placement API, with overloads for chosen nodes, favored nodes, storage policy, add-block flags, and explicit storage-type counts.
- `verifyBlockPlacement(DatanodeInfo[], int)` returns a `BlockPlacementStatus` describing rack or extended failure-domain satisfaction.
- `chooseReplicasToDelete(...)` selects over-replicated storages after accounting for expected replica count, excess storage types, added-node and delete-node hints.
- `initialize(Configuration, FSClusterStats, NetworkTopology, Host2NodesMap)` injects NameNode configuration, cluster stats, topology, and host lookup dependencies.
- Shared helpers include `splitNodesWithRack`, `adjustSetsWithChosenReplica`, `getDatanodeInfo`, and `getRack`.
- `NotEnoughReplicasException` is the internal signal used by concrete policies when placement cannot satisfy the requested target count.

## Control flow

The base class delegates actual placement to subclasses, but it provides shared rack grouping used by deletion and move decisions. `splitNodesWithRack` first builds a rack-to-replica map from all available replicas, then classifies candidate replicas into `moreThanOne` or `exactlyOne` depending on whether their rack has multiple replicas. `adjustSetsWithChosenReplica` updates those structures after a deletion choice, moving a remaining rack peer from `moreThanOne` to `exactlyOne` if it becomes the last replica on its rack.

Favored-node and explicit-storage-type overloads intentionally fall back to the core abstract placement method unless a subclass adds stronger semantics. `getDatanodeInfo` lets shared code operate on either `DatanodeInfo` or `DatanodeStorageInfo`, while `getRack` is virtual so node-group policies can redefine the effective rack.

## State and persistence behavior

The class holds no persistent state. It is a stateless strategy base whose concrete implementations keep configuration-derived state. Its helper methods mutate caller-supplied collections only, especially during excess-replica selection.

## Dependencies and integration points

It sits between `BlockManager`, `DatanodeManager`, `NetworkTopology`, `FSClusterStats`, `BlockStoragePolicy`, storage-type accounting, balancer/mover decisions, and datanode host mappings. The runtime policy selected by NameNode configuration must implement this contract.

## Risks and edge cases

Rack classification assumes candidates are represented in the available set; a missing rack entry can produce null dereference. `getDatanodeInfo` rejects unsupported object types at runtime. Subclasses must keep overload semantics consistent, especially around favored nodes, storage policy fallback, and mutable `excludedNodes`.

## Test signals

Useful tests exercise rack split and adjustment behavior, delete-hint handling, storage-type overload routing, move validation, and subclass compatibility with both `DatanodeInfo` and `DatanodeStorageInfo` inputs.
