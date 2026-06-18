# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/BlockStorageMovementNeeded.java

## Purpose

`BlockStorageMovementNeeded` is the SPS queue for files needing storage policy satisfaction work. It also tracks directory scan progress so SPS can remove the satisfier xAttr once every file under a requested directory has been processed.

## Important APIs, Types, And Functions

Important state includes `storageMovementNeeded`, `pendingWorkForDirectory`, `Context`, `SPSPathIdProcessor`, and its daemon. Public APIs include `add`, `addAll`, `get`, `size`, `clearAll`, `removeItemTrackInfo`, `clearQueuesWithNotification`, `activate`, `close`, `markScanCompletedForDir`, and test setters/getters for status clearance. Nested `DirPendingWorkInfo` tracks `pendingWorkCount` and `fullyScanned`.

## Control Flow

Files are added directly or as scan results for a start path. Directory scan additions update pending-work counts and mark scans complete when the collector reports no more files. `SPSPathIdProcessor` runs while context is running, skips work in safe mode, pulls the next SPS path from context, scans files, removes xAttr for empty/completed directories, retries scan failures up to three times, and sleeps while idle or after errors. When movement for an item succeeds, `removeItemTrackInfo` decrements directory pending count and removes the directory xAttr when the scan is fully done and all child work is complete; file start paths remove their xAttr directly.

## State And Persistence Behavior

The queue and pending-work map are in-memory. Persistent intent is represented outside this class by SPS xAttrs/hints accessed through `Context.getNextSPSPath` and `removeSPSHint`. `clearQueuesWithNotification` removes outstanding hints before clearing local state.

## Dependencies And Integration Points

It depends on `Context` for safe mode, scanning, hint retrieval/removal, and file existence checks. It integrates with `SPSService.addFileToProcess`, recursive `FileCollector` implementations, `BlockStorageMovementAttemptedItems`, and NameNode xAttr state for SPS requests.

## Risks And Edge Cases

Directory pending counts can go negative if decrement calls outnumber queued file additions, but `isDirWorkDone` treats `<= 0` as done once fully scanned. If scanning fails three times, the path is skipped and may retain or lose external hint depending on subsequent handling. Safe mode causes the processor loop to spin without the normal idle sleep in the safe-mode branch. `clearQueuesWithNotification` calls synchronized `get` while already synchronized, relying on Java reentrant locks.

## Test Signals

Tests should cover file and directory item queueing, scan-complete marking, empty directory xAttr removal, child completion decrement/removal, deleted start paths, force clearing with hint cleanup, safe-mode behavior, scan retry limit, interruption, and concurrent add/get/remove access.
