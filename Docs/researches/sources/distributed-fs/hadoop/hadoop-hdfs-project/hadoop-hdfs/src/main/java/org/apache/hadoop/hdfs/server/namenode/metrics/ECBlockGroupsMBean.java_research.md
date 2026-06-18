# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/metrics/ECBlockGroupsMBean.java

## Purpose

`ECBlockGroupsMBean.java` defines JMX metrics for erasure-coded block groups in `FSNamesystem`. The source was read as a complete 69-line file.

## Important APIs, Types, and Functions

The interface declares getters for low redundancy, corrupt, missing, bytes in future block groups, pending deletion EC blocks, total EC block groups, and enabled EC policies.

## Control Flow

There is no implementation flow. `FSNamesystem` or related metrics providers implement the getters.

## State and Persistence Behavior

The interface owns no state. Values reflect in-memory block-manager state derived from namespace and block reports.

## Dependencies and Integration Points

It complements `FSNamesystemMBean`, `ReplicatedBlocksMBean`, and `NameNodeMetrics` by splitting EC-specific block health from replicated block health.

## Risks and Edge Cases

Metric names become JMX attributes, so signature changes affect operators. Counts must be kept semantically distinct from replicated block counts.

## Test Signals

Tests should verify JMX exposure and values for EC policy enablement, low redundancy, corrupt, missing, future, pending deletion, and total EC block groups.
