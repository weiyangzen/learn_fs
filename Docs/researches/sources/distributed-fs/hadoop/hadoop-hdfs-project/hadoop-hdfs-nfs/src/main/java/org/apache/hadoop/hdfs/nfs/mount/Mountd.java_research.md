<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/mount/Mountd.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/mount/Mountd.java

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/mount/Mountd.java` is the mount daemon entry point for the HDFS NFS gateway. The source was read as a complete 45-line file for this report.

## Important APIs, Types, and Functions

`Mountd` extends `MountdBase`. Its constructor builds a `RpcProgramMountd` with `NfsConfiguration`, optional registration socket, and insecure-port policy. `main` creates a default `NfsConfiguration`, constructs `Mountd`, and starts it with registration enabled.

## Control Flow

Standalone startup is simple: create config, create RPC program through the constructor, and call `start(true)`. In normal NFS gateway startup, `Nfs3` owns a `Mountd` instance and starts it before the NFSv3 RPC server.

## State and Persistence Behavior

The daemon owns process-lifetime RPC server state through `MountdBase`. Mount entries and export mappings live inside `RpcProgramMountd`, not in this wrapper.

## Dependencies and Integration Points

It integrates the Hadoop NFS mount base class, `RpcProgramMountd`, UDP registration socket handling, and `NfsConfiguration` defaults.

## Risks and Edge Cases

Standalone `main` passes `allowInsecurePorts=true`, which differs from configurable `Nfs3.startService` policy. Constructor failures propagate as `IOException`.

## Test Signals

`TestMountd`, export table tests, and `Nfs3` startup tests verify daemon construction and mountd/NFS lifecycle ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/mount/Mountd.java -->
