# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournal.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournal.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournal.java

### Purpose
`UfsJournal` is the legacy under-file-system journal implementation for a single master component. It manages versioned log/checkpoint directories, standby tailing, primary writing, suspend/catch-up, formatting, and checkpoints.

### Important APIs, Types, And Functions
It implements `Journal` with `createJournalContext()`, `getLocation()`, and `close()`. Lifecycle methods include `start()`, `gainPrimacy()`, `signalLosePrimacy()`, `awaitLosePrimacy()`, `suspend()`, `catchup()`, `resume()`, `checkpoint()`, `format()`, and reader/writer factory methods. The inner `UfsJournalCatchupThread` replays a bounded sequence range while suspended.

### Control Flow
Standby start resets master state and starts `UfsJournalCheckpointThread`. Gaining primacy waits for tailer shutdown and quiet period, catches up remaining entries, creates `UfsJournalLogWriter`, wraps it in `AsyncJournalWriter`, and switches to primary. Losing primacy first blocks new writes, then closes writers, resets state, and restarts tailing. Replay reads checkpoints and logs, applies entries, appends sinks, retries I/O for up to a year, and fatal-handles corruption.

### State, Persistence, And Dependencies
Persistent layout is `<base>/v1/logs`, `<base>/v1/checkpoints`, and `<base>/v1/.tmp`, with a format breadcrumb. State includes master, UFS handle, primary/standby/closed state, writer/tailer references, suspension sequence, catch-up flags, checkpoint metrics, and sink supplier. Dependencies include `UnderFileSystem`, `Master`, `UfsJournalReader`, `UfsJournalLogWriter`, checkpoint writer/snapshot helpers, retry policies, and metrics.

### Integration Points
`UfsJournalSystem` creates and coordinates one `UfsJournal` per master. Masters write through `MasterJournalContext`; standbys replay through the checkpoint thread. Backup and journal-system catch-up use suspend/catchup/resume.

### Risks
Primary failover relies on UFS file visibility and quiet-period heuristics. Replay retries I/O nearly indefinitely but crashes on logical gaps or corruption. Suspension stops the tailer and can accumulate unapplied entries until resume. Formatting recursively deletes versioned journal contents. State transitions are synchronized but involve background threads with failure propagation.

### Test Signals
Cover startup replay, primary gain/loss, context unavailability in standby, suspend/catchup/resume ranges, checkpoint no-op and write paths, format breadcrumb, replay retry on I/O, sink append, corrupted entry fatal path, and close during each lifecycle state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournal.java -->
