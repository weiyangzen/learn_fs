# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestBackupNode.java

## Purpose

`TestBackupNode` validates HDFS BackupNode and CheckpointNode behavior: startup state, checkpoint upload, edit-log tailing, storage-directory equivalence, authentication failure handling, read/write restrictions, crash handling, and reading data through a backup node.

## Important APIs, Types, and Functions

Key helpers include `getBackupNodeDir`, `startBackupNode`, `waitCheckpointDone`, `testBNInSync`, `assertStorageDirsMatch`, and `testCheckpoint`. The class uses `NameNode.createNameNode`, `BackupNode`, `BackupImage`, `Checkpointer`, `FSImageTestUtil`, `FileJournalManager.EditLogFile`, `StorageDirectory`, `MiniDFSCluster`, `HAUtil.setAllowStandbyReads`, `NamenodeProtocols.rollEditLog`, `DFSTestUtil`, and HA/backup configuration keys such as `DFS_NAMENODE_BACKUP_ADDRESS_KEY` and backup HTTP address.

## Control Flow

`setUp` deletes the MiniDFSCluster base directory and prepares checkpoint/backup name directories. `startBackupNode` configures name and edits dirs, starts a NameNode in checkpoint or backup role, and asserts safe mode plus standby HA state. `startBackupNodeWithIncorrectAuthentication` starts a simple-auth primary, switches backup config to Kerberos with invalid keytab, and expects an IOException rather than a null-pointer abort. Checkpoint tests create namespace edits, start a checkpoint/backup node, wait until the active NameNode records a checkpoint at or beyond a txid, compare storage dirs, restart without formatting, and repeat checkpoints.

## State and Persistence Behavior

This file is heavily persistence-oriented. It verifies fsimage checkpoint transfer to the active NameNode, in-progress edits behavior during BackupNode shutdown, namespace survival across non-format restarts, deletion persistence (`file1` removed while `file2` remains), and identical name/current directories excluding `VERSION`. The tailing test confirms a BackupNode receives edits as files are created, rolls edit logs with the active, uploads checkpoint images, restarts from storage, and tolerates unclean backup-node stop while active edits continue.

## Dependencies and Integration Points

Integration points include active NameNode edit logging, backup node edit tailing, checkpoint image upload, HA standby reads, NameNode RPC addresses, DataNode HA-style dual NameNode config for backup reads, security authentication setup, and filesystem clients pointed at backup-node RPC addresses. `FSImageTestUtil` provides the main storage-level assertions.

## Risks and Edge Cases

The tests depend on local ports, filesystem cleanup, and timing loops for checkpoint completion and edit tailing. Authentication regression coverage checks the error message contains `Running in secure mode`. The read/write behavior differs by role: BackupNode may serve reads, CheckpointNode may not, and writes through backup-node RPC must fail. The final tailing test has a risky-looking `assertStorageDirsMatch(cluster.getNameNode(), backup)` after backup can be nulled in the finally path; the assertion executes after cleanup and depends on the retained object state from the try path.

## Test Signals

Signals include backup/checkpoint startup in safe mode/standby, `FSImageTestUtil.assertNNHasCheckpoints`, identical storage dirs excluding `VERSION`, current segment txid matching after `rollEditLog`, backup namespace visibility for created paths, latest edit log remaining in-progress after backup stop, no active failure after unclean backup stop, failed writes to backup, role-dependent backup reads, matching data read through active and backup node, and token-authentication startup failure avoiding NPE.
