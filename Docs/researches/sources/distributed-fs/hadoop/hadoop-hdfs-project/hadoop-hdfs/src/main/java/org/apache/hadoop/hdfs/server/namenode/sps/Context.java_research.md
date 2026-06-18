# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/Context.java

## Purpose

`Context` is the NameNode-facing service contract used by SPS code. It exposes lifecycle, namespace, storage policy, DataNode report, scanning, block move submission, and movement notification operations without binding SPS internals directly to `FSNamesystem` implementation details.

## Important APIs, Types, And Functions

The interface declares `isRunning`, `isInSafeMode`, `getNetworkTopology`, `isFileExist`, `getStoragePolicy`, `removeSPSHint`, `getNumLiveDataNodes`, `getFileInfo`, `getLiveDatanodeStorageReport`, `getNextSPSPath`, `scanAndCollectFiles`, `submitMoveTask`, and `notifyMovementTriedBlocks`.

## Control Flow

SPS queue workers call lifecycle/safe-mode methods to decide whether to scan, pull paths through `getNextSPSPath`, scan recursively through `scanAndCollectFiles`, query file and DataNode state for block movement planning, submit movement commands, and receive completion notifications. Implementations bridge these calls to NameNode namespace locks and block manager state.

## State And Persistence Behavior

The interface itself has no state. Persistent SPS intent is represented by NameNode hints/xAttrs that implementations expose via `getNextSPSPath` and mutate via `removeSPSHint`. Live DataNode and topology state is transient.

## Dependencies And Integration Points

It depends on `Block`, `BlockStoragePolicy`, `HdfsFileStatus`, `DatanodeStorageReport`, `BlockMovingInfo`, `NetworkTopology`, and `StoragePolicySatisfier.DatanodeMap`. It is consumed by `BlockStorageMovementNeeded`, `DatanodeCacheManager`, attempted-item tracking, and block move scheduling.

## Risks And Edge Cases

Implementations must obey NameNode locking rules and avoid returning stale namespace objects while SPS worker threads are active. Safe mode, deleted files, unavailable policies, and missing DataNode reports must be handled without leaking SPS hints. Network topology must correspond to the same DataNode map used for scheduling.

## Test Signals

Tests should use mock contexts to cover safe-mode pausing, missing files, hint removal failures, stale DataNode reports, move submission failures, movement notifications, and topology/datanode-map consistency.
