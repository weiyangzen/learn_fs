# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/ActiveState.java

## Purpose

`ActiveState.java` implements the active HA state for a NameNode. The source was read as a complete 76-line file.

## Important APIs, Types, and Functions

The class extends `HAState` with `HAServiceState.ACTIVE`. It implements `checkOperation`, `shouldPopulateReplQueues`, `setState`, `enterState`, and `exitState`.

## Control Flow

Active state allows all operation categories. It permits transition only to `NameNode.STANDBY_STATE` through `setStateInternal`. Entering active calls `HAContext.startActiveServices`; exiting calls `HAContext.stopActiveServices`; IO failures are wrapped as `ServiceFailedException`.

## State and Persistence Behavior

The class itself is stateless aside from inherited transition time. Entering active starts services that write edits, serve clients, and populate replication queues.

## Dependencies and Integration Points

It integrates with `HAState`, `HAContext`, `NameNode.ACTIVE_STATE/STANDBY_STATE`, Hadoop HA service states, and NameNode operation categories.

## Risks and Edge Cases

An active transition must fully start active services or fail cleanly. Allowing all operations means fencing and state-transition correctness must be handled before reaching this state.

## Test Signals

Tests should cover allowed operations, replication queue population, active-to-standby transition, rejection of unsupported transitions, and service start/stop exception wrapping.
