# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalWriter.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalWriter.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalWriter.java

### Purpose
`RaftJournalWriter` assigns global sequence numbers to primary-side journal entries, batches them into an aggregate `JournalEntry`, and flushes the batch to Ratis.

### Important APIs, Types, And Functions
It implements `JournalWriter` with `write()`, `flush()`, `close()`, and `getNextSequenceNumberToWrite()`. It tracks `mNextSequenceNumberToWrite`, last submitted/committed sequence numbers, an aggregate `JournalEntry.Builder`, current serialized size, and the owned `RaftJournalAppender`.

### Control Flow
`write()` rejects closed writers and multi-field entries, flushes if the current batch exceeds one third of the Ratis max entry size, sets the next sequence number on the entry, and appends it to the batch. `flush()` sends the whole batch as one Ratis `Message`, waits for the configured timeout, checks the Ratis reply exception, records committed sequence, and clears the batch.

### State, Persistence, And Dependencies
Sequence assignment is in-memory; persistence is Ratis log replication via `RaftJournalAppender`. Dependencies include Alluxio `JournalWriter`, protobuf `JournalEntry`, Ratis `Message`/reply, configuration limits, and `UnsafeByteOperations`.

### Integration Points
`RaftJournalSystem.gainPrimacy()` creates this writer after catch-up and wraps it with `AsyncJournalWriter` for all `RaftJournal` contexts. `JournalStateMachine` de-duplicates retried flushes by sequence number.

### Risks
Flush retry can submit duplicate batches, requiring replay de-duplication to stay correct. A single oversized entry is only logged as an error before still entering the batch. Timeout and Ratis exceptions are surfaced as `IOException`, potentially leaving the same batch for retry. The class is not thread-safe and relies on async-writer serialization.

### Test Signals
Test sequence assignment, batch aggregation, automatic flush threshold, empty flush, timeout/exception propagation, duplicate flush retry behavior, close idempotence, writer start sequence after primacy, and oversized-entry logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalWriter.java -->
