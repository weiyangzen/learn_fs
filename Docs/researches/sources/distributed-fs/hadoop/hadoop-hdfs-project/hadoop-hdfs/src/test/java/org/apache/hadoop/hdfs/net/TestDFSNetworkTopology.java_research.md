<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/net/TestDFSNetworkTopology.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/net/TestDFSNetworkTopology.java

Purpose: Correctness suite for `DFSNetworkTopology`, especially storage-type-aware counts and random selection with scopes and exclusions.

Important APIs/types/functions: Uses static `DFSNetworkTopology CLUSTER`, `DFSTopologyNodeImpl.getChildrenStorageInfo`, `getSubtreeStorageCount`, `chooseRandomWithStorageType`, `chooseRandomWithStorageTypeTwoTrial`, `DatanodeDescriptor`, `DatanodeInfoBuilder`, `DatanodeStorageInfo`, and `StorageType`.

Control flow: `setupDatanodes` builds 25 datanodes across a multi-level topology with varied storage types, adds them to the cluster, and decommissions two nodes. Tests assert child storage maps at multiple levels, add and remove five nodes and verify counts, repeatedly select nodes for desired storage types, exercise excluded node sets and excluded scopes, verify wrapper `"~"` excluded-scope behavior, handle nonexistent scopes, and cover edge cases involving `DatanodeInfo` rather than `DatanodeDescriptor` in exclusions.

State and persistence behavior: In-memory topology is mutated by adding/removing nodes and setting decommission state. There is no disk persistence. Because `CLUSTER` is static and `setupDatanodes` adds nodes before each test, behavior depends on `DFSNetworkTopology.add` being idempotent for existing node identity or tests would accumulate state.

Dependencies and integration points: Covers HDFS block-placement support code, Hadoop network topology abstractions, storage media counts, and DataNode descriptor identity/equality behavior.

Risks: Random selection is validated by membership over repeated trials, not exact distribution. Static cluster reuse can hide or amplify state leakage. Several tests depend on hard-coded host/rack mappings and comments must stay aligned with arrays.

Test signals: Passing indicates storage counts propagate correctly, node removals decrement ancestor counts, storage-type selection respects desired scope, excluded scope, and excluded nodes, and null/nonexistent cases are safe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/net/TestDFSNetworkTopology.java -->
