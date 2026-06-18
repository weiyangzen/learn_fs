# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/InstrumentedReadWriteLock.java

## Purpose

`InstrumentedReadWriteLock` wraps a `ReentrantReadWriteLock` and exposes instrumented read and write locks through the standard `ReadWriteLock` interface.

## Important APIs, Types, And Functions

The constructor accepts fairness, name, logger, minimum logging gap, and warning threshold. `readLock()` returns an `InstrumentedReadLock`; `writeLock()` returns an `InstrumentedWriteLock`.

## Control Flow, State, And Persistence

Construction creates one underlying `ReentrantReadWriteLock` and two wrappers around its read/write sides. Runtime state is the underlying lock plus wrapper timing counters. There is no persistence.

## Dependencies And Integration Points

It depends on Java read-write locks, `InstrumentedReadLock`, `InstrumentedWriteLock`, and SLF4J. It integrates with services that want lock diagnostics while keeping `ReadWriteLock` APIs.

## Risks And Test Signals

Fairness must match the caller's concurrency expectations. Tests should verify read/write locks share the same underlying lock, fairness propagation, long read/write held logging, and standard `ReadWriteLock` semantics.
