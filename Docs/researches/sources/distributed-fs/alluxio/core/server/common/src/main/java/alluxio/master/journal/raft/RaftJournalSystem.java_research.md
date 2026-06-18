# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalSystem.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalSystem.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalSystem.java

### Purpose
`RaftJournalSystem` multiplexes Alluxio master journals into one embedded Apache Ratis group. It owns server startup, primacy transitions, catch-up, snapshots, dynamic quorum operations, leadership transfer, formatting, and journal services.

### Important APIs, Types, And Functions
It extends `AbstractJournalSystem`. Key methods include `initServer()`, `startInternal()`, `stopInternal()`, `createJournal()`, `gainPrimacy()`, `losePrimacy()`, `catchUp()`, `checkpoint()`, `sendMessageAsync()`, `getQuorumServerInfoList()`, `addQuorumServer()`, `removeQuorumServer()`, `transferLeadership()`, `format()`, and metric helpers. It owns `RaftServer`, `JournalStateMachine`, `SnapshotDirStateMachineStorage`, `RaftPrimarySelector`, and shared writer references.

### Control Flow
Startup builds peer IDs from configured embedded-journal addresses, creates a fixed Raft group, configures Ratis storage/log/snapshot/timeouts/transport limits, starts the server, and asynchronously joins the quorum. Gaining primacy writes a random negative sequence marker, waits for it to apply and for an election quiet period, upgrades the state machine to ignore primary replays, then publishes an `AsyncJournalWriter`. Losing primacy closes writers, closes and recreates the Ratis server, and returns to standby replay.

### State, Persistence, And Dependencies
Persistent data lives under the journal path's `raft` directory, migrated from an older group-root layout if present. State includes the Raft group, peer ID, transfer gate, journals map, shared writer references, quorum transfer messages, and metrics. Dependencies are Apache Ratis, Alluxio configuration, metrics, networking utilities, gRPC service registration, and filesystem utilities.

### Integration Points
Masters call `createJournal()` for per-master journals and use the returned `PrimarySelector`. Admin paths call quorum info, add/remove server, transfer leadership, and checkpoint. `JournalStateMachine` calls back on leadership and configuration changes.

### Risks
Pre-apply correctness depends on catch-up marker ordering and the quiet-period heuristic. Ratis configuration values must align with journal entry and flush batch sizes. Leadership transfer is asynchronous and temporarily disables repeated transfer attempts. Formatting deletes the journal path. Dynamic quorum changes assume the current server/group view is fresh.

### Test Signals
Exercise single-node timeout override, old journal migration, start/stop, primacy gain/loss, catch-up retry on `LeaderNotReadyException`, writer publication/removal, manual checkpoint, dynamic quorum add/remove, transfer success/failure messages, formatting access checks, metrics registration, and group update after configuration change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalSystem.java -->
