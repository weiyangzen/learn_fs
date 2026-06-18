# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileAppendRestart.java

## Purpose

`TestFileAppendRestart.java` verifies append edit-log persistence and compatibility across NameNode restarts. The complete 218-line file was read. It is primarily a regression suite for HDFS-2991, where append at block boundaries could miss required edit-log operations.

## Important APIs, Types, and Functions

Key APIs are `FSImageTestUtil.countEditLogOpTypes`, `FSEditLogOpCodes`, `NNStorage.getInProgressEditsFileName`, `StartupOption.UPGRADE`, `FileUtil.unTar`, `AppendTestUtil.write`, and `AppendTestUtil.check`. The helper `writeAndAppend` creates a file with 4096-byte blocks, writes an initial length, appends another length, closes, and asserts the total file length.

## Control Flow

`testAppendRestart` disables persistent IPC so a DFSClient can survive restart, starts a one-DataNode cluster, writes/appends at an exact block boundary, and checks edit-log counts for `OP_ADD`, `OP_APPEND`, two `OP_ADD_BLOCK`, and two `OP_CLOSE` operations. It then writes/appends at a non-block boundary and expects an additional `OP_UPDATE_BLOCKS`. After NameNode restart, it verifies both files' readable lengths. `testLoadLogsFromBuggyEarlierVersions` untars a Hadoop 0.23-era fsimage/edit-log fixture and boots with upgrade to prove old buggy append logs load to the expected file length. `testAppendWithPipelineRecovery` appends after stopping a DataNode in a 4-node rack-aware pipeline, restarts the NameNode, and checks file content length.

## State and Persistence Behavior

This file is explicitly about edit-log and fsimage persistence. It reads in-progress edits, imports archived name directories, upgrades old image format, restarts NameNode, and validates replayed file length.

## Dependencies and Integration Points

It integrates NameNode storage layout, FSImage test utilities, append edit op semantics, pipeline recovery, rack-aware MiniDFSCluster setup, and test-cache archived images.

## Risks and Edge Cases

Risks include missing `OP_ADD`/`OP_APPEND`/`OP_UPDATE_BLOCKS` on append, inability to load historical buggy logs, and pipeline recovery edits failing after restart.

## Test Signals

Signals are exact edit-op counts, exact file status lengths, `AppendTestUtil.check` after restart, archive directory existence, and successful upgrade-mode startup.
