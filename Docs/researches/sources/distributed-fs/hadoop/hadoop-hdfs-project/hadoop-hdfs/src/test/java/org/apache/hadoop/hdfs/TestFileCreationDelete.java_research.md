# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileCreationDelete.java

## Purpose

`TestFileCreationDelete.java` verifies lease persistence and cleanup when a parent directory containing an open file is deleted before NameNode restart. The complete 92-line file was read.

## Important APIs, Types, and Functions

Key APIs are `MiniDFSCluster`, `FileSystem.delete`, `FSDataOutputStream.hflush`, `TestFileCreation.createFile`, `TestFileCreation.writeFile`, `DFS_HEARTBEAT_INTERVAL_KEY`, and `DFS_NAMENODE_HEARTBEAT_RECHECK_INTERVAL_KEY`.

## Control Flow

The test starts a cluster with short heartbeat settings and low IPC idle time. It creates `/foo/file1`, writes and hflushes 1000 bytes while leaving the stream open, then creates `/file2` similarly. It deletes `/foo` recursively, shuts the cluster down without formatting, waits across client idle windows, restarts, shuts down again, waits longer, and restarts once more from the same storage. After obtaining a new filesystem handle, it asserts `/foo/file1` does not exist and `/file2` still exists.

## State and Persistence Behavior

The test is about fsimage/edit-log persistence of open-file leases after deletion. File1's parent deletion must remove that lease/path across restarts, while unrelated open file2 must survive as a persistent lease-backed file.

## Dependencies and Integration Points

It depends on `TestFileCreation` helpers, MiniDFSCluster reuse of name/data dirs with `format(false)`, NameNode lease serialization, delete edit replay, and hflush-created block state.

## Risks and Edge Cases

Risks include resurrecting deleted under-construction files after restart, losing unrelated open files during lease replay, and null filesystem cleanup if setup fails before assignment.

## Test Signals

Signals are final `!fs.exists(file1)` and `fs.exists(file2)` assertions after two unformatted restarts.
