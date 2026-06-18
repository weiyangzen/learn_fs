## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsActiveSyncProvider.java

### Purpose
`HdfsActiveSyncProvider` abstracts HDFS inotify-based active sync support behind a provider interface.

### Important APIs, Types, And Functions
The interface exposes `getActivitySyncInfo`, `startPolling(long)`, `stopPolling`, `startSync(AlluxioURI)`, and `stopSync(AlluxioURI)`.

### Control Flow
Implementations are responsible for starting and stopping a polling thread, tracking sync points, and returning `SyncInfo` deltas or full-sync signals.

### State, Persistence, And Dependencies
The interface itself has no state. It depends on `AlluxioURI`, `SyncInfo`, and checked IO errors for polling startup.

### Integration Points
`HdfsUnderFileSystem` delegates all active-sync methods to a reflected provider or a no-op fallback.

### Risks
The interface does not prescribe threading or lifecycle semantics beyond boolean start/stop results, so implementations must be careful about duplicate starts and concurrent sync-point updates.

### Test Signals
No direct tests are present. Integration tests should validate provider availability by Hadoop version/profile and `SyncInfo` correctness after file-system events.
