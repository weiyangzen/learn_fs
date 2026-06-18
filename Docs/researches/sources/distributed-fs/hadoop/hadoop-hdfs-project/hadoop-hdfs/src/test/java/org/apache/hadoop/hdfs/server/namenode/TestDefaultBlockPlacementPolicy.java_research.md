# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDefaultBlockPlacementPolicy.java

Purpose: Verifies default block placement choices for local, rack-local, remote, decommissioned, no-local-rack, and DFSNetworkTopology scenarios.

Important APIs/types/functions: Uses `MiniDFSCluster` with racks/hosts, `StaticMapping`, `FSNamesystem.startFile`, `NamenodeProtocols.addBlock`, `abandonBlock`, `DatanodeManager`, `DatanodeAdminManager`, `DFSNetworkTopology`, `CreateFlag.NO_LOCAL_RACK`, and `AddBlockFlag.NO_LOCAL_RACK`.

Control flow: Setup creates five DataNodes across three racks. `testPlacement` starts files and calls `addBlock` repeatedly, checking first replica rack when applicable. Dedicated tests map a remote client, use a local DataNode client, set NO_LOCAL_RACK flags, rebuild with DFSNetworkTopology, decommission the only local-rack node, and test an unmapped remote client.

State and persistence behavior: Focuses on live placement decisions and decommission state. Allocated blocks are abandoned after checks; restart persistence is not tested.

Dependencies and integration points: Integrates NameNode file creation, block allocation, network topology resolution, static rack mapping, and decommission filtering.

Risks: The test checks placement order, so policy changes that remain valid but alter ordering can fail it.

Test signals: Replica count equals replication factor, first replica rack matches expected rack when required, local rack is excluded for NO_LOCAL_RACK and decommissioned cases, and configured topology is `DFSNetworkTopology`.
