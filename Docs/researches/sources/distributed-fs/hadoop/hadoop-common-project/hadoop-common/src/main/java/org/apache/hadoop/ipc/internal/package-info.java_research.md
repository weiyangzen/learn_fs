<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/internal/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/internal/package-info.java

## Purpose
Declares `org.apache.hadoop.ipc.internal` as internal Hadoop IPC implementation space, limited to selected Hadoop modules and unstable.

## Important APIs, Types, And Functions
- Package annotations: `@InterfaceAudience.LimitedPrivate({"HDFS", "MapReduce", "YARN"})` and `@InterfaceStability.Unstable`.

## Control Flow
No executable control flow.

## State And Persistence
No runtime state or persistence.

## Dependencies And Integration Points
Sets API audience expectations for classes such as `ShadedProtobufHelper`.

## Risks And Edge Cases
Downstream users should not rely on stable signatures. Changes can still affect Hadoop submodules listed in the limited-private audience.

## Test Signals
No direct runtime tests; compatibility and compilation of dependent Hadoop modules are the signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/internal/package-info.java -->
