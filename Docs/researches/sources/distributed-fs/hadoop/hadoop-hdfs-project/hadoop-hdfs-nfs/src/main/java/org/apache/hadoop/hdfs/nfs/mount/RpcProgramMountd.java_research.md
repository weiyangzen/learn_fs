<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/mount/RpcProgramMountd.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/mount/RpcProgramMountd.java

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/mount/RpcProgramMountd.java` implements the ONC/RPC mount protocol program used by the HDFS NFS gateway. The source was read as a complete 283-line file for this report.

## Important APIs, Types, and Functions

`RpcProgramMountd` extends `RpcProgram` and implements `MountInterface`. Key APIs are constructor, `addExports`, `nullOp`, `mnt`, `dump`, `umnt`, `umntall`, `handleInternal`, `isIdempotent`, and testing accessor `getExports`. It defines mountd program/version constants and stores synchronized `mounts`, export path-to-URI map, `NfsConfiguration`, and `NfsExports` host matcher.

## Control Flow

Construction registers the RPC program, resolves configured export paths through `Nfs3Utils.getResolvedURI`, initializes host access matching, configures UGI, and logs in from keytab when configured. `handleInternal` decodes the RPC procedure and dispatches to mount operations. `MNT` enforces host exports and port monitoring, resolves a DFS file handle from the export directory file ID and namenode ID, records the mount entry, and writes an XDR response.

## State and Persistence Behavior

Export mappings are built at startup and kept in memory. Current mounts are an in-memory synchronized list used by `DUMP`, `UMNT`, and `UMNTALL`; they are not durable. HDFS file IDs and namenode IDs are encoded into returned file handles.

## Dependencies and Integration Points

It integrates Netty, ONC/RPC XDR, Hadoop NFS mount response types, HDFS `DFSClient`, `NfsExports`, Kerberos login, and `Nfs3Utils` URI/namenode helpers.

## Risks and Edge Cases

Access-control errors must not leak handles. Export path matching is exact, hostnames are recorded from reverse DNS, `HashMap` export iteration order is not stable, and each mount opens a short-lived `DFSClient` without explicit close in this method.

## Test Signals

`TestExportsTable`, `TestViewfsWithNfs3`, mount access tests, port-monitoring tests, and RPC procedure dispatch tests cover this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/mount/RpcProgramMountd.java -->
