# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestInstrumentedLock.java

Purpose: validates `InstrumentedLock`, a wrapper around `Lock` that preserves mutual exclusion while logging long hold and wait times with suppression statistics.

Important APIs and types: `InstrumentedLock`, `AutoCloseableLock`, `Timer`, `SuppressedSnapshot`, `ReentrantLock`, `SubjectInheritingThread`, and overridden `logWarning`/`logWaitWarning` hooks.

Control flow: one test proves a competing thread cannot `tryLock` while the lock is held. Another wraps the lock in `AutoCloseableLock` and verifies try-with-resources acquisition/release updates thread-local ownership. Hold-time reporting uses a fake monotonic timer and mocked lock to trigger below-threshold, first warning, suppressed warning, and later warning-with-suppressed-count cases. Wait-time reporting uses a fair `ReentrantLock`, a blocking competitor, and timer advances to exercise the same suppression window.

State and persistence: lock ownership is transient; test-visible state is held in atomics recording warning count, suppressed count, max suppressed wait, and current owner thread.

Dependencies and integration points: integrates Java concurrency locks, Hadoop timer abstraction, logging throttling, and subject-inheriting test threads.

Risks: logging on every unlock, missing wait warnings, incorrect suppression counters, or broken try-with-resources release would create noisy or unsafe synchronization behavior. Test signals use timed JUnit tests, fake time, and competing threads.
