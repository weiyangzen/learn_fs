# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/NetworkTopologyWithNodeGroup.java

Purpose: extends `NetworkTopology` for a four-level topology with node groups between racks and leaves, used for virtualization-aware placement where hosts sharing a hypervisor should be closer than same-rack but not identical.

Important APIs/types/functions: `DEFAULT_NODEGROUP`, `getNodeForNetworkLocation`, `getRack`, `getNodeGroup`, `isOnSameRack`, `isOnSameNodeGroup`, `isNodeGroupAware`, `add`, `remove`, `getWeight`, `sortByDistance`, and nested `InnerNodeWithNodeGroup`.

Control flow: default-rack leaves are rewritten to `/default-rack/default-nodegroup`. `add` validates that the implied rack is an inner node with a parent, then adds the leaf and increments rack count only when a new rack appears. Same-rack compares parents of node-group parents; same-node-group compares direct parents. Sorting substitutes an out-of-tree reader with an existing sibling leaf from the same node group when possible, then delegates to base sorting.

State and persistence: in-memory topology state inherited from `NetworkTopology`, but the constructor replaces `clusterMap` with `InnerNodeWithNodeGroup`. It does not update the base class empty-rack tracking on add/remove, so nodegroup-aware users primarily rely on rack counts and distance sorting.

Dependencies and integration: integrates with `InnerNodeImpl` and base topology APIs. HDFS block placement can query `isNodeGroupAware` and `isOnSameNodeGroup` to avoid colocating replicas on the same physical host.

Risks: `getNodeGroup` only recognizes `InnerNodeWithNodeGroup`; leaf lookup paths fall through as not handled. The rack/nodegroup classification in `InnerNodeWithNodeGroup` inspects the first child, assuming homogeneous subtree shape. The constructor sets `clusterMap` directly and leaves `factory` as the base default factory, so removal fallback uses `factory.newInnerNode` rather than the nodegroup subclass.

Test signals: `TestNetworkTopologyWithNodeGroup` covers node group identity, rack identity, add/remove, distance sorting, and default nodegroup behavior.
