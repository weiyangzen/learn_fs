# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSUpgrade.java

Purpose: validates NameNode and DataNode upgrade behavior across valid storage layouts, invalid storage states, multiple storage directories, rolling-upgrade rejection during upgrade, and layout-version boundaries.

Important APIs and types: `UpgradeUtilities`, `MiniDFSCluster.Builder`, `StartupOption.UPGRADE/REGULAR`, `StorageInfo`, `Storage`, `DataNodeLayoutVersion`, `NNStorage` image/edit filename helpers, `InconsistentFSStateException`, `RemoteException`, and `TestParallelImageWrite`.

Control flow: `initialize` prepares master upgrade fixtures. `testUpgrade` loops over one and two storage directories, creates current/previous NN and DN states, starts clusters with `format(false)` and unmanaged directories, verifies success cases, and asserts failures for existing previous dirs, future layout versions, newer CTime, missing edits/image files, corrupt VERSION files, and too-old/future NameNode versions. A four-directory case verifies parallel image writes.

State and persistence: directly creates, deletes, and corrupts NameNode/DataNode storage directories under test storage. Verifies `current`, `previous`, `VERSION`, `seen_txid`, fsimage, in-progress edits, and block-pool finalized directories.

Dependencies and integration: exercises storage upgrade code, block pool initialization, safe mode, rolling upgrade guardrails, image write parallelism, and checksum fixtures from `UpgradeUtilities`.

Risks: hard-coded `EXPECTED_TXID`, directory-sensitive checksum expectations, disabled manual failure test, and broad filesystem mutation make failures environment-sensitive.

Test signals: expected directory existence, checksum equality with master fixtures, image parity across storage dirs, expected startup exceptions, failed block-pool service, and layout-version exception checks.
