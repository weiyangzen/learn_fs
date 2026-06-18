# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/InstrumentedLock.java

## Purpose

`InstrumentedLock` wraps a `Lock` to detect long wait times and long held times, logging throttled warnings with suppressed-message statistics.

## Important APIs, Types, And Functions

It implements `Lock`: `lock()`, `lockInterruptibly()`, `tryLock()`, timed `tryLock()`, `unlock()`, and `newCondition()`. Timing hooks are `startLockTiming()` and `check(acquireTime, releaseTime, isLockHeld)`. Supporting types `SuppressedStats` and `SuppressedSnapshot` track throttled warning counts and max suppressed waits.

## Control Flow, State, And Persistence

Acquisition methods record wait start, delegate to the wrapped lock, check wait duration, then store acquire time. `unlock()` delegates and checks held duration. `check()` compares duration to threshold and uses atomic timestamps to throttle logs by `minLoggingGap`; otherwise it increments suppressed stats. State is per-wrapper timing counters, atomics, wrapped lock state, and logger output only.

## Dependencies And Integration Points

It depends on `java.util.concurrent.locks`, Hadoop `Timer`, `VisibleForTesting`, and SLF4J. Services wrap hot locks with it to diagnose stalls without changing lock callers.

## Risks And Test Signals

Non-reentrant or externally shared locks can make one acquire timestamp insufficient for unusual patterns; read locks are handled by a subclass. Tests should use fake timers to cover wait warnings, hold warnings, throttling, suppressed snapshots, interruptible and timed paths, and condition delegation.
