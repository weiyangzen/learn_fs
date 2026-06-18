# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/AsyncJournalWriter.java

## Purpose
`AsyncJournalWriter` decouples journal entry appends from durable flushes and batches writes on a dedicated thread.

## Important APIs, Types, And Functions
`appendEntry` enqueues an entry and returns a counter. `flush(targetCounter)` registers a `FlushTicket`, releases the flush thread semaphore, and blocks with ForkJoin managed blocking until the target counter is durable or failed. `close`/`stop` terminate the flush thread. `FlushTicket` wraps `SettableFuture` and error propagation.

## Control Flow, State, Dependencies, Risks, And Tests
The flush thread waits for queued entries or a timeout, writes entries through `JournalWriter`, appends to sinks, flushes the writer and sinks, updates counters, and completes tickets. State includes lock-free queue, counters, ticket set, semaphore, stop flag, and thread. Persistence is through the underlying `JournalWriter`. Dependencies include Alluxio `ForkJoinPoolHelper`, `JournalSink`, metrics, `JournalClosedException`, Ratis `NotLeaderException` pass-through via callers, and config batch timing. Risks include unbounded queue growth, constructor overload setting journal name after thread creation, stop not guaranteeing pending durability, ticket failure after IO errors, and sink side effects coupled to writer success. Tests should cover append/flush ordering, batching, IO failure ticket propagation, close semantics, concurrent flushes, sink append/flush calls, and interruption mapping.
