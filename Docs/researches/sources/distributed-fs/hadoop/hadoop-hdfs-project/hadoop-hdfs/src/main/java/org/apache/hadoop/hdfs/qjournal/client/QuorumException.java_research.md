<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/QuorumException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/QuorumException.java

Purpose: IOException used when a quorum operation receives too many failures to satisfy the required success threshold.

Important APIs/types/functions: Static factory `create(simpleMsg, successes, exceptions)` builds a diagnostic message including successes and per-logger failures.

Control flow: Callers pass accumulated result maps from `QuorumCall`; runtime exceptions are stringified with stack traces, checked exceptions prefer localized messages, and null successes are rendered explicitly.

State and persistence behavior: No persistent state. The created message is the primary state and is intended for operator/test diagnostics.

Dependencies/integration: Thrown by `QuorumCall.rethrowException` and `AsyncLoggerSet.waitForWriteQuorum`; uses Guava `Joiner`, Hadoop `StringUtils`, and `Preconditions`.

Risks: Message order follows map iteration order, which may be nondeterministic. Checked exceptions without useful messages still fall back to stack stringification.

Test signals: Verify empty-exception rejection, success and failure message formatting, runtime stack inclusion, checked-exception message handling, and stable behavior with null success values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/QuorumException.java -->
