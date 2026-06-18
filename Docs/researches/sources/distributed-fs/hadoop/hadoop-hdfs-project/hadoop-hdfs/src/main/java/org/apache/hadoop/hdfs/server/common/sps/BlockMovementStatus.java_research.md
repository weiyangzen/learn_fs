<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlockMovementStatus.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlockMovementStatus.java

Purpose: enum of SPS DataNode block-storage movement outcomes.

Important APIs and types: two statuses are defined: `DN_BLK_STORAGE_MOVEMENT_SUCCESS(0)` and `DN_BLK_STORAGE_MOVEMENT_FAILURE(-1)`. Package-private `getStatusCode` returns the numeric code.

Control flow, state, and persistence: enum constants are static immutable values. No persistence is performed here.

Dependencies and integration points: used by `BlockDispatcher` and movement result objects; TODO notes future finer-grained failure categories.

Risks and test signals: failure detail is coarse, so diagnostics must come from logs or higher-level exceptions. Tests should confirm code values if protocol serialization or metrics depend on them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlockMovementStatus.java -->
