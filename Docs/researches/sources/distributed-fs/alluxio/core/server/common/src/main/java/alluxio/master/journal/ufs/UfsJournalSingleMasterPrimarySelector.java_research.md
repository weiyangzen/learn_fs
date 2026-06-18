# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalSingleMasterPrimarySelector.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalSingleMasterPrimarySelector.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalSingleMasterPrimarySelector.java

### Purpose
`UfsJournalSingleMasterPrimarySelector` is the primary selector for single-master UFS journal deployments.

### Important APIs, Types, And Functions
It extends `AbstractPrimarySelector`. `start(InetSocketAddress)` immediately sets state to `PRIMARY`. `stop()` is a no-op.

### Control Flow
There is no election or external coordination; starting the selector makes the only master primary.

### State, Persistence, And Dependencies
Selector state is inherited and in-memory. It has no persistent state and depends only on `NodeState`, `AbstractPrimarySelector`, and the local address parameter.

### Integration Points
`UfsJournalSystem` can use this selector when ZooKeeper/multi-master election is not configured, allowing UFS journals to gain primacy immediately.

### Risks
Using this selector in a multi-master deployment would allow unsafe split-brain writes. Stop does not demote state, so lifecycle owners must not reuse it in contexts that expect a stopped state transition.

### Test Signals
Verify immediate primary on start, no exception on stop, and integration that single-master UFS journal systems gain primacy without ZooKeeper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalSingleMasterPrimarySelector.java -->
