# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/activesync/ActiveSyncManager.java

## Purpose
`ActiveSyncManager` manages active UFS sync points, polling threads, initial full sync tasks, and journaled active-sync state. It coordinates UFS event polling with file-system master metadata sync so mounted paths can stay current without only relying on lazy sync.

## Important APIs, types, and functions
The class implements `Journaled`. Public operations include `start`, `stop`, `startSyncAndJournal`, `stopSyncAndJournal`, `stopSyncForMount`, `getFilterList`, `getSyncPathList`, `setTxId`, `getExecutor`, recovery helpers, journal processing, reset, and checkpoint iterator methods. State maps track pollers by mount id, sync filters by mount id, starting tx ids, and initial sync futures by sync point. `launchPollingThread`, `startInitialFullSync`, `startSyncInternal`, and `stopSyncInternal` manage runtime tasks.

## Control flow
Starting the manager initializes UFS sync monitoring for all journaled sync points, launches polling threads for mounts with filters, and optionally starts initial full syncs when no valid tx id exists. Starting a sync point validates UFS support and duplicate coverage, applies and journals `AddSyncPointEntry`, then launches initial sync and polling; failures journal a removal and recover runtime state. Stopping applies and journals `RemoveSyncPointEntry`, cancels initial sync, stops polling when the last filter for a mount disappears, and tells UFS to stop monitoring the path.

## State and persistence behavior
Persistent state is journaled through add/remove sync-point entries and active-sync tx-id entries. `getJournalEntryIterator` checkpoints sync points plus tx ids. Runtime state lives in concurrent maps, a copy-on-write sync path list, futures, and a thread pool. `resetState` stops sync points for every mount using `RpcContext.NOOP`.

## Dependencies and integration points
It depends on `MountTable`, UFS active-sync APIs, `FileSystemMaster.activeSyncMetadata`, `recordActiveSyncTxid`, `ActiveSyncer`, heartbeat threads, retry policy configuration, journal/checkpoint APIs, server user state, and path utilities. Client RPC start/stop/list methods reach this through `FileSystemMaster`.

## Risks
The class is annotated not thread-safe but uses concurrent collections and a lock for some compound operations; all callers must respect locking for multi-step state transitions. `startInitialFullSync` captures a UFS resource in a submitted task while the try-with-resources scope closes after submission, so resource lifetime should be reviewed against the resource wrapper semantics. Failure recovery must keep journaled state and runtime futures/pollers consistent. `stop()` iterates while `stopSyncInternal` mutates maps/lists. Active sync support and tx-id replay are UFS-specific.

## Test signals
Tests should cover journal replay/checkpoint, duplicate sync-point rejection, unsupported UFS, start failure rollback, stop failure recovery, tx-id recording, restart with existing tx ids, initial sync enable/disable, and cleanup of futures/pollers when the last sync point for a mount is removed.
