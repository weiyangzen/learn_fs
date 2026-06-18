<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReplicaWaitingToBeRecovered.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReplicaWaitingToBeRecovered.java

## Purpose

`ReplicaWaitingToBeRecovered` represents a local RWR replica, typically loaded from an `rbw` directory after a DataNode restart. It is persisted data that is not visible to readers and does not participate in pipeline recovery until lease recovery decides its fate.

## Important APIs, Types, And Functions

- Constructors accept explicit block id/length/generation stamp, a `Block`, or another RWR replica.
- `getState()` returns `ReplicaState.RWR`.
- `getVisibleLength()` returns `-1` to indicate no bytes are visible.
- `getBytesOnDisk()` returns `getNumBytes()`.
- Recovery wrapper APIs `getOriginalReplica`, `getRecoveryID`, `setRecoveryID`, and `createInfo` throw `UnsupportedOperationException`.

## Control Flow

Dataset startup or recovery logic creates this state for interrupted writes. Normal reads should treat it as invisible. To perform actual block recovery, higher-level code wraps a valid RWR in `ReplicaUnderRecovery` rather than using recovery APIs directly on this class.

## State And Persistence

The persistent state is local block and metadata files inherited from `LocalReplica`. The class adds no new fields; it only changes reported state and visibility semantics.

## Dependencies And Integration Points

It integrates with restart recovery, `ReplicaBuilder.buildRWR()`, and lease recovery transitions. It depends on `Block`, `FsVolumeSpi`, `ReplicaState`, and `ReplicaRecoveryInfo` for unsupported method signatures.

## Risks And Edge Cases

`getVisibleLength()` returning `-1` is a sentinel and must not be treated as an actual byte count. Calling recovery-id methods directly is a misuse. Outdated RWR replicas can remain if the client continues writing elsewhere.

## Test Signals

Tests should verify state, invisible length, bytes-on-disk behavior, copy construction, unsupported recovery methods, and transitions from restarted RBW files into RWR and then RUR during lease recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReplicaWaitingToBeRecovered.java -->
