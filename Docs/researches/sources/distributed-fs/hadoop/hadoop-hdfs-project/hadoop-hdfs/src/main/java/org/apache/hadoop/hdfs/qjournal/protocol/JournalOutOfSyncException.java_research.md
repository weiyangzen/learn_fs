<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/JournalOutOfSyncException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/JournalOutOfSyncException.java

Purpose: Signals that a JournalNode's local write state no longer matches the active writer's expected segment or transaction sequence.

Important APIs/types/functions: Public constructor accepting a message; subclass of `IOException`.

Control flow: Thrown by server-side `Journal.checkSync` and by client-side `IPCLoggerChannel.throwIfOutOfSync`. A failed write causes the channel to stop useful writes until the next segment roll.

State and persistence behavior: The exception itself has no state. It protects durable edit-log invariants such as contiguous txids, correct segment id, and no overwriting finalized segments.

Dependencies/integration: Propagates through qjournal RPCs; quorum logic can tolerate it from minority loggers while still committing to a majority.

Risks: Frequent out-of-sync failures indicate a logger is lagging or an ordering invariant broke. Recovery depends on subsequent log roll or segment recovery to restore participation.

Test signals: Tests should verify txid mismatch, segment mismatch, missing segment, and client out-of-sync heartbeat paths all surface this exception and preserve quorum behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/protocol/JournalOutOfSyncException.java -->
