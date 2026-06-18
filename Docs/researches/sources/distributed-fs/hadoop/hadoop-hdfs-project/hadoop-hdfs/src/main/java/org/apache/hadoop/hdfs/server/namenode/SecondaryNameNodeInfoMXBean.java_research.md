# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SecondaryNameNodeInfoMXBean.java

## Purpose

`SecondaryNameNodeInfoMXBean.java` defines the JMX management contract exposed by `SecondaryNameNode`. The source was read as a complete 65-line file.

## Important APIs, Types, and Functions

The interface extends `VersionInfoMXBean` and declares `getHostAndPort`, `isSecurityEnabled`, `getStartTime`, `getLastCheckpointTime`, `getLastCheckpointDeltaMs`, `getCheckpointDirectories`, and `getCheckpointEditlogDirectories`.

## Control Flow

There is no executable flow. `SecondaryNameNode` implements these getters and registers itself through Hadoop metrics/JMX utilities during initialization.

## State and Persistence Behavior

The interface owns no state. It exposes runtime state from the secondary daemon and configured checkpoint directories that point to persistent local fsimage/edit storage.

## Dependencies and Integration Points

It uses Hadoop classification annotations and inherits build/version methods from `VersionInfoMXBean`. It integrates with JMX object registration in `SecondaryNameNode.initialize`.

## Risks and Edge Cases

Because this is an operational interface, changes to method names or return types can break monitoring tools that rely on JMX naming conventions. Null or empty directory arrays would indicate bad initialization rather than an interface issue.

## Test Signals

Tests should register a `SecondaryNameNode` MBean and verify that values reflect configured directories, start time, security state, version fields, and checkpoint timestamp/delta before and after a checkpoint.
