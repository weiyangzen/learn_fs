# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDecommissioningStatus.java

Purpose: Tests DataNode decommissioning status counters, CLI/API reporting, dead-node decommission cases, and recovery when decommissioning risks data loss.

Important APIs/types/functions: Uses `HostsFileWriter`, `DatanodeManager.refreshNodes`, `DatanodeAdminManager`, `DatanodeDescriptor.getLeavingServiceStatus`, `BlockManagerTestUtil.recheckDecommissionState`, `DFSAdmin.report -decommissioning`, `DistributedFileSystem.getDataNodeStats`, and MiniDFSCluster stop/restart helpers.

Control flow: Setup creates hosts/exclude files and speeds heartbeat, redundancy, and decommission intervals. Tests decommission one and then two nodes with closed and open files; restart a decommissioning DN; decommission an already-dead DN; and decommission all replicas before adding capacity so reconstruction can recover.

State and persistence behavior: Focuses on in-memory admin states, tracked node counts, under-replicated counts, out-of-service-only replicas, open-file under-replication, and exclude-host file configuration.

Dependencies and integration points: Integrates block reports, replication monitor, lease/open-file behavior, DFSAdmin output parsing, Java DataNode reports, dead DataNode handling, and reconstruction queues.

Risks: Timing-sensitive and dependent on block reports reaching the BlockManager before decommission begins. Helpers wait for expected block counts to reduce flakiness.

Test signals: Expected decommission status triples, DFSAdmin counts, Java decommissioning reports, descriptor states, missing/low-redundancy counters, pending reconstruction counters, and cleanup through empty exclude files.
