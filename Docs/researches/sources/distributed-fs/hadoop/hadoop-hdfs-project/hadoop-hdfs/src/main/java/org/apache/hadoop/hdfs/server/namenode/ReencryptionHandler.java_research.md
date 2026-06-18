# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ReencryptionHandler.java

## Purpose
`ReencryptionHandler` is the background worker that walks encryption zones and submits file EDEK re-encryption batches to a KMS-backed thread pool. It coordinates traversal, batching, throttling, cancellation, checkpoint resume, nested-zone skipping, and updater handoff.

## Important APIs, types, and functions
Constructor setup includes `EncryptionZoneManager`, `FSDirectory`, KMS provider validation, sleep interval, batch size, handler throttle ratio, EDEK thread pool, completion service, updater, current batch, and traverser. Key methods are `run`, `startUpdaterThread`, `stopThreads`, `cancelZone`, `removeZone`, `getTracker`, `addDummyTracker`, `notifyNewSubmission`, `reencryptEncryptionZone`, `completeReencryption`, and `restoreFromLastProcessedFile`. Inner types are `ReencryptionBatch`, `EDEKReencryptCallable`, `ReencryptionPendingInodeIdCollector`, and `ZoneTraverseInfo`.

## Control flow
The handler sleeps or waits for notification, selects the next unprocessed zone under read lock, marks it started, resets its tracker, and traverses from the beginning or last checkpoint. The traverser adds encrypted files whose EDEK key version differs from the target version to batches. Batches are submitted to KMS callables that run without NameNode locks. Submission completion is signaled to `ReencryptionUpdater`, with a dummy tracker used when no files need re-encryption.

## State and persistence behavior
Runtime submission trackers and current batches are in memory. Durable re-encryption status and progress are stored by `ReencryptionStatus` and `FSDirEncryptionZoneOp` via xattrs/edit logs, largely through the updater. Cancellation marks status and cancels futures.

## Dependencies and integration points
It depends on `EncryptionZoneManager`, `FSDirectory`, `FSDirEncryptionZoneOp`, `FSTreeTraverser`, `ReencryptionUpdater`, KMS provider APIs, `ZoneReencryptionStatus`, safe-mode/write operation checks, and re-encryption DFS config keys. Client RPC reaches it via `FSNamesystem.reencryptEncryptionZone`.

## Risks and invariants
Only one handler is expected. It must not contact KMS while holding namespace locks. Resume must skip exactly the checkpointed lexicographic prefix. Tracker access is monitor-protected, while namespace consistency relies on FSDirectory/FSNamesystem locks. Large batches can pressure edit-log buffers. Cancellation, safe mode, and standby transitions must prevent stale updates.

## Test signals
Cover submission, empty-zone completion, cancellation, deleted zones, checkpoint resume, nested EZ skip, KMS failure accounting, throttling, safe-mode retry, active/standby behavior, and pause/fault-injection hooks.
