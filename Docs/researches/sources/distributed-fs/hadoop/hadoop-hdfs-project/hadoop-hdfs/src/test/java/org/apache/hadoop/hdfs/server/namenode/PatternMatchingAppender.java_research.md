<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/PatternMatchingAppender.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/PatternMatchingAppender.java

Purpose: simple Log4j test appender that records whether a log message matching a fixed metric pattern was seen.

Important APIs/types/functions: extends `AppenderSkeleton`; constructor compiles `^.*FakeMetric.*$`; `append(LoggingEvent)` checks event messages; `isMatched()` returns a volatile boolean; `close()` and `requiresLayout()` satisfy appender contract.

Control flow: when attached to a logger, each `LoggingEvent` message is converted to string and matched. The first match flips `matched` to true and it remains true for the appender lifetime.

State and persistence: in-memory only: compiled `Pattern` and volatile `matched`. No log storage or layout handling.

Dependencies and integration points: integrates with legacy Log4j appenders in NameNode tests that need to assert metric log emission.

Risks and test signals: null messages would throw through `toString()`, and the pattern is hard-coded to `FakeMetric`. Signal is `isMatched()` becoming true after expected logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/PatternMatchingAppender.java -->
