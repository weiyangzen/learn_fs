# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/MasterJournalContext.java

## Purpose
`MasterJournalContext` is the standard durable journal context for master state changes.

## Important APIs, Types, And Functions
`append` enqueues entries through `AsyncJournalWriter` and records the returned flush counter. `flush` and `close` call `waitForJournalFlush`, which retries until the configured timeout, maps closed/not-leader conditions to `UnavailableException`, logs retryable failures, and fatal-errors on unexpected or exhausted failures.

## Control Flow, State, Dependencies, Risks, And Tests
State is the last flush counter for this context. Persistence occurs when the async writer flushes through its backend. Dependencies include `AsyncJournalWriter`, `TimeoutRetry`, `ProcessUtils`, Ratis `NotLeaderException`, and journal flush configuration. Risks include only tracking the last append counter, fatal process exits after timeout, memory mutation preceding journal durability, and cancellation being logged but not cancelling partial writes. Tests should cover no-op flush, append/close durability, retry loops, not-leader mapping, timeout fatal path, and concurrent append synchronization.
