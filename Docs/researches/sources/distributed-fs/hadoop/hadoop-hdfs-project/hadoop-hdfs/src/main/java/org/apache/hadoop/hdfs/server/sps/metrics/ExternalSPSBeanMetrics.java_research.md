<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/metrics/ExternalSPSBeanMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/metrics/ExternalSPSBeanMetrics.java

## Purpose

`ExternalSPSBeanMetrics` exposes external Storage Policy Satisfier runtime counters through a JMX MBean.

## Important APIs and types

The class implements `ExternalSPSMXBean`. It registers a `StandardMBean` under `ExternalSPS/ExternalSPS`, stores the returned `ObjectName`, and delegates metrics to `StoragePolicySatisfier`. Public metrics are processing queue size, movement-finished block count, and attempted item count. Visible-for-testing helpers mutate SPS queues/sets to exercise metric changes.

## Control flow

Construction registers the MBean and throws a runtime exception on non-compliant MBean setup. `close()` unregisters the MBean and nulls the object name. Metric getters read current SPS queue/monitor state on demand.

## State and persistence behavior

State is runtime-only: the MBean registration and reference to SPS. No persistent data is written.

## Dependencies and integration points

It depends on `MBeans`, JMX `StandardMBean`, `ExternalSPSMXBean`, `StoragePolicySatisfier`, `ItemInfo`, and `Block`. It is initialized by `ExternalSPSContext`.

## Risks and test signals

Risks include duplicate MBean registration, failure to unregister on shutdown, direct test mutation of internal SPS collections, and null SPS references. Tests should cover registration, close idempotence, getter values before/after queue changes, and ExternalSPS process shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/metrics/ExternalSPSBeanMetrics.java -->
