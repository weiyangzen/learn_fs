# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCheckpoint.java

Purpose: Broad regression coverage for HDFS NameNode checkpoint creation, transfer, import, storage locking, namespace persistence, and SecondaryNameNode behavior. It uses `MiniDFSCluster`, `SecondaryNameNode`, `FSImage`, `NNStorage`, `NamenodeProtocols`, `TransferFsImage`, and `CheckpointFaultInjector` to exercise both normal checkpoint flows and many interrupted flows.

Important APIs and helpers: `startSecondaryNameNode`, `checkFile`, `cleanupFile`, `assertLockFails`, `assertClusterStartFailsWhenDirLocked`, `assertParallelFilesInvariant`, and `DoCheckpointThread`. The suite drives `SecondaryNameNode.doCheckpoint`, `NameNode.format`, `DFSAdmin -saveNamespace`, `rollEditLog`, `saveNamespace`, `restoreFailedStorage`, and `TransferFsImage` download/upload APIs. Mockito fault injection simulates failures around edit rolling, image upload, MD5 rename, edit rename, merge, and corrupt/short image transfer.

Control flow: Tests isolate MiniDFS storage, install a mock fault injector, run checkpoint or failure scenarios, then reset the injector and prove recovery by restart or a later checkpoint. Concurrent tests use two SecondaryNameNodes and `DelayAnswer` to force races around image save or edit manifest retrieval.

State and persistence behavior: The file validates `fsimage_N`, finalized and in-progress edit segments, MD5 files, VERSION storage metadata, storage locks, checkpoint directories, legacy OIV image retention, and most-recent-checkpoint txid. It proves incomplete transfers do not truncate images, temporary edits are cleaned, out-of-order checkpoints preserve the highest txid, failed storage dirs can be restored, and checkpoint import works only into an empty NameNode image set.

Dependencies and integration points: Integrates HTTP image transfer, RPC `NamenodeProtocol`, DFSAdmin, metrics `NameNodeActivity`, safe mode, delegation tokens, lease manager fsimage state, federated NameNode topologies, local filesystem permissions, and namespace identity checks through `StorageInfo` and `CheckpointSignature`.

Risks: Many tests depend on exact txid counts, local permission semantics, timing-sensitive checkpoint threads, and Java-version-specific transfer error text. Fault injection must be reset in `finally` blocks to avoid cross-test contamination.

Test signals: File existence and replication after restart, expected checkpoint txid lists, image/edit transfer metrics, absence of temp files, expected exceptions, storage lock failures, CLI parsing results, lease/delegation-token reload behavior, and byte identity for matching files across NameNode and SecondaryNameNode current directories.
