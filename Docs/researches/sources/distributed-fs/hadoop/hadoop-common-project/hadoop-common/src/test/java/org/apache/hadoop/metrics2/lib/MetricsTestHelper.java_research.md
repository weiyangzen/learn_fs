# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/MetricsTestHelper.java

## Purpose

`MetricsTestHelper` exposes package-private metrics behavior to tests, specifically replacing the scheduled rolling window task in `MutableRollingAverages`.

## Important APIs, Types, And Functions

The class is `final` with a private constructor, a logger, and static `replaceRollingAveragesScheduler(MutableRollingAverages, int numWindows, long interval, TimeUnit)`, which delegates to `mutableRollingAverages.replaceScheduledTask(...)`.

## Control Flow

Tests call the helper with a mutable rolling-averages metric and desired window parameters. The helper performs no validation and directly invokes the package-private method.

## State And Persistence Behavior

State changes occur inside the supplied `MutableRollingAverages`, replacing its scheduler/task configuration. No state is stored in the helper and no persistence is written.

## Dependencies And Integration Points

It integrates with `MutableRollingAverages` and Java `TimeUnit`. It is a test-only bridge around encapsulation for metrics rolling average timing.

## Risks And Test Signals

Risks include misuse with invalid window/interval values and hidden scheduler resource leaks in callers. Signals come from downstream rolling-average tests that can deterministically shrink scheduling windows through this helper.
