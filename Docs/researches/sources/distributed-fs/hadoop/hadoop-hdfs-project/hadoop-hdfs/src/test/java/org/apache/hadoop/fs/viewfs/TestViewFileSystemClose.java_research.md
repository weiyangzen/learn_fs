# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemClose.java

## Purpose

`TestViewFileSystemClose` checks that a `ViewFileSystem` closes its child filesystems when inner caching and filesystem caching are disabled. It is a leak-prevention test for child target lifecycle management.

## Important APIs, types, and functions

The test uses `ViewFileSystem`, `FileSystem.get`, `FileSystem.closeAll`, `getChildFileSystems`, `ConfigUtil.addLink`, `FsConstants.VIEWFS_URI`, and `LambdaTestUtils.intercept`. Relevant configuration keys are `fs.viewfs.enable.inner.cache`, `fs.viewfs.impl.disable.cache`, and `fs.hdfs.impl.disable.cache`.

## Control flow, state, and persistence

The test builds an isolated `Configuration`, registers `fs.viewfs.impl`, disables caches, adds `/data -> hdfs://localhost/tmp/data`, creates a `ViewFileSystem`, captures its child filesystems, closes the viewfs and all cached filesystems, then verifies each child rejects create operations with "Filesystem closed". State is limited to in-memory FileSystem objects.

## Dependencies and integration points

This covers ViewFS child filesystem ownership and close propagation when cache semantics do not retain shared instances. It integrates with Hadoop's global `FileSystem` cache and target filesystem close checks.

## Risks and test signals

Regressions would leave target filesystems open after closing ViewFS, causing leaks and unexpected operations after shutdown. The signal is an `IOException` containing "Filesystem closed" for every captured child.
