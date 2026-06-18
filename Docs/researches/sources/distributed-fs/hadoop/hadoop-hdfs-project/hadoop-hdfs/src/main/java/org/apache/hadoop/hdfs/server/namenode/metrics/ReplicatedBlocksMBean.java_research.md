# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/metrics/ReplicatedBlocksMBean.java

## Purpose

`ReplicatedBlocksMBean.java` defines JMX metrics for contiguous replicated blocks in `FSNamesystem`. The source was read as a complete 73-line file.

## Important APIs, Types, and Functions

The interface declares getters for low redundancy, corrupt, missing, missing replication-one blocks, badly distributed blocks, bytes in future blocks, pending deletion replicated blocks, and total replicated blocks.

## Control Flow

There is no implementation flow. Implementers compute values from block-manager state.

## State and Persistence Behavior

The interface owns no state. Values are live views over block metadata and DataNode reports.

## Dependencies and Integration Points

It complements `ECBlockGroupsMBean` and `FSNamesystemMBean`, separating replicated block health from erasure-coded block group health.

## Risks and Edge Cases

Metric names are externally visible JMX attributes. Misclassifying EC block groups as replicated blocks, or vice versa, would distort operational health dashboards.

## Test Signals

Tests should verify JMX exposure and counts for replicated low redundancy, corrupt, missing, replication-one missing, badly distributed, future, pending deletion, and total block states.
