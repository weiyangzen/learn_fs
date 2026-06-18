<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlocksMovementsStatusHandler.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlocksMovementsStatusHandler.java

Purpose: callback interface for collecting or processing completed SPS block movement attempts.

Important APIs and types: single method `handle(BlockMovementAttemptFinished moveAttemptFinishedBlk)`.

Control flow, state, and persistence: no implementation; state and persistence are owned by implementors.

Dependencies and integration points: consumed by `BlockStorageMovementTracker`, implemented by SPS coordination code that needs movement completion events.

Risks and test signals: implementors need to be thread-safe because callbacks happen on the tracker thread. Tests belong with implementations and should validate failure/status propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlocksMovementsStatusHandler.java -->
