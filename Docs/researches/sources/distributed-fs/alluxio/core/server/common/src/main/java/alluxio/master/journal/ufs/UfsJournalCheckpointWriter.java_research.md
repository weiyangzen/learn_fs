# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalCheckpointWriter.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalCheckpointWriter.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalCheckpointWriter.java

### Purpose
`UfsJournalCheckpointWriter` writes a checkpoint to a temporary UFS file and commits it atomically enough by renaming to the final checkpoint filename.

### Important APIs, Types, And Functions
`create(UfsJournal,long)` builds the tmp path, final `UfsJournalFile`, and output stream. `write(byte[],int,int)` delegates to the underlying stream. `close()` commits or discards the checkpoint. `cancel()` closes and deletes the temporary file.

### Control Flow
Checkpoint bytes are written under `.tmp/<uuid>`. On close, the writer checks whether an equal or newer checkpoint already exists; if so it deletes the tmp file. Otherwise it ensures the checkpoint directory exists and renames tmp to `checkpoints/0x0-0x<end>`. Rename failures are cleaned up and rethrown unless another writer already produced the destination.

### State, Persistence, And Dependencies
State includes the journal, UFS, final checkpoint file, tmp URI, and closed flag. Persistence is the committed checkpoint file named by exclusive end sequence. Dependencies include `UnderFileSystem`, `UfsJournalFile`, `UfsJournalSnapshot`, and Java `FilterOutputStream`.

### Integration Points
`UfsJournal.checkpoint()` and `UfsJournalCheckpointThread.writeCheckpoint()` use it when compacting master state.

### Risks
Rename semantics vary by UFS and may not be atomic. Concurrent standby checkpoint writers are handled by destination existence checks, but transient failures can still leave tmp files for GC. Closing twice is a no-op; cancellation after close will not delete a committed file.

### Test Signals
Cover successful commit, newer checkpoint preexistence, mkdir failure, rename failure with and without destination, cancel cleanup, double close/cancel, and checkpoint filename encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalCheckpointWriter.java -->
