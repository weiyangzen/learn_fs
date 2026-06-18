# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemWithTruncate.java

## Purpose

`TestViewFileSystemWithTruncate` verifies that `ViewFileSystem` advertises and forwards file truncation to an HDFS mount target. It checks both `hasPathCapability` and the final truncated length.

## Important APIs, types, and functions

Important APIs include `FileSystem.truncate`, `hasPathCapability`, `CommonPathCapabilities.FS_TRUNCATE`, `MiniDFSCluster`, `MiniDFSNNTopology.simpleFederatedTopology(2)`, `GenericTestUtils.waitFor`, `FileSystem.isFileClosed`, `FSDataOutputStream`, and `ConfigUtil.addLink`.

## Control flow, state, and persistence

Setup starts a federated cluster, mounts `/mountOnNn1` to an HDFS test root, writes a file via ViewFS, asserts truncate capability, calls `truncate(filePath, 10)`, and if the operation is asynchronous waits until the raw HDFS file is closed. It then asserts ViewFS reports length 10. State is a temporary HDFS file under the test root.

## Dependencies and integration points

The test integrates ViewFS path resolution with HDFS truncate semantics, capability reporting, asynchronous block recovery completion, and raw HDFS status visibility.

## Risks and test signals

Risks include ViewFS not exposing `FS_TRUNCATE`, returning before HDFS completes without a usable wait path, wrong raw target path assumptions, or stale file length after truncate. Passing requires capability true and exact final length.
