<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3Utils.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3Utils.java

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3Utils.java` provides NFSv3 gateway utility methods for inode paths, attribute conversion, weak-cache consistency data, socket writes, access-right calculation, byte conversions, elapsed time, namenode IDs, and export URI resolution. The source was read as a complete 273-line file for this report.

## Important APIs, Types, and Functions

Important APIs include `getFileIdPath`, `getFileStatus`, `getNfs3FileAttrFromFileStatus`, `getFileAttr`, `getDirSize`, `getWccAttr`, `createWccData`, `writeChannel`, `writeChannelCommit`, `getAccessRights`, `getAccessRightsForUserGroup`, `bytesToLong`, `longToByte`, `getElapsedTime`, `getNamenodeId`, and `getResolvedURI`.

## Control Flow

Most helpers are straight conversions. Attribute conversion maps HDFS status into NFS file type, nlink, mode, uid/gid, size, file ID, and times. Access checks choose owner, group/auxiliary group, or other permission bits. `getResolvedURI` resolves viewfs mount points or HDFS export paths and rejects non-HDFS backing filesystems.

## State and Persistence Behavior

The class is stateless. It reads HDFS metadata through `DFSClient` and writes network responses to Netty channels but does not persist durable data itself.

## Dependencies and Integration Points

It integrates HDFS protocol status, Hadoop NFS attribute/response types, Netty channels, ONC/RPC XDR, ID mapping, viewfs, and DFS namenode address resolution.

## Risks and Edge Cases

Directory size is synthetic, file IDs are 64-bit despite old client concerns, access-right mapping must match NFSv3 semantics, byte conversion assumes exactly eight bytes, and viewfs export resolution chooses the first matching mount prefix.

## Test Signals

`TestNfs3Utils`, `TestViewfsWithNfs3`, `TestRpcProgramNfs3`, readdir/read/write tests, and namenode-ID/export resolution tests cover this utility surface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3Utils.java -->
