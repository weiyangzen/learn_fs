<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/StoragePolicySatisfyManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/StoragePolicySatisfyManager.java

## Purpose

`StoragePolicySatisfyManager` is the BlockManager-side coordinator for satisfy-storage-policy requests. It holds administrator configuration, tracks pending path inode ids for external SPS mode, enforces the outstanding queue limit, and clears queued SPS hints when the feature or mode is disabled.

## Important APIs and types

- Constructor reads `dfs.storage.policy.enabled`, SPS mode, and max outstanding path config.
- `start`, `stop`, and `changeModeEvent` implement mode transitions for `EXTERNAL` and `NONE`.
- `addPathId`, `getNextPathId`, `removeAllPathIds`, and `getPendingSPSPaths` manage the pending inode id queue.
- `verifyOutstandingPathQLimit` protects the queue from unbounded user requests.
- `isEnabled` means external SPS mode is enabled, not that an internal worker is running.

## Control flow

Startup logs the configured mode but does not start the internal `StoragePolicySatisfier`; this manager is for external or disabled operation. On `stop` in external mode it clears path ids. On `changeModeEvent(EXTERNAL)` it stops any internal satisfier gracefully before switching. On `changeModeEvent(NONE)` it force-stops SPS, removes the xattr for each queued inode through `Namesystem.removeXattr`, clears the queue, and updates mode.

## State and persistence behavior

The path queue is an in-memory `LinkedList<Long>` guarded by synchronization on the queue object. The manager mutates persistent namespace state only while clearing queued ids: it removes `XATTR_SATISFY_STORAGE_POLICY` from each inode so disabled SPS requests do not survive as active hints.

## Dependencies and integration points

It depends on `Namesystem`, `HdfsServerConstants.XATTR_SATISFY_STORAGE_POLICY`, `DFSConfigKeys`, `StoragePolicySatisfierMode`, and the external SPS entry point. BlockManager/NameNode RPC paths use it when users invoke `satisfyStoragePolicy` or when admins reconfigure SPS mode.

## Risks and edge cases

- `getPendingSPSPaths` reads `LinkedList.size()` without synchronizing, so it is only an approximate metric under concurrent mutation.
- Queue entries are plain inode ids; stale ids are handled later by SPS or xattr cleanup.
- `isEnabled` returns true only for `EXTERNAL`, which can be misread as a generic feature-enabled flag.
- `verifyOutstandingPathQLimit` is based on a snapshot size and must be called while higher-level request paths still handle races.

## Test signals

Signals include SPS admin command tests, NameNode reconfiguration tests, persistent SPS tests, HA SPS tests, and external SPS integration tests. Important assertions are mode transitions, xattr cleanup in `NONE`, outstanding queue limit errors, and external queue polling order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/StoragePolicySatisfyManager.java -->
