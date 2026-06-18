<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/FakeTimer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/FakeTimer.java

## Purpose

`FakeTimer.java` is a test timer implementation whose wall-clock and monotonic time can be advanced manually.

## Important APIs, Types, and Functions

It extends `Timer`, stores `now` and `nowNanos`, and overrides `now`, `monotonicNow`, and `monotonicNowNanos`. Constructors initialize from current time or a supplied millisecond value. `advance(long)` and `advanceNanos(long)` move time forward.

## Control Flow

Callers read the fake time through normal `Timer` methods, then advance milliseconds or nanoseconds between assertions to simulate expiry, scheduling, and timeout behavior.

## State and Persistence Behavior

All state is mutable in-memory time counters. Advancing milliseconds also advances nanoseconds by converting with `TimeUnit.MILLISECONDS.toNanos`.

## Dependencies and Integration Points

It integrates with Hadoop code that accepts a `Timer`, and uses Hadoop classification annotations plus `TimeUnit`.

## Risks and Edge Cases

It is not synchronized, so concurrent tests can observe races if shared across threads. Negative advances are not visibly guarded in this file and would move time backward if allowed by callers.

## Test Signals

Consumers should assert deterministic timeout/cache behavior by advancing fake time without sleeping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/FakeTimer.java -->
