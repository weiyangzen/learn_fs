# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSetrepIncreasing.java

Purpose: End-to-end tests for increasing replication with FsShell, simulated-storage behavior, and edge cases involving storage policy and erasure-coded files.

Important APIs and types: `FsShell -setrep`, `MiniDFSCluster`, `SimulatedFSDataset`, `DistributedFileSystem`, `BlockLocation`, `NameNodeProxies.createProxy`, `ClientProtocol.enableErasureCodingPolicy`, `ClientProtocol.setErasureCodingPolicy`, and `StripedFileTestUtil.getDefaultECPolicy`.

Control flow: Static `setrep` builds a 10-datanode cluster, optionally installs `SimulatedFSDataset`, configures default replication and short block-report/pending reconstruction intervals, creates a file with `TestDFSShell`, runs `-setrep -w`, refreshes the filesystem, and validates each block location has `toREP` hosts. `testSetrepIncreasing` and `testSetrepIncreasingSimulatedStorage` call it for 3 to 7 replicas. `testSetRepWithStoragePolicyOnEmptyFile` sets HOT storage policy on a directory, creates an empty file, and sets replication to 4 without error. `testSetRepOnECFile` enables EC at root, creates an EC file, runs `-setrep 2`, expects a skip message, and validates replication remains 1.

State and persistence behavior: Test state lives in MiniDFSCluster metadata and block placement. Shell output is captured for the EC skip message.

Dependencies and integration points: Covers FsShell, NameNode block-management convergence, simulated datanode storage, storage policy metadata, EC policy metadata, and client RPC proxy setup.

Risks and test signals: Setrep convergence depends on block reports and reconstruction timing. Passing signals replication changes are honored for replicated files, tolerated for empty storage-policy files, and intentionally ignored for erasure-coded files.
