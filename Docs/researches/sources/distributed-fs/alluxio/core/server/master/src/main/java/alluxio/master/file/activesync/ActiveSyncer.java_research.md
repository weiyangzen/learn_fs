# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/activesync/ActiveSyncer.java

## Purpose
`ActiveSyncer` is the heartbeat executor for one mount id. It consumes active-sync events from a UFS, submits metadata sync work for changed sync points, and records the processed transaction id after the work completes.

## Important APIs, types, and functions
The constructor stores `FileSystemMaster`, `ActiveSyncManager`, `MountTable`, mount id, mount URI, and creates a bounded queue of sync tasks. `heartbeat(long)` removes completed tasks, gets the mount filter list, reads `SyncInfo` from UFS, submits per-sync-point `CompletableFuture` work, and chains tx-id journaling. `close()` cancels queued sync tasks. `processSyncPoint` resolves UFS URIs back to Alluxio URIs and calls `activeSyncMetadata`.

## Control flow
Each heartbeat exits if no filters are registered or the UFS lacks active sync. Otherwise it processes every UFS sync point in `SyncInfo`. Force sync triggers full metadata sync for the resolved Alluxio path. Incremental sync maps changed UFS files through `MountTable.reverseResolve` and passes them to the master. The queued aggregate future records the tx id only after all per-sync futures complete.

## State and persistence behavior
Runtime state is the bounded queue of in-flight sync futures. Persistent active-sync progress is written indirectly through `FileSystemMaster.recordActiveSyncTxid`.

## Dependencies and integration points
It integrates with UFS active-sync APIs, `ActiveSyncManager` retry/executor/filter state, `FileSystemMaster.activeSyncMetadata`, mount reverse resolution, heartbeat scheduling, and configuration for heartbeat interval.

## Risks
The bounded queue can delay new task admission when prior syncs are slow. Reverse resolution returning null is handled for sync-point URI but changed-file mapping uses `Objects.requireNonNull`, so an unresolved changed file can fail the incremental task. Tx id is recorded after all tasks complete, so a single slow or failed task can delay progress. `timeLimitMs` is not directly enforced.

## Test signals
Tests should cover force versus incremental sync, unresolved UFS URIs, retry behavior, tx-id recording after completion, queue saturation, and cancellation in `close()`.
