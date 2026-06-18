<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/LeaseExpiredException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/LeaseExpiredException.java

## Purpose

`LeaseExpiredException` indicates that the lease used to create or write a file has expired and can no longer authorize the requested operation.

## Important APIs and Types

It is an evolving private `IOException` subclass with a single message constructor.

## Control Flow, State, and Persistence

The exception has no extra state. It participates in file create/write/append/recovery control flow by distinguishing lease expiry from generic I/O failure.

## Dependencies and Integration Points

It integrates with lease checking in NameNode write paths, `LeaseManager`, client error propagation, and retry/recovery behavior.

## Risks and Test Signals

Risks are mainly caller handling. Tests should verify expired hard-limit leases produce this exception where expected, active leases do not, and clients transition to lease recovery or fail with useful diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/LeaseExpiredException.java -->
