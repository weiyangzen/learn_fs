<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/FencedException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/FencedException.java

## Purpose

`FencedException` indicates that a previous writer or resource user attempted to use a shared journal/resource after another writer fenced it.

## Important APIs and types

The class extends `IOException`, declares `serialVersionUID`, and exposes a single string-message constructor.

## Control flow

Journal methods such as `journal`, `startLogSegment`, and `fence` document this exception. Implementations throw it when the caller's epoch or writer identity is no longer valid.

## State and persistence behavior

The exception carries only a message. Fencing epochs and writer state are maintained by the journal implementation.

## Dependencies and integration points

It integrates with `JournalProtocol`, HA edit-log replication, backup-node journaling, and RPC retry/failover logic that must distinguish fenced writers from transient IO failures.

## Risks and test signals

Risks are callers retrying a fenced operation as if it were transient or implementations throwing generic IO errors instead. Tests should verify stale epochs receive `FencedException` and active writers stop after being fenced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/FencedException.java -->
