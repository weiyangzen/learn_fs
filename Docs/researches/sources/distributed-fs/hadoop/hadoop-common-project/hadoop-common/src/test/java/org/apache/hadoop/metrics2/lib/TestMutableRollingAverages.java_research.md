# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/TestMutableRollingAverages.java

## Purpose
Tests `MutableRollingAverages`, including empty rollovers, sliding-window average calculation, metrics-system annotation injection, and thread-local state collection.

## Important APIs, Types, And Functions
Uses `MutableRollingAverages`, `replaceScheduledTask()`, `snapshot()`, `add()`, `collectThreadLocalStates()`, and `getStats()`. `DummyTestMetric` exposes a `@Metric(valueName = "testing")` rolling average registered in `DefaultMetricsSystem`.

## Control Flow
The empty test snapshots before and after a scheduled rollover and verifies no gauges are emitted. The rollover test configures two five-second windows, inserts repeated constant values into successive windows, sleeps past each boundary, and checks the rolling average gauge. The annotation test registers a source, adds two named metrics, waits until thread-local stats are collected, then reads gauges from the metrics system.

## State And Persistence Behavior
Rolling average state is held in scheduled window buckets plus thread-local accumulators. Try-with-resources closes `MutableRollingAverages` in direct tests, which is important because it owns scheduled rollover work. The default metrics system registration persists during the test and may affect subsequent tests if not isolated.

## Dependencies And Integration Points
Integrates with metrics2 annotations, `DefaultMetricsSystem`, `GenericTestUtils.waitFor`, Hadoop `Time`, and mocked `MetricsRecordBuilder`.

## Risks
Timing is the main risk: tests sleep around five-second and one-second windows. Failure to collect thread-local state would make `getStats()` empty even when samples were added. Metric names include bracketed, capitalized sample names such as `[Foo2]RollingAvgTime`.

## Test Signals
Expected signals include no gauges for empty windows, rolling averages of 1.0/1.5/2.5 over two windows, and registered gauges `[Metric1]RollingAvgTesting=500.0` and `[Metric2]RollingAvgTesting=1000.0`.
