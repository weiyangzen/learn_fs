# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalUtils.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalUtils.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalUtils.java

### Purpose
`RaftJournalUtils` centralizes small helper operations for embedded-journal peer IDs, storage paths, temporary snapshot files, and exceptional futures.

### Important APIs, Types, And Functions
`RAFT_DIR` is the storage subdirectory. `getPeerId(InetSocketAddress)` and `getPeerId(String,int)` encode peers as `host_port`. `getRaftJournalDir(File)` returns `<base>/raft`. `createTempSnapshotFile(SimpleStateMachineStorage)` creates a timestamped temp `.dat` file under a sibling `tmp` directory. `completeExceptionally(Exception)` creates a failed `CompletableFuture`.

### Control Flow
Methods are direct helpers. Temporary snapshot creation ensures the temp directory exists before calling `File.createTempFile()`.

### State, Persistence, And Dependencies
No mutable state is stored. The path helpers define persistent directory conventions consumed by `RaftJournalSystem` and Ratis. Dependencies include Ratis `RaftPeerId`, `SimpleStateMachineStorage`, Java `File`, and futures.

### Integration Points
`RaftJournalSystem` uses peer ID and raft directory helpers for group/server setup and quorum operations. `JournalStateMachine.applyTransaction()` uses `completeExceptionally()` through failed apply futures.

### Risks
Peer IDs replace host/port separator with `_`, so reverse parsing elsewhere assumes that convention. `createTempSnapshotFile()` is tied to the old single-file snapshot utility path and must not conflict with directory-snapshot tmp handling.

### Test Signals
Check peer ID formatting for hostnames/IPs, raft directory construction, temp directory creation failure, unique temp file creation, and failed future propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalUtils.java -->
