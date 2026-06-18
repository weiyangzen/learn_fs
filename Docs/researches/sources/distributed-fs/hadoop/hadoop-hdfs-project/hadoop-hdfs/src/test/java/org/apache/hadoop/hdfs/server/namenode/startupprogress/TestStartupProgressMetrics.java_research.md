# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/TestStartupProgressMetrics.java

## Purpose
`TestStartupProgressMetrics` verifies the Hadoop metrics projection of `StartupProgress` in initial, running, and final states.

## Important APIs, Types, and Functions
The suite uses `StartupProgress`, `StartupProgressMetrics`, `StartupProgressTestHelper.setStartupProgressForRunningState`, `setStartupProgressForFinalState`, and `MetricsAsserts` helpers including `mockMetricsSystem`, `getMetrics`, `assertCounter`, `assertGauge`, and `getLongCounter`.

## Control Flow
Setup initializes a mocked metrics system, a fresh `StartupProgress`, and a `StartupProgressMetrics` wrapper. `testInitialState` reads metrics and asserts all elapsed/count/total counters and percent gauges are zero. `testRunningState` applies the helper running state and verifies overall percent complete is 0.375, fsimage is complete, edits is half complete, and remaining phases are zero. `testFinalState` applies the helper final state and verifies overall and per-phase percent complete are 1.0 with expected counts and totals.

## State and Persistence Behavior
State is in-memory metrics sampling from the current progress view. There is no persistence or cluster interaction.

## Dependencies and Integration Points
The file integrates the startup progress model with Hadoop metrics2 naming. Metric names such as `LoadingFsImageCount`, `LoadingEditsPercentComplete`, and `SafeModeTotal` are part of the observable contract under test.

## Risks and Edge Cases
Risks include incorrect metric names, counters/gauges swapped, stale sampling, and percentage calculation drift between `StartupProgressView` and metrics serialization. The tests allow elapsed-time counters to be nonnegative rather than exact because timing is runtime-dependent.

## Test Signals
Signals are exact metric counter/gauge assertions for deterministic values and nonnegative elapsed-time checks for active/completed phases.
