# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftPrimarySelector.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftPrimarySelector.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftPrimarySelector.java

### Purpose
`RaftPrimarySelector` adapts embedded-journal leadership notifications into Alluxio's primary selector abstraction.

### Important APIs, Types, And Functions
It extends `AbstractPrimarySelector`. `start(InetSocketAddress)` initializes state to `STANDBY`, and `stop()` transitions to `STOPPED`.

### Control Flow
Actual primary/standby transitions are driven externally by `RaftJournalSystem.notifyLeadershipStateChanged()`, which calls inherited state-change methods. This class only initializes and stops the selector.

### State, Persistence, And Dependencies
Selector state is inherited and in-memory only. Dependencies are `NodeState`, `AbstractPrimarySelector`, and the local address passed on start.

### Integration Points
`RaftJournalSystem` exposes this selector to the master process and updates it from `JournalStateMachine` Ratis leader callbacks. `gainPrimacy()` checks it during catch-up.

### Risks
If Ratis leader notifications are delayed or missed, this selector reports stale primary state. `start()` always begins as standby even in a single-node cluster until Ratis elects the server.

### Test Signals
Verify start-to-standby, stop-to-stopped, external primary/standby notifications through the journal system, and waiters on `AbstractPrimarySelector` seeing transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftPrimarySelector.java -->
