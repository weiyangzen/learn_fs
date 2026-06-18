<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStorageStateRecovery.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStorageStateRecovery.java

## Purpose
`TestDFSStorageStateRecovery` verifies NameNode, DataNode, and block-pool recovery behavior for combinations of HDFS storage directories: `current`, `previous`, `previous.tmp`, and `removed.tmp`. It encodes expected recovery outcomes from the HDFS upgrade test plan.

## Important APIs, Types, and Functions
- `testCases` is the central truth table with input directory existence and expected recovery/current/previous outcomes.
- `createNameNodeStorageState`, `createDataNodeStorageState`, and `createBlockPoolStorageState` materialize storage states using `UpgradeUtilities`.
- `checkResultNameNode`, `checkResultDataNode`, and `checkResultBlockPool` verify directory existence and checksums against master storage contents.
- `createCluster` starts a `MiniDFSCluster` over preexisting unmanaged storage without formatting.
- `setUp` calls `UpgradeUtilities.initialize`; `tearDown` shuts down active clusters.

## Control Flow
`testNNStorageStates` iterates one and two storage-directory configurations over all NameNode cases, builds the input layout, starts the cluster when recovery should succeed, verifies post-recovery state, or expects startup failure. The empty-storage failure case also checks for the "NameNode is not formatted" message.

`testDNStorageStates` creates valid NameNode storage first, starts a NameNode-only cluster, then creates DataNode storage for each case and starts one DataNode. Empty DataNode storage is allowed to create/format `current`; other cases either verify checksums or assert the DataNode is down.

`testBlockPoolStorageStates` mirrors DataNode recovery at the block-pool directory level and asserts block-pool service liveness for failures.

## State and Persistence Behavior
The test is entirely about persistent on-disk storage state. It deliberately creates, removes, and recovers directories under configured name/data dirs, then compares checksums to ensure `previous` contents are not modified and `current` contents match expected master layouts. It disables DataNode scanning for speed and repeatability.

## Dependencies and Integration Points
It integrates with storage upgrade/recovery code, NameNode startup, DataNode startup, block-pool service startup, `FSImageTestUtil.findNewestImageFile`, `Storage.STORAGE_DIR_CURRENT/PREVIOUS`, and `UpgradeUtilities` checksum fixtures.

## Risks
The truth table is dense and has repeated case labels, so maintaining expected outcomes requires care. Several assertions only run when directories should exist; unexpected extra directories are not always explicitly rejected. The tests repeatedly start and stop clusters and can be slow or sensitive to leftover storage state if cleanup fails.

## Test Signals
Signals include startup success/failure, DataNode/BP service liveness, exact directory and VERSION/image/seen_txid checks for NameNode current state, and checksum comparisons for DataNode/current, block-pool/current, and previous directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStorageStateRecovery.java -->
