# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/SnapshotIdJournaled.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/SnapshotIdJournaled.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/SnapshotIdJournaled.java

### Purpose
`SnapshotIdJournaled` is a small `SingleEntryJournaled` implementation used to store the last journal sequence number included in an embedded-journal snapshot.

### Important APIs, Types, And Functions
It overrides `getCheckpointName()` to return `CheckpointName.SNAPSHOT_ID`. It inherits single-entry checkpoint read/write behavior from `SingleEntryJournaled`.

### Control Flow
During snapshot creation, `JournalStateMachine` processes a synthetic `JournalEntry` whose sequence number is the snapshot ID, then writes this as a checkpoint entry. During restore, another instance restores that checkpoint and exposes the stored entry for sequence-number recovery.

### State, Persistence, And Dependencies
The persisted state is one `JournalEntry` under the `SNAPSHOT_ID` checkpoint name in the snapshot directory. Dependencies include `SingleEntryJournaled`, `CheckpointName`, and journal protobufs.

### Integration Points
`JournalStateMachine.takeLocalSnapshot()` and `install()` use this class before all master checkpoints to align snapshot term/index with Alluxio global sequence numbers.

### Risks
If the snapshot ID is missing or corrupt, restore cannot correctly set `mNextSequenceNumberToRead`, which can cause duplicate or skipped replay. It only stores sequence number, not per-master sequence state.

### Test Signals
Validate checkpoint name, write/restore of a sequence-number entry, missing entry handling through inherited behavior, and integration in snapshot restore updating next sequence number.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/SnapshotIdJournaled.java -->
