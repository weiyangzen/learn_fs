# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalReader.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalReader.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalReader.java

### Purpose
`UfsJournalReader` reads UFS journal checkpoints and logs in sequence order, optionally including the current incomplete log for primary catch-up.

### Important APIs, Types, And Functions
It implements `JournalReader` with `advance()`, `getCheckpoint()`, `getEntry()`, `getNextSequenceNumber()`, and `close()`. `updateInputStream()` snapshots available files and opens the next one. `advanceEntry()` enforces sequence continuity. Static `getLastSN()` estimates the final sequence number without parsing entries.

### Control Flow
On advance, the reader may expose the latest checkpoint if it is newer than the current sequence, then queues logs whose end is beyond the checkpoint and current sequence. It skips incomplete logs unless configured. Entry reads accept exact next sequence, skip duplicates below next sequence, and throw on gaps. Truncated completed logs are fatal; incomplete logs may simply end.

### State, Persistence, And Dependencies
State includes next sequence, current `JournalInputStream`, queued `UfsJournalFile`s, checkpoint stream, next entry, read-incomplete flag, and closed flag. It reads but does not modify UFS files. Dependencies include `UfsJournalSnapshot`, `JournalEntryStreamReader`, `CheckpointInputStream`, UFS open options, and `ProcessUtils`.

### Integration Points
Used by standby checkpoint threads, UFS journal catch-up, primary promotion catch-up, and progress estimation.

### Risks
File snapshots are refreshed only when the processing queue is empty, so visibility timing matters. Gaps throw `IllegalStateException`, and truncated completed logs trigger fatal error. Duplicate entries are tolerated to handle rename races and checkpoint overlap. The checkpoint stream is caller-owned after `advance()` returns `CHECKPOINT`.

### Test Signals
Cover no files, latest checkpoint selection, log queue after checkpoint, incomplete-log include/exclude, duplicate skip, gap detection, truncated complete log fatal path, start sequence offsets, close behavior, and `getLastSN()` with listing failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalReader.java -->
