<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/UnexpectedReplicaStateException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/UnexpectedReplicaStateException.java

## Purpose

`UnexpectedReplicaStateException` is a checked exception used when a block replica is not in the state required by a DataNode operation.

## Important APIs, Types, And Functions

- Extends `IOException`.
- Provides a no-argument constructor, a message constructor, and a constructor that formats an `ExtendedBlock` plus expected `ReplicaState`.
- Carries a fixed `serialVersionUID`.

## Control Flow

The class has no internal control flow. It is thrown by replica-management callers when state validation fails before an operation such as append, recovery, finalization, or deletion.

## State And Persistence

Only inherited exception state is stored. The block and expected state constructor embeds diagnostics into the message rather than retaining structured fields.

## Dependencies And Integration Points

It depends on `ExtendedBlock` and `ReplicaState`, and belongs to the DataNode replica error vocabulary alongside existence and I/O exceptions.

## Risks And Edge Cases

Because actual state is not included by the typed constructor, callers often need to add richer custom messages if the actual state matters. Catching it as generic `IOException` can obscure state-machine bugs.

## Test Signals

Caller tests should assert invalid state transitions throw this exception, include useful block/state diagnostics, and leave replica maps and files unchanged after failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/UnexpectedReplicaStateException.java -->
