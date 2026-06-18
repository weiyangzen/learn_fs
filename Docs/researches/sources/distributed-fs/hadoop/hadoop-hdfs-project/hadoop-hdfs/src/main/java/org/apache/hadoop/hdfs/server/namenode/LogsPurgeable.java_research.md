<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/LogsPurgeable.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/LogsPurgeable.java

## Purpose

`LogsPurgeable` abstracts edit-log stores that can purge old transactions and expose input streams for replay.

## Important APIs and Types

`purgeLogsOlderThan` removes edit logs below a minimum transaction id. `selectInputStreams` returns streams starting with the segment containing `fromTxId` and continuing forward, with flags for in-progress streams and durable transaction bounding.

## Control Flow, State, and Persistence

The interface does not implement behavior; concrete journal managers define persistence semantics. The `onlyDurableTxns` parameter is important for QJM committed txids and file journals' largest written txids.

## Dependencies and Integration Points

It is extended by `JournalManager` and consumed by `JournalSet`, `FSEditLog`, checkpointers, and edit-log loading code.

## Risks and Test Signals

Risks include purging needed recovery logs, returning streams with gaps, and mishandling in-progress or non-durable tails. Tests should cover purge boundaries, stream selection from the middle of a segment, in-progress inclusion/exclusion, durable truncation, and behavior when storage is inaccessible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/LogsPurgeable.java -->
