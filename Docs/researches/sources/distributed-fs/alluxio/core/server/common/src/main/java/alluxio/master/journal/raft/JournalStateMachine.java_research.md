# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/JournalStateMachine.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/JournalStateMachine.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/JournalStateMachine.java

### Purpose
`JournalStateMachine` is the Ratis state machine for the embedded journal. It applies replicated `JournalEntry` commands to the proper Alluxio master, manages sequence-number de-duplication, snapshots and restores master state, and coordinates primary-mode pre-apply behavior.

### Important APIs, Types, And Functions
It extends `BaseStateMachine`. Key methods are `initialize()`, `reinitialize()`, `applyTransaction()`, `applyJournalEntryCommand()`, `takeSnapshot()`, `takeLocalSnapshot()`, `install()`, `pause()`, `unpause()`, `suspend()`, `resume()`, `catchup()`, `upgrade()`, and leader/snapshot notifications. It owns `BufferedJournalApplier`, `RaftSnapshotManager`, and `SnapshotDirStateMachineStorage`.

### Control Flow
Initialization loads the latest snapshot. Each Ratis transaction parses log data into a `JournalEntry`, recursively expands batch entries, records negative sequence numbers as primary-start markers, ignores empty snapshot entries, skips duplicate sequence numbers, and fatals on gaps. Before primacy, entries are applied to masters; after `upgrade()`, `mIgnoreApplys` suppresses primary double-application because requests already modified state before journaling.

### State, Persistence, And Dependencies
Persistent state is held in Ratis logs and snapshot directories named by `SimpleStateMachineStorage`. Snapshots include a `SnapshotIdJournaled` entry plus all master `Journaled` checkpoints, and restore updates `mNextSequenceNumberToRead`. Volatile state tracks commit index, snapshot index/time/durations, primary-start sequence, leader status, suspension callbacks, and closed/snapshotting flags. Dependencies include Apache Ratis, Alluxio `Journaled`, `StateLockManager`, checkpoint streams, metrics, and `RaftSnapshotManager`.

### Integration Points
`RaftJournalSystem` constructs this state machine and calls it for catch-up, checkpoint, suspend/resume, leadership state changes, and dynamic quorum additions through read-only queries. Ratis calls snapshot and install hooks; followers may download snapshots from peers rather than using Ratis snapshot installation.

### Risks
Sequence-number gaps call fatal error, so writer and replay ordering are critical. Primary snapshots require a state lock unless a follower or explicitly allowed leader checkpoint. Snapshot restore can interrupt external suspended work via callback. `mIgnoreApplys` is central to pre-apply correctness and must only be set after catch-up and quiet-period validation. Metrics read some fields outside synchronization.

### Test Signals
Exercise batched entries, duplicates, gaps, negative primary-start markers, empty entries, upgrade no-op apply, snapshot creation/restoration in directory and old single-file formats, pause/unpause interrupt behavior, follower snapshot download hooks, manual leader checkpoint locking, and corruption-tolerant restore paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/JournalStateMachine.java -->
