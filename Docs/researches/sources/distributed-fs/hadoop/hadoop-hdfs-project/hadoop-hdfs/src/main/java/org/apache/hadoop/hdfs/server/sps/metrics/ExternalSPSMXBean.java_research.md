<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/metrics/ExternalSPSMXBean.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/metrics/ExternalSPSMXBean.java

## Purpose

`ExternalSPSMXBean` is the JMX management interface for external Storage Policy Satisfier metrics.

## Important APIs and types

The stable private interface declares `getProcessingQueueSize()`, `getMovementFinishedBlocksCount()`, and `getAttemptedItemsCount()`.

## Control flow

JMX clients call these methods through the registered `ExternalSPSBeanMetrics` MBean. No implementation lives in the interface.

## State and persistence behavior

The interface has no state. Implementations read external SPS runtime state.

## Dependencies and integration points

It is consumed by `ExternalSPSBeanMetrics` and Hadoop's JMX/MBeans helper.

## Risks and test signals

Because this is a management interface, method renames or signature changes break JMX clients. Tests should cover MBean compliance, exported attribute names, and metric values under representative SPS queue/attempt states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/metrics/ExternalSPSMXBean.java -->
