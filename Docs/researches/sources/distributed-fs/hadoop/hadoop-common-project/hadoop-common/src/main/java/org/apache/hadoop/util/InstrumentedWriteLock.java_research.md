# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/InstrumentedWriteLock.java

## Purpose

`InstrumentedWriteLock` adapts `InstrumentedLock` for `ReentrantReadWriteLock.WriteLock`, including reentrant write-lock timing rules.

## Important APIs, Types, And Functions

The constructor wraps `readWriteLock.writeLock()`. It overrides `unlock()` and `startLockTiming()` to use `ReentrantReadWriteLock.getWriteHoldCount()`.

## Control Flow, State, And Persistence

`startLockTiming()` records timing only on first write hold by the current thread. `unlock()` checks whether the write hold count is about to reach zero, delegates unlock, and only then reports held duration. State is inherited timing plus the shared read-write lock; nothing persists.

## Dependencies And Integration Points

It depends on `InstrumentedLock`, `ReentrantReadWriteLock`, `Timer`, and SLF4J. It is the write-side wrapper returned by `InstrumentedReadWriteLock`.

## Risks And Test Signals

Reentrant write locking should not log intermediate unlocks. Tests should cover nested write locks, final unlock logging, timed acquisition wait logging, and behavior when unlock is called without ownership.
