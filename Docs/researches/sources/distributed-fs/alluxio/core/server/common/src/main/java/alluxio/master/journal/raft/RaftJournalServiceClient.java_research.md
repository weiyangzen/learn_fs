# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalServiceClient.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalServiceClient.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalServiceClient.java

### Purpose
`RaftJournalServiceClient` is a master client for the auxiliary Raft journal gRPC service used to discover and download snapshots from peer masters.

### Important APIs, Types, And Functions
It extends `AbstractMasterClient`, identifies `RAFT_JOURNAL_SERVICE`, and builds a blocking `RaftJournalServiceGrpc` stub after connection. `requestLatestSnapshotInfo()` sends `LatestSnapshotInfoPRequest` with a configured deadline. `requestLatestSnapshotData(SnapshotMetadata)` returns a streaming iterator of `SnapshotData`.

### Control Flow
The client is constructed with an explicit `MasterSelectionPolicy`, so `beforeConnect()` intentionally avoids primary discovery. Calls require `connect()` to have populated `mBlockingClient`.

### State, Persistence, And Dependencies
State is the gRPC channel/stub inherited from `AbstractMasterClient`. No data is persisted locally. Dependencies include Alluxio client context, retry policy suppliers, generated gRPC service types, and `MASTER_JOURNAL_REQUEST_INFO_TIMEOUT`.

### Integration Points
`RaftSnapshotManager` creates one client per other master RPC address, requests metadata in parallel, then streams the best snapshot candidate into a local temporary directory.

### Risks
Snapshot data streaming has no explicit deadline in this wrapper, so long-running transfers rely on gRPC/channel behavior and caller handling. `requestLatestSnapshotInfo()` only works after successful connection, and failed metadata calls force the manager to disconnect.

### Test Signals
Test service type/name/version, no-primary-selection behavior, deadline application on info requests, data iterator forwarding, reconnect after failed metadata requests, and use with specified-master selection policies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalServiceClient.java -->
