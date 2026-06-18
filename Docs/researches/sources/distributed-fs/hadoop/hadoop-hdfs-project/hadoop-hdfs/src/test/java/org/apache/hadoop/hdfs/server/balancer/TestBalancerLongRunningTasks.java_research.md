# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerLongRunningTasks.java

## Purpose
`TestBalancerLongRunningTasks` contains slow, integration-heavy balancer tests for edge cases that require larger storage layouts or longer runtime: same-DataNode replica avoidance, RAM_DISK lazy persist behavior, minimum block size and source-node filtering, upgrade-domain and rack placement preservation, pinned blocks, top-node sorting, limiting over-utilized nodes, metrics duplicate registration, and max iteration time cancellation.

## Important APIs, Types, and Functions
The file uses `Balancer`, `BalancerParameters`, `BalancingPolicy.Node`, `ExitStatus`, `MiniDFSCluster`, `SimulatedFSDataset`, `LazyPersistTestCase`, `StorageType.RAM_DISK`, `BlockPlacementPolicyWithUpgradeDomain`, `BlockPlacementStatus`, `DatanodeManager`, `DataNodeTestUtils`, `DefaultMetricsSystem`, and `NameNodeConnector`. Helpers include `initConf`, `initConfWithRamDisk`, and `runBalancerAndVerifyBlockPlacmentPolicy`.

## Control Flow
Tests build MiniDFSClusters with carefully chosen storage capacities, storage types, racks, hosts, and upgrade domains. They create files to fill selected nodes, start new empty nodes, then call `Balancer.run` or run a single `Balancer.runOneIteration`. Placement tests verify every located block still satisfies the active placement policy after balancing. RAM_DISK tests create lazy-persist files, wait for lazy writer activity, add a new DataNode, and assert no RAM_DISK moves. Sorting tests create deterministic utilization levels, run one balancer iteration with `-sortTopNodes` or `-limitOverUtilizedNum`, then assert bytes/blocks moved and maximum usage.

## State and Persistence Behavior
The tests rely on cluster storage state, DataNode liveness state, block reports, heartbeats, deletion reports, lazy-persist memory settings, sticky-bit pinned blocks, upgrade-domain metadata in the datanode manager, and the metrics system. Most clusters are shut down in `@AfterEach` or try-with-resources, but `DefaultMetricsSystem` mode is temporarily changed.

## Dependencies and Integration Points
Integration points include DataNode storage-type policies, lazy persist, block placement policies, balancer dispatcher node selection, NameNode block reports, metrics registration, client socket timeout behavior, and HDFS configuration parsing for balancer CLI flags. The class reuses `TestBalancer` utility methods.

## Risks and Test Signals
Risks are slow runtime, timing and heartbeat sensitivity, platform restriction for pinned blocks, random block choice in sorting tests, and global metrics-system side effects. Signals include precise exit statuses, storage-type replica verification, block placement satisfaction, exact top-node movement counts, maximum usage expectations, and zero moved blocks when max iteration time is too short.
