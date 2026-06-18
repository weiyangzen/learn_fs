<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/AsyncLoggerSet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/AsyncLoggerSet.java

Purpose: Immutable wrapper around all `AsyncLogger` instances for one quorum journal. It fans out operations and provides majority-based wait semantics for write quorum operations.

Important APIs/types/functions: `setEpoch`, `getEpoch`, `setCommittedTxId`, `waitForWriteQuorum`, `getMajoritySize`, `getMajorityString`, `appendReport`, and boilerplate quorum-call factories for all `AsyncLogger` methods.

Control flow: Construction copies the logger list. Epoch can be established only once, then pushed to every logger. Write quorum waits return when all loggers answer, a majority succeeds, or too many failures make quorum impossible; after waiting, insufficient successes are converted to `QuorumException`. Fan-out methods build a map of logger to future and wrap it with `QuorumCall`.

State and persistence behavior: Tracks only `myEpoch`; persistent effects are on remote JournalNodes. `purgeLogsOlderThan` intentionally fire-and-forgets because failure to purge is not correctness critical.

Dependencies/integration: Used by `QuorumJournalManager` and `QuorumOutputStream`; depends on `QuorumCall`, `QuorumException`, and protobuf response types for recovery, manifests, and upgrades.

Risks: Majority math assumes an odd number of loggers for best availability; even counts are supported but reduce failure tolerance. Epoch establishment is one-shot, so manager reuse across writer epochs is not supported. Late future completions can mutate a `QuorumCall` after wait returns, though returned result maps are copied.

Test signals: Unit tests should cover majority thresholds for 1/3/5 nodes, timeout and interruption translation to `IOException`, too-many-failure exception formatting, one-shot epoch validation, and all fan-out wrappers creating one future per logger.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/AsyncLoggerSet.java -->
