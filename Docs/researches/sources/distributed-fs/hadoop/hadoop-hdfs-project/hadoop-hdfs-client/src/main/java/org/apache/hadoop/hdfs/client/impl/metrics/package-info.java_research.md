# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/metrics/package-info.java

## Purpose
This package-info documents the `org.apache.hadoop.hdfs.client.impl.metrics` package as support for tracking Block Reader Local latencies.

## Important APIs, types, and functions
It declares package annotations `@InterfaceAudience.Private` and `@InterfaceStability.Evolving`, indicating internal HDFS client metrics APIs that may still change.

## Control flow
There is no executable control flow.

## State and persistence behavior
There is no runtime state or persistence.

## Dependencies and integration points
It imports Hadoop classification annotations and applies them to the metrics package containing `BlockReaderIoProvider` and `BlockReaderLocalMetrics`.

## Risks and test signals
Test signal is limited to API classification and package documentation. Build or javadoc checks should ensure annotations resolve.
