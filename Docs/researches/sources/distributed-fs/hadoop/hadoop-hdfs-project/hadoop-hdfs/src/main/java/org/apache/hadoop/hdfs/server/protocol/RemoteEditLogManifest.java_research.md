<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/RemoteEditLogManifest.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/RemoteEditLogManifest.java

## Purpose

`RemoteEditLogManifest` is a list of remote edit-log segments plus the committed transaction ID known by the provider.

## Important APIs and types

Fields are `List<RemoteEditLog> logs` and `committedTxnId`. Constructors accept a log list and optional committed txid. `checkState()` enforces non-null logs and non-overlapping sorted order. `getLogs()` returns an unmodifiable view.

## Control flow

`NamenodeProtocol.getEditLogManifest` returns this object to checkpoint or tailing clients. The constructor validates segment order immediately so callers do not fetch overlapping ranges.

## State and persistence behavior

The object is transient and represents persistent edit-log files. It does not copy the input list, so external mutation of the original list after construction can bypass validation despite `getLogs()` being unmodifiable.

## Dependencies and integration points

It depends on `RemoteEditLog`, `Preconditions`, `Joiner`, and `HdfsServerConstants`. It integrates with checkpointing, backup nodes, and edit-log fetchers.

## Risks and test signals

Risks include unsorted lists, overlapping ranges, in-progress logs with invalid end txids, and post-construction mutation of the backing list. Tests should cover overlap rejection, gap allowance, unmodifiable getter behavior, committed txid formatting, and defensive-copy expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/RemoteEditLogManifest.java -->
