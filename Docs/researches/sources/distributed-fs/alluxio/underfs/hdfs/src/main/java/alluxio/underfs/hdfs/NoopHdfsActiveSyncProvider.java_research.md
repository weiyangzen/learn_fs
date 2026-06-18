## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/NoopHdfsActiveSyncProvider.java

### Purpose
`NoopHdfsActiveSyncProvider` is the fallback ActiveSync provider when HDFS inotify support is unavailable or excluded.

### Important APIs, Types, And Functions
`getActivitySyncInfo` returns `SyncInfo.emptyInfo`. `startPolling` and `stopPolling` return false. `startSync` and `stopSync` are no-ops.

### Control Flow
Every method returns immediately without starting threads or tracking sync points.

### State, Persistence, And Dependencies
There is no mutable state. It depends on `SyncInfo` and `AlluxioURI`.

### Integration Points
`HdfsUnderFileSystem.supportsActiveSync` checks whether the active-sync provider is an instance of this class.

### Risks
Deployments expecting active sync can silently run without it if the supported provider is not in the extension jar or cannot initialize.

### Test Signals
No direct tests are present. ActiveSync integration tests should verify `supportsActiveSync` under the relevant build profiles.
