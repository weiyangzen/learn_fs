<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStartupVersions.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStartupVersions.java

## Purpose
This test verifies DataNode startup compatibility against NameNode version metadata across layout version, namespace ID, cluster ID, block pool ID, and filesystem state creation time combinations.

## Important APIs, Types, and Functions
- `StorageData` packages a `StorageInfo` and block pool ID for synthetic version files.
- `initializeVersions` generates the compatibility matrix: old/current/future layout versions, current/invalid namespace IDs, past/current/future cTimes, plus invalid cluster/block-pool scenarios.
- `isVersionCompatible` encodes expected compatibility rules and is the oracle for the test.
- `UpgradeUtilities` creates NameNode/DataNode storage directories and version files.
- `MiniDFSCluster` starts a NameNode without DataNodes, then starts one DataNode per matrix row.

## Control Flow
`testVersions` initializes upgrade utilities and storage-state configuration, creates current NameNode storage, starts a NameNode with no DataNodes, captures the actual NameNode version fields, and iterates through all `StorageData` variants. For each case it creates DataNode storage, writes a version file using the candidate metadata, attempts DataNode startup, and compares `cluster.isDataNodeUp()` to `isVersionCompatible`.

## State and Persistence Behavior
The test writes on-disk VERSION files and storage directory layouts through `UpgradeUtilities`. NameNode state persists for the whole test; DataNode directories are recreated for each case, and DataNodes are shut down after each attempt. Compatibility is stateful around layout versions, namespace IDs, cluster IDs, block pool IDs, and cTimes.

## Dependencies and Integration Points
It exercises startup checks in DataNode storage loading, NameNode/DataNode version compatibility, block-pool identity validation, upgrade-related layout-version rules, and cluster startup paths that use existing storage (`format(false)`, unmanaged data/name dirs).

## Risks
The oracle duplicates compatibility logic, so it can drift from production startup rules. `invalidClusterID` is set to the same string as `clusterID` in the version array, which weakens the intended invalid-cluster case unless overwritten by the live NameNode cluster ID. The test is expensive and uses a broad timeout.

## Test Signals
The primary signal is a matrix assertion: for every synthetic DataNode version file, actual DataNode liveness must match the encoded compatibility rules. Logs print every case's version tuple for diagnosis.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStartupVersions.java -->
