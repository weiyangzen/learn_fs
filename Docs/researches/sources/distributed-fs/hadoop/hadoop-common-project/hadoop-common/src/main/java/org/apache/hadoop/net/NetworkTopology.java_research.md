# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/NetworkTopology.java

Purpose: `NetworkTopology` models a Hadoop cluster as a hierarchical tree of `InnerNode` switches/racks and leaf `Node` data nodes. It is used by HDFS and MapReduce to reason about rack locality, replica distance, random target selection, and sorting candidate nodes by network distance.

Important APIs/types/functions: `getInstance(Configuration)` reflects `net.topology.impl`; `add`, `remove`, `contains`, `getNode`, `getDatanodesInRack`, `getDistance`, `getDistanceByPath`, `isOnSameRack`, `chooseRandom`, `countNumOfAvailableNodes`, `getLeaves`, `sortByDistance`, `sortByDistanceUsingNetworkLocation`, `shuffle`, `decommissionNode`, `recommissionNode`, and `getNumOfNonEmptyRacks`. `InvalidTopologyException` protects against mixed leaf depths.

Control flow: writes acquire `netlock.writeLock`, reject inner-node additions/removals, enforce a consistent leaf depth, update rack counters, and delegate structural mutation to `clusterMap`. Reads use `readLock`. Random selection normalizes include/exclude scopes, subtracts excluded subtrees and excluded nodes, then chooses uniformly among valid leaves. Sorting groups active nodes by distance weight, shuffles each weight bucket, optionally applies a secondary sort, and rewrites the active prefix.

State and persistence: state is in-memory only: `clusterMap`, `depthOfAllLeaves`, rack counts, `rackMap`, `decommissionNodes`, and `clusterEverBeenMultiRack`. No disk persistence exists; callers rebuild topology from membership events and DNS-to-switch mappings.

Dependencies and integration: depends on `Node`, `NodeBase`, `InnerNode`, `InnerNodeImpl`, Hadoop `Configuration`, `CommonConfigurationKeysPublic.NET_TOPOLOGY_IMPL_KEY`, and `ReflectionUtils`. Consumers include block placement, read replica ordering, and topology-aware schedulers.

Risks: scope logic is path-string sensitive; wrong normalization changes random selection and available-node counts. `isChildScope` naming is unintuitive because it checks prefix containment after appending slashes. Empty-rack accounting relies on node names and can drift if callers mutate `Node` names/locations after insertion. `getDistance` depends on parent references belonging to this topology, while path-based distance does not. `RANDOM_REF` is static test state.

Test signals: `TestClusterTopology` and related topology tests exercise add/remove, rack counts, distances, random selection, sorting, and decommission/recommission behavior. Useful additional coverage is deterministic random selection with excluded inner scopes and empty rack transitions.
