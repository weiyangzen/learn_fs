# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSFinalize.java

Purpose: This upgrade/finalization integration test validates that NameNode, DataNode, and block-pool finalization remove `previous` directories while preserving valid `current` storage contents.

Important APIs/types/functions: `UpgradeUtilities`, `MiniDFSCluster.Builder`, `StartupOption.REGULAR`, `cluster.finalizeCluster`, `cluster.triggerBlockReports`, `FSImageTestUtil`, `BlockPoolSliceStorage`, and `DataStorage.STORAGE_DIR_FINALIZED`.

Control flow: For one and two storage directories, the test initializes synthetic upgrade storage states. It runs two variants for whole DataNode storage finalization, first with existing `previous` directories and then idempotently without them. It then resets directories and repeats for block-pool-level finalization. After each finalization, it triggers block reports, waits briefly for asynchronous DataNode/block-pool work, and calls `checkResult`.

State and persistence behavior: This file is entirely about on-disk HDFS storage state. `checkResult` validates that NameNode `current` dirs are reasonable and parallel-identical, DataNode current checksums match master data, `previous` dirs are gone, and block-pool finalized content matches expected checksums. Duplicate replica deletion and block scanning are disabled to keep deliberately mirrored test directories unchanged.

Dependencies and integration points: It uses the shared upgrade test harness, HDFS storage directory configuration keys, MiniDFSCluster startup without formatting or managed dirs, and DataNode block reports as the finalization trigger.

Risks and test signals: Signals are filesystem existence checks and checksum comparisons. Timing risk exists in the fixed one-second wait for asynchronous finalization. Because it disables normal scanners and deletion, it tests finalization behavior in a controlled upgrade-fixture environment rather than arbitrary production storage churn.
