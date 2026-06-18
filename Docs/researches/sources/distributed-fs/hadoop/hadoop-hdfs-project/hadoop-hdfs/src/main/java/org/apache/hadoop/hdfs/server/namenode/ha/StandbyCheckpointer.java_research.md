# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/StandbyCheckpointer.java

## Purpose

`StandbyCheckpointer.java` runs inside a standby NameNode to periodically save a local namespace checkpoint and upload it to peer NameNodes. The source was read as a complete 513-line file.

## Important APIs, Types, and Functions

The class owns `CheckpointConf`, `FSNamesystem`, `CheckpointerThread`, remote and local HTTP addresses, upload thread factory, cancellation state, and per-receiver upload state. Important methods are constructor, `setNameNodeAddresses`, `start`, `stop`, `triggerRollbackCheckpoint`, `doCheckpoint`, `cancelAndPreventCheckpoints`, `getLastCheckpointTime`, and `countUncheckpointedTxns`. The nested `CheckpointReceiverEntry` tracks last upload and whether this standby is primary for a receiver.

## Control Flow

The background thread runs as the login user, sleeps for the checkpoint check period, refreshes Kerberos credentials, checks for rollback image need, transaction threshold, or elapsed-period threshold, then creates a `Canceler` under `cancelLock` unless checkpoints are temporarily prevented. `doCheckpoint` takes the checkpoint lock, verifies edit log is open for read, compares current and previous checkpoint txids, chooses `IMAGE_ROLLBACK` during rolling upgrade when needed, calls `FSImage.saveNamespace`, optionally writes legacy OIV output, releases the lock, then uploads the saved image to remote NameNodes using a bounded executor. Uploads run when this standby is primary for the receiver or the receiver has been quiet long enough.

## State and Persistence Behavior

The checkpointer persists fsimage or rollback fsimage files in local NameNode storage and may upload them to remote active NameNodes through `TransferFsImage`. It updates `lastCheckpointTime` after success and receiver upload timestamps after accepted uploads. Cancellation is transient, but it protects state transition to active from racing with checkpoint save/upload.

## Dependencies and Integration Points

It integrates with `CheckpointConf`, `FSNamesystem`, `FSImage`, `TransferFsImage`, `NameNodeFile`, `HAUtil`, `DFSUtil`, `NameNode`, `CheckpointFaultInjector`, `Canceler`, `SaveNamespaceCancelledException`, `MultipleIOException`, and secure `SubjectInheritingThread` execution.

## Risks and Edge Cases

Checkpoint cancellation and failover prevention are critical; a standby must not continue a checkpoint while becoming active. Upload rejection can be normal when the peer is standby, already has a newer image, or recently accepted another image. More than half of uploads failing with exceptions aborts the checkpoint. Rollback checkpoint flags must be cleared only after rollback image exists.

## Test Signals

Tests should cover threshold and period triggering, rollback checkpoint triggering, no-op when txid unchanged, saveNamespace cancellation, prevent window during failover, parallel and serial upload modes, upload result handling, majority upload exception threshold, receiver quiet period/primary logic, legacy OIV errors, secure relogin, and remote address validation.
