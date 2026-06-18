# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/StopWatch.java

## Purpose
`StopWatch` is a simple closeable monotonic elapsed-time accumulator measured in nanoseconds, with an injectable `Timer` for tests.

## Important APIs, Types, And Functions
Important APIs are constructors, `isRunning`, `start`, `stop`, `reset`, `now(TimeUnit)`, `now()`, `toString`, and `close`. State fields are `timer`, `isStarted`, `startNanos`, and `currentElapsedNanos`.

## Control Flow
`start` rejects already-running watches, records current monotonic time, and marks running. `stop` rejects stopped watches, adds elapsed nanos since `startNanos`, and marks stopped. `reset` clears elapsed time and stops. `now` returns accumulated elapsed plus current running delta when active, or accumulated elapsed when stopped. `close` stops only if running.

## State And Persistence
All state is per-instance memory. There is no synchronization and no persistence.

## Dependencies And Integration Points
It depends on Hadoop `Timer`, Java `TimeUnit`, and `Closeable`. It is useful with try-with-resources for scoped timing.

## Risks
The class is not thread-safe. Time conversion truncates according to `TimeUnit.convert`. Reusing a running watch across `close` silently stops it, while explicit double stop/start misuse throws.

## Test Signals
Tests should use a fake `Timer` to verify start/stop accumulation, reset, running `now`, conversion truncation, `toString`, close behavior, and illegal state exceptions for double start or stop-before-start.
