## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/activesync/SupportedHdfsActiveSyncProvider.java

### Purpose
`SupportedHdfsActiveSyncProvider` implements HDFS ActiveSync using HDFS inotify events. It tracks configured sync points, batches events, records changed files, and returns `SyncInfo` when activity becomes quiet enough or old enough to sync.

### Important APIs, Types, And Functions
The constructor builds an `HdfsAdmin`, read/write locks, thread pool, sync-point list, change maps, transaction-id maps, and thresholds from configuration. Core methods are `startPolling`, `stopPolling`, `startSync`, `stopSync`, `pollEvent`, `processEvent`, `recordFileChanged`, `getActivitySyncInfo`, and `getCountSinceLastLog`.

### Control Flow
Polling opens an inotify event stream from a supplied txid or current stream, then submits a polling loop. The loop polls batches up to configured batch size, submits event-processing tasks, and periodically logs throughput. Events map CREATE/UNLINK/APPEND/RENAME/METADATA paths to sync points by prefix. `getActivitySyncInfo` ages activity windows, returns a full sync if events were missed, or returns changed-file sets when activity drops below the max threshold or exceeds max age.

### State, Persistence, And Dependencies
State is concurrent in-memory maps for changed files, activity, age, txids, current txid, missed-event flag, task queue, polling future, and sync-point list. Persistent filesystem data is not modified. Dependencies include Hadoop `HdfsAdmin`, `DFSInotifyEventInputStream`, inotify events, Alluxio `SyncInfo`, locks, executor services, and sampling logs.

### Integration Points
`HdfsUnderFileSystem` loads this class reflectively when compiled and delegates all active-sync methods. Alluxio master active-sync logic consumes the returned `SyncInfo`.

### Risks
Concurrency is subtle: event processing tasks and `getActivitySyncInfo` mutate the same maps, and `syncSyncPoint` removes map entries while tasks can still record changes. Missing events force full syncs. Path-prefix matching must handle renames into and out of sync points. Polling and processing share the same executor, which can affect latency under high event volume.

### Test Signals
No tests are included here. Valuable tests would simulate inotify batches, missing events, rename paths, concurrent sync-point removal, txid tracking, activity/age thresholds, and duplicate start/stop behavior.
