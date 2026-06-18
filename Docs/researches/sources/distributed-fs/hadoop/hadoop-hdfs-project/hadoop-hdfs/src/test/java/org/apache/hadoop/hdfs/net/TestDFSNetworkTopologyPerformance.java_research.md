<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/net/TestDFSNetworkTopologyPerformance.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/net/TestDFSNetworkTopologyPerformance.java

Purpose: Disabled benchmark-style comparison between generic `NetworkTopology.chooseRandom` with retry filtering and `DFSNetworkTopology.chooseRandomWithStorageType`.

Important APIs/types/functions: `NetworkTopology`, `DFSNetworkTopology`, `DFSTestUtil.createDatanodeStorageInfos`, `DatanodeDescriptor.hasStorageType`, `addNodeByTypes`, `getRandLocation`, `getRandType`, `printMemUsage`, and constants `NODE_NUM=2000`, `OP_NUM=20000`.

Control flow: `init` precomputes random racks and hosts. Each disabled test creates both topology implementations, fills the `types` array with a distribution, adds identical nodes to both clusters, sleeps for measurement stability, then times old retry-based selection and/or direct storage-aware selection. Scenarios cover uniform types, unbalanced archive minority, all same type, configurable percentage, and a mixed first-generic-then-storage-aware approach.

State and persistence behavior: All state is synthetic and in-memory. Timing samples are stored in `records`; memory usage is logged through `Runtime`.

Dependencies and integration points: Used as exploratory performance evidence for HDFS storage-type-aware placement. It is not a CI correctness gate because the class is annotated `@Disabled`.

Risks: Random topology and type distribution make numbers non-reproducible unless seeded externally. Assertions only guard non-null/type correctness during benchmarking. Sleep and JVM memory logging are approximate.

Test signals: When manually enabled, log output showing total time, average time, average trials, and memory usage is the useful signal. Normal CI should skip it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/net/TestDFSNetworkTopologyPerformance.java -->
