# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/sink/JournalSink.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/sink/JournalSink.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/sink/JournalSink.java

### Purpose
`JournalSink` is the extension point for consumers that observe journal entries as they are replayed or applied.

### Important APIs, Types, And Functions
It defines one method, `append(JournalEntry entry) throws IOException`, for writing or forwarding a single journal entry.

### Control Flow
There is no implementation flow in the interface. Callers invoke sinks after successful state-machine processing through `JournalUtils.sinkAppend()`.

### State, Persistence, And Dependencies
The interface has no state. Implementations may persist or export entries externally. It depends only on the journal protobuf `JournalEntry` and `IOException`.

### Integration Points
Both `BufferedJournalApplier` and UFS replay paths append entries to configured sinks. `AsyncJournalWriter` also receives sink suppliers in the journal systems, so sink behavior can observe primary writes and standby replay depending on configuration.

### Risks
Sink implementations run in journal application paths, so slow or failing sinks can affect replay/write latency depending on `JournalUtils` handling. Implementations must tolerate duplicate or retried journal entries where upper layers permit them.

### Test Signals
Verify sink append on Raft and UFS replay, behavior when a sink throws `IOException`, ordering across entries, duplicate entry behavior, and configuration with empty sink sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/sink/JournalSink.java -->
