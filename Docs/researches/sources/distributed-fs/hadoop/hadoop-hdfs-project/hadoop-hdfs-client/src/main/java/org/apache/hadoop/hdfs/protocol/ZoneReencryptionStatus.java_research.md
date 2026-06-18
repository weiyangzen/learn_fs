# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ZoneReencryptionStatus.java

## Purpose
`ZoneReencryptionStatus` tracks the state of re-encryption for an HDFS encryption zone. It is consumed by crypto admin/listing APIs and updated by NameNode re-encryption logic. The class comment states that `FSDirectory` locking provides synchronization except for test-only methods.

## Important APIs, Types, and Functions
`State` has three values: `Submitted`, `Processing`, and `Completed`. The nested `Builder` validates that `id`, `state`, `ezKeyVersionName`, and `submissionTime` are set, then populates all status fields. Public getters expose zone id/name, state, key version, submission/completion time, cancellation, last checkpoint file, files re-encrypted, and failure count.

Mutable operations include `reset`, `setZoneName`, `cancel`, package-private `setState`, `markZoneCompleted`, `markZoneSubmitted`, and `updateZoneProcess`. `markZoneCompleted` loads completion time, cancellation flag, metrics, and clears the checkpoint. `markZoneSubmitted` resets then restores submitted state from protobuf. `updateZoneProcess` updates checkpoint and metrics while work is active.

## Control Flow
The object starts in `Submitted` state with zeroed times/metrics after `reset`. NameNode re-encryption code updates it as edit-log/protobuf information is replayed or as the re-encryption handler makes progress. Listing code resolves and sets `zoneName` for user-facing output.

## State and Persistence Behavior
This is a mutable status object. The comment explicitly says `state` is in-memory only: after failover it is restored as `Submitted`, or `Completed` if `completionTime != 0`, based on persisted protobuf fields. Persistent fields include id, key version, submission/completion times, cancellation, checkpoint file, and metrics. The last checkpoint stores a file name rather than inode id so replay can resume even if the inode was removed.

## Dependencies and Integration Points
It depends on `HdfsProtos.ReencryptionInfoProto` and Hadoop `Preconditions`. It integrates with `EncryptionZoneManager`, `ReencryptionHandler`, `ReencryptionUpdater`, `FSDirEncryptionZoneOp`, `FSNamesystem.listReencryptionStatus`, `DistributedFileSystem.listReencryptionStatus`, `CryptoAdmin`, and router/federation client protocols.

## Risks and Edge Cases
Correct lock ownership is critical because the class is mutable. Builder validation rejects id/submission time zero, which assumes zero is never a valid value. Failover semantics depend on protobuf restoration and completion time. `setZoneName` rejects null. Metrics can be reset or overwritten during state transitions, so tests should confirm no accidental loss during cancellation/completion.

## Test Signals
`hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestReencryption.java` heavily exercises re-encryption status listing and completion. Additional focused tests should cover builder validation, submitted/processing/completed transitions from `ReencryptionInfoProto`, cancellation behavior, checkpoint clearing on completion, and failover/replay semantics.
