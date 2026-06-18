# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/InstrumentedReadLock.java

## Purpose

`InstrumentedReadLock` adapts `InstrumentedLock` for `ReentrantReadWriteLock.ReadLock`, where multiple threads may hold the read lock simultaneously.

## Important APIs, Types, And Functions

The constructor wraps `readWriteLock.readLock()`. It overrides `unlock()` and `startLockTiming()`. A `ThreadLocal<Long>` records the first read-lock acquisition timestamp for each holding thread.

## Control Flow, State, And Persistence

On first read hold per thread, `startLockTiming()` stores the monotonic timestamp. `unlock()` checks whether the thread's read hold count is about to drop to zero, then unlocks, removes the thread-local, and calls `check()` for held time. State is per-thread timing plus the underlying read-write lock.

## Dependencies And Integration Points

It depends on `ReentrantReadWriteLock`, `InstrumentedLock`, `Timer`, and SLF4J. It is created by `InstrumentedReadWriteLock`.

## Risks And Test Signals

Thread-local cleanup only occurs when hold count reaches zero, so unbalanced locking leaks thread-local state until thread death. Tests should cover reentrant read locking, concurrent readers, threshold logging on final unlock only, and interruption-free delegation.
