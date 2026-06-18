<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/package-info.java

## Purpose
Documents `org.apache.hadoop.ipc` as the package for network client/server helpers and Hadoop RPC APIs, with limited-private evolving compatibility expectations.

## Important APIs, Types, And Functions
- Package annotations: limited private to HBase, HDFS, MapReduce, YARN, Hive, and Ozone; stability evolving.
- Notes that changes to `RPC` and `RpcEngine` signatures can break external ASF projects, especially with shaded/unshaded protobuf variants.

## Control Flow
No executable control flow.

## State And Persistence
No runtime state or persistence.

## Dependencies And Integration Points
Applies compatibility guidance to the whole IPC package, including server, client, protocol, scheduler, and protobuf integration classes.

## Risks And Edge Cases
The package is not fully public but has broad ecosystem consumers, so apparently internal signature changes can be breaking.

## Test Signals
Cross-project compatibility, Hadoop module compilation, and RPC integration suites provide signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/package-info.java -->
