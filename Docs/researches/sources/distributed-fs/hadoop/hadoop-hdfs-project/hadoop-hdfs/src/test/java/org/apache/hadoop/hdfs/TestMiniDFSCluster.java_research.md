# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestMiniDFSCluster.java

## Purpose
This file tests `MiniDFSCluster` construction, isolation, restart, storage, host, topology, and DataNode port-configuration behavior. It protects the local test harness itself rather than a single HDFS feature.

## Important APIs, Types, And Functions
Key tests are `testClusterWithoutSystemProperties`, `testClusterSetStorageCapacity`, `testIsClusterUpAfterShutdown`, `testClusterSetDatanodeHostname`, `testClusterSetDatanodeDifferentStorageType`, `testClusterNoStorageTypeSetForDatanodes`, `testSetUpFederatedCluster`, and `testStartStopWithPorts`. Helpers `newCluster` and `verifyStorageCapacity` construct DataNodes with two volumes and inspect `FsVolumeImpl` capacities through `FsDatasetSpi.FsVolumeReferences`.

## Control Flow
Each test builds a cluster with specific builder options, waits active, then inspects resulting directories, DataNode configuration, NameNode HA state, HTTP address propagation, storage locations, or explicitly assigned ports. The storage-capacity test creates a file and repeatedly restarts DataNodes and NameNodes in different orders, verifying custom capacities survive. The federated test builds a simple two-namespace HA topology, transitions active NameNodes, and restarts individual NameNodes.

## State And Persistence
State includes MiniDFSCluster base directories, DataNode storage type arrays, storage capacities, configured hostnames, HA NameNode state, per-NameNode suffixed configuration keys, shutdown state returned by `isClusterUp`, and DataNode IPC/HTTP ports. Capacity persistence across NameNode/DataNode restarts is the main persistence signal.

## Dependencies And Integration Points
The tests use `MiniDFSCluster.Builder`, `MiniDFSNNTopology`, `DFSUtil.addKeySuffixes`, `DataNode.getStorageLocations`, `FsVolumeImpl`, `NetUtils.getFreeSocketPorts`, JUnit assumptions for Linux-only hostname behavior, and `LambdaTestUtils.intercept` for port-list validation errors.

## Risks
Port selection is explicitly racy because another process can bind a free port before cluster startup. Tests use local filesystem paths and system properties, so cleanup and property restoration matter. The storage-capacity helper assumes exactly two volumes per DataNode and casts to `FsVolumeImpl`.

## Test Signals
Signals include correct base data directory selection without `test.build.data`, exact custom capacities after all restart orderings, `isClusterUp` eventually false after shutdown, preserved `dfs.datanode.hostname`, expected storage-location counts, active/standby HA states, consistent federated HTTP address keys, validation exceptions for mismatched port counts, and exact DataNode info/IPC port mappings.
