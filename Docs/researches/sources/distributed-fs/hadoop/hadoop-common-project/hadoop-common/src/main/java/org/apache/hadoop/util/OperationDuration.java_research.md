# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/OperationDuration.java

## Purpose

`OperationDuration` is a simple elapsed-time value object used to capture operation duration in milliseconds and format it as human-readable minutes/seconds/milliseconds.

## Important APIs, Types, And Functions

The constructor records start and initial finish time. `finished()` updates the finish timestamp. `value()` returns elapsed milliseconds. `getDurationString()`, `toString()`, and static `humanTime(long)` format values. `asDuration()` returns a `java.time.Duration`.

## Control Flow, State, And Persistence

By default, `value()` is zero until `finished()` is called because start and finish are initialized together. `time()` is protected for test overrides. State is just start and finish timestamps; no persistence.

## Dependencies And Integration Points

It depends on `java.time.Duration` and Hadoop annotations. `DurationInfo` extends it for scoped logging, and other utilities can use it for timing without logging.

## Risks And Test Signals

It uses wall-clock `System.currentTimeMillis()`, so clock adjustments can produce negative or skewed durations. Tests should override `time()` or control timestamps to cover formatting, repeated `finished()` calls, `asDuration()`, and negative/large values.
