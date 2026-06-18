# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalMultiMasterPrimarySelector.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalMultiMasterPrimarySelector.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalMultiMasterPrimarySelector.java

### Purpose
`UfsJournalMultiMasterPrimarySelector` uses ZooKeeper/Curator leader election to choose the primary master for UFS journal deployments.

### Important APIs, Types, And Functions
It extends `AbstractPrimarySelector` and implements `LeaderSelectorListener`. Public methods are `start()`, `stop()`, `getName()`, `stateChanged()`, and `takeLeadership()`. Helpers handle standard versus session-based connection error policy and build Curator clients.

### Control Flow
Construction creates a `LeaderSelector` with auto-requeue. `start()` sets this participant's `host:port` ID and starts selection. `takeLeadership()` sets `PRIMARY`, writes an ephemeral leader path, records the ZooKeeper session, waits until state becomes standby, then deletes the leader path and clears session ID. Connection state changes can demote to standby or preserve primary if session identity survived reconnection under session policy.

### State, Persistence, And Dependencies
State includes election/leader paths, Curator leader selector, participant name, ZooKeeper address, leader session ID, connection policy, and lifecycle state. Persistent/external state is ZooKeeper ephemeral znodes. Dependencies include Curator, ZooKeeper, Alluxio configuration, and `ZookeeperConnectionErrorPolicy`.

### Integration Points
`UfsJournalSystem` uses this selector in multi-master UFS mode to drive gain/loss of primacy across all UFS journals.

### Risks
Incorrect handling of suspended/lost ZooKeeper sessions can produce stale primary state; the session policy mitigates this by comparing session IDs. Leader path cleanup can fail if the session changes. The constructor intentionally creates and closes a client once to avoid stale server session behavior after fast restart.

### Test Signals
Test lifecycle transitions, participant ID, standard-policy demotion, session-policy reconnection with same/different session IDs, ephemeral leader path creation/deletion, auto-requeue behavior, stop before/after start, and Curator client configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalMultiMasterPrimarySelector.java -->
