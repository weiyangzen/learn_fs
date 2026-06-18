# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementPolicyWithNodeGroup.java

## Purpose

`BlockPlacementPolicyWithNodeGroup` adapts HDFS placement to topologies with a node-group layer below racks. It treats node groups as an additional failure domain so replicas avoid landing in the same node group when possible.

## Important APIs and types

- `initialize` requires `NetworkTopologyWithNodeGroup`.
- `chooseFavouredNodes` first tries favored nodes, then falls back to another node in each unchosen favored node's node group.
- `chooseLocalStorage` adds fallback from local node to local node group and then local rack.
- `chooseLocalRack`, `chooseRemoteRack`, and `chooseLocalNodeGroup` use first-half rack and last-half node-group topology helpers.
- `addToExcludedNodes` excludes every leaf in the selected node group plus dependent hostnames.
- `pickupReplicaSet`, `isMovable`, and `verifyBlockPlacement` enforce node-group diversity during deletion, move, and audit.

## Control flow

Initialization fails fast if the configured topology is not node-group aware. Placement first tries local storage, then a peer in the local node group, then local rack fallback. Remote-rack placement uses the rack portion of the writer path. When a node is chosen, the entire node group and dependent datanodes are excluded so later replicas do not duplicate the same lower-level failure domain. Verification temporarily strips node-group suffixes from `DatanodeInfo` network locations to reuse default rack verification, restores the original locations, then wraps the result with node-group status requiring one node group per replica.

For over-replication, the policy first uses the inherited rack split. If candidates already share a rack, it further partitions them by node group and prefers replicas from node groups with more than one copy.

## State and persistence behavior

The policy adds no durable state. It relies on `NetworkTopologyWithNodeGroup` and optional `Host2NodesMap` dependent-host metadata. `verifyBlockPlacement` temporarily mutates `DatanodeInfo` network locations and restores them in the normal path.

## Dependencies and integration points

It integrates with the node-group topology implementation, datanode dependent-host metadata, favored-node placement, replication deletion, balancer move validation, and `BlockPlacementStatusWithNodeGroup`.

## Risks and edge cases

Temporary mutation of datanode network locations during verification is fragile if exceptions are introduced before restoration. Dependent-host exclusion logs but otherwise tolerates missing host mappings. Node-group extraction assumes topology paths are well formed. Requiring `numberOfReplicas` node groups can report unsatisfied placement when the topology has fewer node groups than replicas.

## Test signals

Tests should cover topology type rejection, local node-group fallback, favored-node node-group fallback, dependent-host exclusion, delete-candidate node-group preference, `isMovable` with same-node-group target, and verification restoration of original network locations.
