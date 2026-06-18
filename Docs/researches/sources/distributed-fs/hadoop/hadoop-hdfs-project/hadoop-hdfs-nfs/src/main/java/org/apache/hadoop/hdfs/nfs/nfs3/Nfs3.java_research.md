<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3.java

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3.java` starts and stops the HDFS NFSv3 gateway and its companion mount daemon. The source was read as a complete 81-line file for this report.

## Important APIs, Types, and Functions

`Nfs3` extends `Nfs3Base`, stores `Mountd mountd`, exposes constructors, `getMountd`, `startServiceInternal`, static `startService`, `stop`, and `main`.

## Control Flow

Construction creates the NFSv3 RPC program through `RpcProgramNfs3.createRpcProgramNfs3` and constructs `Mountd` with the same registration socket and port policy. `startService` logs startup, reads insecure-port policy from configuration, starts mountd, then starts the NFS server. `stop` stops the NFS server first, then mountd.

## State and Persistence Behavior

Runtime state is the pair of RPC servers and their sockets, registrations, metrics, caches, and write managers. No durable state is owned here; HDFS mutations occur in the RPC program.

## Dependencies and Integration Points

It integrates `Nfs3Base`, `RpcProgramNfs3`, `Mountd`, `NfsConfiguration`, startup logging, and `NfsConfigKeys.DFS_NFS_PORT_MONITORING_DISABLED_KEY`.

## Risks and Edge Cases

Lifecycle ordering matters: clients need mountd available for handles before NFS operations. Shared registration socket handling and insecure-port policy must remain consistent between mountd and NFS.

## Test Signals

Gateway startup/shutdown tests, `TestExportsTable`, `TestNfs3HttpServer`, and tests that inspect `getMountd()` validate this wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3.java -->
