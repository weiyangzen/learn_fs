# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileCreationEmpty.java

## Purpose

`TestFileCreationEmpty.java` checks that lease expiry over multiple empty files does not throw `ConcurrentModificationException`. The complete 84-line file was read.

## Important APIs, Types, and Functions

Key APIs are `Thread.setDefaultUncaughtExceptionHandler`, `ConcurrentModificationException`, `LeaseManager.LOG`, `MiniDFSCluster`, `cluster.setLeasePeriod`, and `TestFileCreation.createFile`.

## Control Flow

The test installs a temporary default uncaught exception handler that records any `ConcurrentModificationException`. It starts a three-DataNode cluster, creates three empty files (`/foo`, `/foo2`, `/foo3`) through `TestFileCreation.createFile` without closing the returned streams, sets both soft and hard lease periods to one second, waits five lease periods, and asserts the flag was not set. The original exception handler is restored in `finally`.

## State and Persistence Behavior

State is in-memory lease manager state for three zero-length under-construction files. There is no restart, but lease expiry mutates the lease collection while scanning it.

## Dependencies and Integration Points

The test targets NameNode `LeaseManager` empty-file release behavior and MiniDFSCluster lease-period control.

## Risks and Edge Cases

Risks include global uncaught exception handler leakage, lease scans modifying collections during iteration, and false negatives if lease recovery does not run during the sleep window.

## Test Signals

Signals are absence of uncaught `ConcurrentModificationException` after lease expiry, handler restoration, and clean cluster shutdown.
