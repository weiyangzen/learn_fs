# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/DataNodeCluster.java

`DataNodeCluster` is a standalone utility for launching many DataNodes in one process without a NameNode. It assumes an external NameNode is already configured and is mainly useful for NameNode scalability benchmarks, especially with simulated datasets and synthetic block injection.

The `main` method parses options for DataNode count, block pool ID, rack count, replication, data directories, simulated capacity, block injection, and whether to use configured DataNode addresses. It validates counts and required NameNode authority, sets `test.build.data`, formats DataNode directories through `MiniDFSCluster`, creates optional rack assignments with `getUniqueRackPrefix`, starts DataNodes with `StartupOption.REGULAR`, sleeps ten seconds for registration, and optionally injects sequential blocks into each DataNode and neighboring replicas.

State persists under `/tmp/DataNodeCluster` by default unless `-d` is supplied. Simulated mode uses `SimulatedFSDataset`; injection writes block metadata for the provided block pool ID and is intended to match NameNode edits created by `CreateEditsLog`. Dependencies include `MiniDFSCluster`, `HdfsConfiguration`, `FileSystem.getDefaultUri`, `FsDatasetSpi.Factory`, `SimulatedFSDataset`, `CreateEditsLog`, `Block`, `DNS`, and `DFSUtil`.

Risks include process exits on parse errors, option-order sensitivity for `-inject` versus `-simulated`, clobbering default `/tmp` state, heuristic startup sleeps, and probabilistic rack-prefix uniqueness. Signals are console output for startup, rack assignment, injection ranges, and caught DataNode creation/format errors.
