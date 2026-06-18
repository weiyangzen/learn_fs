# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestInstrumentedReadWriteLock.java

Purpose: tests read/write variants of Hadoop instrumented locks, including exclusivity, shared-read behavior, warning throttling, and reentrant hold accounting.

Important APIs and types: `InstrumentedReadWriteLock`, `InstrumentedReadLock`, `InstrumentedWriteLock`, `AutoCloseableLock`, `ReentrantReadWriteLock`, `Timer`, and `SuppressedSnapshot`.

Control flow: `testWriteLock` holds a write lock and confirms neither competing writers nor readers can acquire. `testReadLock` proves concurrent readers can acquire while writers cannot. Separate hold-report tests use fake monotonic time to verify no warning below threshold, first warning above threshold, suppression inside the log gap, and later warning carrying the suppressed count. Reentrant tests acquire the same read or write lock three times and require only the outermost release to produce one warning with total held time.

State and persistence: no persisted state; relevant state is lock hold count, read/write ownership, fake clock value, and atomic warning counters.

Dependencies and integration points: ties Hadoop's instrumented wrappers to Java `ReentrantReadWriteLock`, try-with-resource adapters, and logging diagnostics used by services.

Risks: incorrectly treating nested reentrant releases as independent holds, allowing writers during reads, blocking concurrent reads, or losing suppression stats. Test signals include timed concurrency checks and exact warning-count/held-time assertions.
