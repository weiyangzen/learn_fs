## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ClusterStorageCapacityExceededException.java

Purpose: evolving public `IOException` used by HDFS and related clients to signal cluster-wide storage capacity exhaustion.

Important APIs and types: standard no-arg, message, message-plus-cause, and cause constructors.

Control flow: exception type only.

State and persistence behavior: standard exception message/cause state; no persistence.

Dependencies and integration points: raised by storage allocation/write paths and observed by MapReduce/HDFS clients for capacity-specific handling.

Risks: callers catching generic `IOException` may not distinguish quota/capacity failures. No extra structured fields identify cluster, storage type, or remaining capacity.

Test signals: verify constructor message/cause combinations and propagation through write/allocation failure paths that need capacity-specific behavior.
