# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalServiceHandler.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalServiceHandler.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalServiceHandler.java

### Purpose
`RaftJournalServiceHandler` serves latest snapshot metadata and snapshot directory bytes over gRPC so lagging embedded-journal followers can bootstrap from other masters.

### Important APIs, Types, And Functions
It implements `requestLatestSnapshotInfo()` and `requestLatestSnapshotData()`. `SnapshotGrpcOutputStream` chunks marshalled directory bytes into `SnapshotData` messages using `MASTER_EMBEDDED_JOURNAL_SNAPSHOT_REPLICATION_CHUNK_SIZE` and `UnsafeByteOperations` to avoid copies.

### Control Flow
Metadata requests return `exists=false` when storage has no snapshot, otherwise term/index. Data requests convert term/index to the Ratis snapshot directory name, marshal that directory into the gRPC stream, complete the observer, and update upload metrics. Cancellation is checked before doing work; exceptions are returned as internal gRPC errors.

### State, Persistence, And Dependencies
The handler is read-only over `StateMachineStorage` snapshot directories. It tracks last upload duration, compressed stream size, and disk size metrics. Dependencies include generated gRPC classes, Ratis `SnapshotInfo`, `SimpleStateMachineStorage`, `DirectoryMarshaller`, metrics, and protobuf `ByteString`.

### Integration Points
Registered by `RaftJournalSystem.getJournalServices()` as `RAFT_JOURNAL_SERVICE`. `RaftSnapshotManager` is the client-side consumer.

### Risks
The data path trusts requested term/index and reads the corresponding directory; missing or changing directories surface as upload failures. Chunk buffering allocates a new byte array per flush. Cancellation is only checked at request start, not during long marshalling.

### Test Signals
Cover no-snapshot metadata, valid metadata, cancelled requests, successful directory stream round trip, chunk boundary sizes, observer errors on marshalling failure, and metric updates for duration and byte counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalServiceHandler.java -->
