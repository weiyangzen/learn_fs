# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/AsyncJournalWriter.java

## Purpose
This legacy `journalv0` `AsyncJournalWriter` provides asynchronous append accounting and batched flushing on top of a synchronous `JournalWriter`. It lets callers append entries, receive a monotonically increasing counter, and later wait until that counter has been flushed.

## Important APIs, Types, and Functions
The class exposes `appendEntry(JournalEntry)` and `flush(long)`. It stores a `JournalWriter`, a `ConcurrentLinkedQueue<JournalEntry>`, atomic counters for appended, written, and flushed entries, a flush batch duration derived from `MASTER_JOURNAL_FLUSH_BATCH_TIME_MS`, and a fair `ReentrantLock` protecting actual writes and flushes.

## Control Flow, State, and Persistence
`appendEntry()` increments `mCounter` before enqueueing, then returns the current counter after enqueueing. This preserves the invariant that the returned counter is at least the entry's position even without an append lock. `flush(targetCounter)` returns immediately if the target is already flushed, otherwise it takes `mFlushLock`, drains queued entries through `mJournalWriter.write()`, updates `mWriteCounter`, optionally continues past the target within the configured batch window, then calls `mJournalWriter.flush()` and advances `mFlushCounter`.

Persistence is delegated to the underlying writer; this class only orders and batches writes. If a write throws, the queue head is left in place because it is polled only after a successful write. If flush throws, `mFlushCounter` is not advanced, so later flush calls retry.

## Dependencies and Integration Points
It depends on the legacy protobuf `JournalEntry`, `JournalWriter`, Alluxio configuration, Guava `Preconditions`, atomics, concurrent queues, and locks. It is the asynchronous facade used by legacy journal writers to amortize flush overhead while preserving caller-visible durability counters.

## Risks and Test Signals
Risks include an unbounded queue, contention around the fair flush lock, repeated retries of a permanently failing head entry, and reliance on caller discipline to flush returned counters. Signals are append counter monotonicity, no lost entries after write failure, no flush-counter advancement after flush failure, batch-window throughput, and concurrent append/flush ordering tests.
