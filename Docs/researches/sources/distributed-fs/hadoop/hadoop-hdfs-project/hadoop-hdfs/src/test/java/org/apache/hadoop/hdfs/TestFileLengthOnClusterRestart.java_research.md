# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileLengthOnClusterRestart.java

## Purpose

`TestFileLengthOnClusterRestart.java` verifies visible file length after `hsync` and NameNode restart, and verifies safe-mode behavior when DataNodes have not registered. The complete 99-line file was read.

## Important APIs, Types, and Functions

Key APIs are `FSDataOutputStream.hsync`, `HdfsDataInputStream.getVisibleLength`, `MiniDFSCluster.restartNameNode`, `cluster.shutdownDataNodes`, `DistributedFileSystem.isInSafeMode`, and `DFS_BLOCK_SIZE_KEY`.

## Control Flow

The test configures 512-byte blocks, starts a two-DataNode cluster, creates `/tmp/TestFileLengthOnClusterRestart/test`, writes 1030 bytes, and calls `hsync`. It restarts the NameNode with DataNodes available, waits active, opens the file, and asserts `getVisibleLength()` equals 1030. It then shuts down all DataNodes, restarts only the NameNode without formatting, loops until `dfs.isInSafeMode()` reports true, and verifies opening the path fails with an IOException whose message contains "Name node is in safe mode".

## State and Persistence Behavior

The persistent state is the hsynced file length in NameNode metadata and block reports. The second phase intentionally lacks DataNode registrations, so the NameNode remains in safe mode even though namespace metadata exists.

## Dependencies and Integration Points

It integrates DFSOutputStream hsync visibility, HDFS client visible-length reporting, NameNode restart, safe-mode detection, and DataNode registration timing.

## Risks and Edge Cases

Risks include file length reverting to block-report length after restart, open incorrectly succeeding while safe mode prevents block access, and the safe-mode polling loop spinning if the NameNode never starts.

## Test Signals

Signals are exact visible length `1030`, successful detection of safe mode, expected IOException on open, and message substring validation for safe mode.
