<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlockMovementAttemptFinished.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlockMovementAttemptFinished.java

Purpose: immutable value object describing the result of one SPS block movement attempt.

Important APIs and types: constructor captures `Block`, source `DatanodeInfo`, target `DatanodeInfo`, target `StorageType`, and `BlockMovementStatus`. Getters expose block, target datanode, target type, and status; source is included only in `toString`.

Control flow, state, and persistence: no behavior beyond construction and formatting. State is final and not persisted by this class.

Dependencies and integration points: used as the result type for `CompletionService<BlockMovementAttemptFinished>` consumed by `BlockStorageMovementTracker` and passed to `BlocksMovementsStatusHandler`.

Risks and test signals: the missing source getter may matter to consumers that need source details after completion. Tests are simple construction/getter/toString checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlockMovementAttemptFinished.java -->
