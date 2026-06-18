# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/UpgradeUtilities.java

Purpose: Static helper library for HDFS upgrade tests. It creates canonical populated NameNode/DataNode storage directories, copies them into test layouts, computes checksums, writes VERSION files, corrupts files, and exposes current layout/namespace/cluster/block-pool identifiers.

Important APIs and types: `MiniDFSCluster`, `DFSTestUtil.formatNameNode`, `NamenodeProtocols.versionRequest`, `Storage`, `StorageDirectory`, `NNStorage`, `DataStorage`, `BlockPoolSliceStorage`, `StorageInfo`, `DataNodeLayoutVersion`, `LayoutVersion.Feature.FEDERATION`, `CRC32`, and `FileUtil`.

Control flow: `initialize` wipes the test root, formats NameNode/DataNode storage, starts a cluster without managing dirs, records namespace/cluster/block-pool IDs and cTime, writes files before and after `saveNamespace`, shuts down, removes lock files, and computes master checksums for NameNode, DataNode, block pool, finalized, and rbw dirs. Other helpers build name/data dir config strings, create empty dirs, copy master NameNode/DataNode/block-pool storage into requested parents, create NameNode/DataNode/block-pool VERSION files, corrupt a target byte sequence in a file, report current layout/IDs from a running cluster or cached master, and create empty block-pool dirs.

State and persistence behavior: Maintains static master directories under `MiniDFSCluster.getBaseDirectory()` and cached checksums/IDs. It deliberately mutates local filesystem storage layouts and VERSION properties for upgrade tests.

Dependencies and integration points: Integrates local filesystem copying, HDFS storage layout internals, NameNode saveNamespace, DataNode block-pool storage, version files, and upgrade test setup.

Risks and test signals: `createDataNodeStorageDirs` appears to alter the master datanode VERSION storage UUID after copying rather than the copied directory, so callers should inspect expected UUID behavior. The utility is foundational: incorrect cleanup, checksum exclusions, or VERSION generation can invalidate many upgrade tests.
