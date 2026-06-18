# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestXAttrConfigFlag.java

## Purpose

`TestXAttrConfigFlag` verifies that disabling `dfs.namenode.xattrs.enabled` rejects XAttr client operations while still allowing the NameNode to load existing XAttrs from edit logs and fsimage.

## Important APIs, Types, and Functions

The fixture uses `MiniDFSCluster`, `DistributedFileSystem`, `DFS_NAMENODE_XATTRS_ENABLED_KEY`, `NameNodeAdapter.enterSafeMode`, `NameNodeAdapter.saveNamespace`, `IOUtils.cleanupWithLogger`, and JUnit `Executable` for expected failures.

## Control Flow

Operation tests start a formatted cluster with XAttrs disabled, create `/path`, and assert `setXAttr`, `getXAttrs`, and `removeXAttr` throw `IOException` containing the config key. Persistence tests start with XAttrs enabled, create an XAttr, then restart without formatting with XAttrs disabled. One path restarts from edit logs; the other checkpoints first and restarts from fsimage.

## State and Persistence Behavior

The tests persist a namespace path and `user.foo` XAttr through edit logs and optionally fsimage. Restart helper shuts down the old cluster and reuses storage without formatting under a changed config flag.

## Dependencies and Integration Points

It integrates DFSClient XAttr APIs, NameNode XAttr feature flag checks, edit-log replay, fsimage loading, safe mode, and namespace save.

## Risks and Edge Cases

The key distinction is rejecting new XAttr operations while preserving backward-compatible loading of existing metadata. A bug could make disabling XAttrs render a namespace with XAttrs unbootable.

## Test Signals

Signals are `IOException` messages containing `DFS_NAMENODE_XATTRS_ENABLED_KEY` for active operations and successful restarts with disabled XAttrs after both edit-log and fsimage persistence.
