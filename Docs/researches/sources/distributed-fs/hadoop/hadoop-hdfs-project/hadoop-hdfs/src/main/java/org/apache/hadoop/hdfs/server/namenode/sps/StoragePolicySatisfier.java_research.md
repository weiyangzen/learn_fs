<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/StoragePolicySatisfier.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/StoragePolicySatisfier.java

## Purpose

`StoragePolicySatisfier` is the NameNode/external-service worker that turns a `satisfyStoragePolicy` request into concrete block movement tasks. It dequeues inode work, reads current file/block placement, compares actual storage media against the file's `BlockStoragePolicy`, chooses source and target DataNodes, submits `BlockMovingInfo` tasks, and tracks attempts until DataNodes report completion or retry limits are reached.

## Important APIs and types

- Implements `SPSService` and `Runnable`; lifecycle is `init(Context)`, `start(StoragePolicySatisfierMode)`, `stop`, `stopGracefully`, `run`, `join`.
- `BlocksMovingAnalysis` and its `Status` enum summarize per-file analysis outcomes: retry, paired targets, no targets, already satisfied, skipped, low redundancy, or task submission failure.
- `analyseBlocksStorageMovementsAndAssignToDN` is the main block-analysis routine.
- `computeBlockMovingInfos`, `findSourceAndTargetToMove`, `chooseTargetTypeInSameNode`, and `chooseTarget` build source/target pairs.
- `DatanodeMap`, `DatanodeWithStorage`, and `StorageDetails` cache live DataNode storage media and available movement capacity.
- `AttemptedItemInfo` extends `ItemInfo` with last attempt/report time and scheduled block set for the attempted-items monitor.

## Control flow

`init` wires the NameNode/external `Context`, `BlockStorageMovementNeeded` queue, attempted-items monitor, work multiplier, and retry limit. `start` rejects `NONE`, starts the main daemon and monitor, activates the needed queue, and builds a `DatanodeCacheManager`.

The `run` loop skips work if the upstream context is down or the NameNode is in safe mode. For each `ItemInfo`, it enforces `blockMovementMaxRetry`, gets file status by inode id, drops deleted directories/files, loads the current storage policy, and analyzes located blocks. Paired or retry-skipped work is put into the attempt monitor; no-target, low-redundancy, and failed movement states are requeued; already satisfied or skipped states remove SPS tracking/xattrs. The loop throttles by sleeping when the queue is empty or when scheduled block count exceeds live DataNodes times the configured work multiplier.

Block analysis rejects under-construction files, skips empty files, validates EC striped policy compatibility, computes expected storage types, removes already-satisfied/non-movable overlaps, and schedules move tasks through `ctxt.submitMoveTask`. Continuous blocks produce a single local `Block`; striped blocks are converted into internal block ids and lengths using `StripedBlockUtil`.

## State and persistence behavior

Runtime state is in memory: `isRunning`, worker thread, queue objects, monitor state, `blockCount`, retry counts, and cached DataNode storage reports. Persistent namespace effects happen indirectly through `BlockStorageMovementNeeded.removeItemTrackInfo`, which can clean the satisfy-storage-policy xattr when work is done or abandoned. The class itself does not write files or edit logs; it relies on the NameNode context, DataNode reports, and queue/monitor collaborators for persistence-visible effects.

## Dependencies and integration points

The class integrates with HDFS file metadata (`HdfsLocatedFileStatus`, `LocatedBlock`, `LocatedStripedBlock`), storage policies, EC policy validation, DataNode topology matching (`Matcher.SAME_NODE_GROUP`, `SAME_RACK`, `ANY_OTHER`), `BlockStorageMovementCommand.BlockMovingInfo`, SPS queues/monitors, and external SPS service contexts. It is also used by `ExternalStoragePolicySatisfier`, `ExternalSPSContext`, and SPS metrics.

## Risks and edge cases

- Target selection mutates the `expectedStorageTypes` and `existing` lists in place; callers must pass throwaway lists.
- The initial `foundMatchingTargetNodesForBlock` value is `true` and is OR-assigned, so careful tests are needed around partial target failures.
- EC striped block movement depends on block index mapping and internal block length calculation; off-by-one/index errors can corrupt movement requests.
- Low redundancy, under-construction files, safe mode, unavailable storage media, and retry limits all affect whether SPS cleans xattrs or requeues work.
- Scheduling capacity is approximate and held in the cached storage details for one analysis pass.

## Test signals

Relevant signals include `TestExternalStoragePolicySatisfier`, `TestPersistentStoragePolicySatisfier`, `TestStoragePolicySatisfierWithHA`, `TestStoragePolicySatisfierWithStripedFile`, WebHDFS SPS coverage, admin command tests, and mover conflict tests. Good coverage should include EC striped policies, unavailable target media, low redundancy, retry-limit cleanup, same-node moves, rack/node-group fallback, and DataNode movement-finished reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/StoragePolicySatisfier.java -->
