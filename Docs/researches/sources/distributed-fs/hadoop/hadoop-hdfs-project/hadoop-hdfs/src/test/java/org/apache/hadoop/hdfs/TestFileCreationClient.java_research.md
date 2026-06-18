# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileCreationClient.java

## Purpose

`TestFileCreationClient.java` tests DFSClient-triggered lease recovery while multiple slow writers are actively flushing files and a DataNode fails. The complete 150-line file was read.

## Important APIs, Types, and Functions

Key APIs are `MiniDFSCluster`, `FileSystem.create/open`, `FSDataOutputStream.hflush`, `SubjectInheritingThread`, `DFS_DATANODE_HANDLER_COUNT_KEY`, `DFS_REPLICATION_KEY`, `DataNode`, `LeaseManager`, `FSNamesystem`, and `InterDatanodeProtocol` logging. The nested `SlowWriter` thread creates one path, writes increasing byte values, hflushes after every byte, sleeps, and closes in `finally`.

## Control Flow

`testClientTriggeredLeaseRecovery` starts a three-DataNode cluster with replication 3 and one DataNode handler. It creates ten `SlowWriter` threads under `/wrwelkj`, starts them, lets them write for a second, stops one random DataNode, and lets writing continue for several more seconds. In `finally`, it flips each writer's `running` flag, interrupts and joins all threads, then verifies every produced file by reading from byte 0 to EOF and asserting byte value equals its sequence index.

## State and Persistence Behavior

State consists of ten open HDFS files, per-writer output streams, hflushed bytes, DataNode liveness, and recovered pipeline/lease state. There is no restart persistence, but data must remain readable after client-side recovery from a DataNode stop.

## Dependencies and Integration Points

The test integrates DFSClient write-pipeline recovery, lease recovery, hflush visibility, DataNode handler pressure, and inter-DataNode recovery protocols.

## Risks and Edge Cases

Risks include writer threads swallowing failures while producing truncated files, lease recovery not triggering when a DataNode dies mid-write, and byte values exceeding single-byte expectations if writers run too long.

## Test Signals

Signals are successful joins, non-throwing writer close paths, file status lengths printed for each writer, and sequential byte equality for every file read to EOF.
