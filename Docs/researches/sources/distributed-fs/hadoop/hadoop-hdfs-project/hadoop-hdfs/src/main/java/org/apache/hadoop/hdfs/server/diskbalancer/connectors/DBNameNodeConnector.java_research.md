# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/connectors/DBNameNodeConnector.java

Purpose: live-cluster connector that reads DataNode and storage-volume information from the NameNode for diskbalancer.

Important APIs/types/functions: constructor disables `NameNodeConnector` id-file writing and creates a `NameNodeConnector` named `DiskBalancer` with `/system/diskbalancer.id`. `getNodes()` calls `getLiveDatanodeStorageReport()`, maps each `DatanodeInfo` to `DiskBalancerDataNode`, maps each `StorageReport` to `DiskBalancerVolume`, and adds volumes to the node. `getConnectorInfo()` identifies the NameNode URI.

Control flow: for each live DataNode storage report, the connector sets node UUID/IP/hostname/IPC port, then iterates storage reports to set capacity, failed flag, DFS used, storage ID as UUID, skip flag for read-only-shared or failed volumes, storage type name, transient flag, and finally updates node density via `addVolume()`.

State and persistence behavior: holds `clusterURI` and a `NameNodeConnector`. It does not persist output but uses `NameNodeConnector` for NameNode RPC state. The static id path is configured but id-file writing is disabled because DataNode admission controls concurrent diskbalancer execution.

Dependencies and integration points: depends on HDFS balancer `NameNodeConnector`, `DatanodeStorageReport`, `StorageReport`, `DatanodeStorage`, and diskbalancer data model classes. Feeding this connector into `DiskBalancerCluster` powers report and plan commands on real clusters.

Risks: only live DataNodes are considered. `reserved` is not populated from storage reports here, so effective-capacity behavior depends on defaults or JSON/test data. Volume path is not available until later DataNode RPC path population. A failure connecting to NameNode aborts command execution.

Test signals: mini-cluster diskbalancer command tests exercise live storage report mapping; `DiskBalancerTestUtil` builds imbalanced DataNodes used by plan/execute tests.
