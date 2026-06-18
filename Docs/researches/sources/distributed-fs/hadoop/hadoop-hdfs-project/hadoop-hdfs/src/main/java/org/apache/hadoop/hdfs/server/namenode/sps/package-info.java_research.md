<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/package-info.java

## Purpose

This package descriptor marks `org.apache.hadoop.hdfs.server.namenode.sps` as the private, unstable NameNode package that implements storage-policy satisfaction for paths.

## Important APIs and types

It applies `@InterfaceAudience.Private` and `@InterfaceStability.Unstable` to the package. The substantive APIs in the package include `StoragePolicySatisfier`, `StoragePolicySatisfyManager`, SPS queues, context interfaces, and movement listeners.

## Control flow

There is no executable control flow. The file documents package intent and sets classification annotations consumed by developers and generated docs.

## State and persistence behavior

No runtime or persistent state is defined here.

## Dependencies and integration points

The descriptor depends only on Hadoop classification annotations. It frames the SPS package as internal to HDFS NameNode/external SPS implementation rather than a stable public API.

## Risks and edge cases

The unstable/private classification gives maintainers room to change the package, but downstream users that depend on internals can break. The package summary is intentionally brief and does not document the external SPS process boundary.

## Test signals

No direct tests are expected. Indirect signal comes from compiling package annotations and from SPS integration tests that exercise classes in this package.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/package-info.java -->
