<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/LoggerTooFarBehindException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/LoggerTooFarBehindException.java

Purpose: Marker `IOException` used when an `IPCLoggerChannel` has too many pending edit bytes and should be treated as unavailable for the current write.

Important APIs/types/functions: Empty package-private subclass of `IOException` with a stable `serialVersionUID`.

Control flow: `IPCLoggerChannel.reserveQueueSpace` throws this when queue limits would be exceeded while existing bytes are pending; `sendEdits` converts it to an immediate failed future so quorum handling can proceed.

State and persistence behavior: No state or persistence. It protects client memory by stopping further queuing for a slow logger.

Dependencies/integration: Consumed by `IPCLoggerChannel` and indirectly by `AsyncLoggerSet.waitForWriteQuorum`.

Risks: The exception carries no message, so diagnosis depends on the warning logged at the throw site. Treating the logger as failed relies on enough remaining loggers for quorum.

Test signals: Queue-limit tests should assert failed future type, warning path, and successful quorum writes with one lagging logger.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/LoggerTooFarBehindException.java -->
