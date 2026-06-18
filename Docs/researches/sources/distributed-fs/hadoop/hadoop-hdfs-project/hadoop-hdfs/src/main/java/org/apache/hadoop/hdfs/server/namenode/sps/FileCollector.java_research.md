# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/FileCollector.java

## Purpose

`FileCollector` is the SPS abstraction for recursively scanning a path and adding files that need storage policy satisfaction to the SPS needed-work queue.

## Important APIs, Types, And Functions

It declares `scanAndCollectFiles(long path) throws IOException, InterruptedException`, where `path` is a file or directory inode/path ID.

## Control Flow

`BlockStorageMovementNeeded.SPSPathIdProcessor` or `Context.scanAndCollectFiles` invokes an implementation for an SPS start path. The implementation walks namespace children, identifies candidate files, and adds them to `SPSService` or `BlockStorageMovementNeeded`, marking directory scan completion when done.

## State And Persistence Behavior

The interface has no state. Implementations read live namespace state and produce transient queue entries. Persistent SPS intent remains in path hints/xAttrs until scan and movement completion remove them.

## Dependencies And Integration Points

It depends only on Java exceptions and Hadoop classification annotations. It integrates with `Context`, `SPSService.addAllFilesToProcess`, and `BlockStorageMovementNeeded` directory pending-work tracking.

## Risks And Edge Cases

Implementations must handle interruption promptly, avoid holding NameNode locks for excessive time, handle deleted paths and permission/namespace errors, and correctly report scan completion for empty directories.

## Test Signals

Tests should cover recursive directory scans, file start paths, empty directories, interruption, deleted paths, batched queue additions, and scan-completion markers.
