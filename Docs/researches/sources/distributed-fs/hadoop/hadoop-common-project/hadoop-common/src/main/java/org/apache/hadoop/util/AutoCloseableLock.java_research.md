# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/AutoCloseableLock.java

Purpose: `AutoCloseableLock` wraps a `Lock` so callers can acquire it and release it via try-with-resources.

Important APIs and types: constructors wrap a new `ReentrantLock` or supplied `Lock`. Methods are `acquire`, `release`, `close`, `tryLock`, package-visible/testing `isLocked`, and `newCondition`.

Control flow: `acquire` calls `lock.lock()` and returns `this`; `close` delegates to `release`; `tryLock` returns immediately with lock outcome. `isLocked` only works for `ReentrantLock`, otherwise throws `UnsupportedOperationException`.

State and persistence behavior: stores one lock reference; no persistence.

Dependencies and integration points: integrates with Java `Lock`, `Condition`, and resource-scoped synchronization patterns across Hadoop code.

Risks: callers must only use try-with-resources after a successful `acquire` or `tryLock` that actually acquired the lock. `close` can throw `IllegalMonitorStateException` if the current thread does not hold it. Fairness depends on supplied lock.

Test signals: cover acquire/release with try-with-resources, reentrant acquire, tryLock success/failure, condition creation, `isLocked` for default lock, and unsupported `isLocked` for non-reentrant locks.
