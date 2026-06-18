# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDatanodeReport.java

Purpose: validates live/all/dead datanode reports, storage reports, upgrade-domain propagation from host config, expired heartbeat metrics, and reporting after all replicas of a block are deleted from disk.

Important APIs and types: `DFSClient.datanodeReport`, `getDatanodeStorageReport`, `DatanodeReportType`, `DatanodeAdminProperties`, `CombinedHostFileManager`, `HostsFileWriter`, `DatanodeStorageReport`, `StorageReport`, `LocatedBlock`, and metrics assertions.

Control flow: upgrade-domain test writes include-host JSON entries, refreshes nodes, and checks report domains. Main report test starts four DNs, checks ALL/LIVE/DEAD counts and storage IDs, shuts down one DN, waits until it appears dead, rechecks counts, and asserts `ExpiredHeartbeats`. Missing-block test writes a file, deletes block files on DNs, expects read failure, triggers heartbeats, and verifies located block locations drop to zero.

State and persistence: creates host include files, starts/shuts down datanodes, creates and corrupts HDFS block files, and observes NameNode metrics and block-location metadata.

Dependencies and integration: integrates host include provider, datanode manager refresh, DFSClient reports, fsdataset storage reports, block corruption/deletion handling, and FSNamesystem metrics.

Risks: waits for dead-node detection by polling, shared static configuration can retain values across tests, and direct block-file deletion bypasses normal datanode workflows.

Test signals: report counts, upgrade-domain values, datanode info equality with storage reports, matching storage IDs, `ExpiredHeartbeats` counter, read exception for missing block, and zero locations after deletion acknowledgement.
