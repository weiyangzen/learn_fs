# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/OperationCostValidator.java

Purpose: reusable test harness for declarative assertions over S3A instrumentation counters around an operation or expected exception.

Important APIs/types/functions: `OperationCostValidator.builder(S3AFileSystem)` creates a `Builder` with selected metrics or all counters/durations. The validator tracks `S3ATestUtils.MetricDiff` objects for mutable counter metrics from `S3AInstrumentation`, exposes `exec`, `intercepting`, `get`, `resetMetricDiffs`, and static probe builders `always`, `probe`, `probes`, and `expect`. Nested `ExpectedProbe`, `ExpectSingleStatistic`, `ProbeList`, and `EmptyProbe` implement conditional verification.

Control flow: construction filters requested statistics to mutable counters. `exec()` resets diffs, skips the test through AssertJ assumptions if every probe is disabled, executes the callable, logs operation state and IOStatistics, then verifies each enabled probe. `intercepting()` wraps `LambdaTestUtils.intercept` inside `exec()` so exception paths also get metric validation.

State and persistence: stores metric-diff baselines and instrumentation `IOStatistics` references in memory only. It clears builder metric lists after construction.

Dependencies/integration: S3A instrumentation, Hadoop metrics2 `MutableCounter`, `StatisticTypeEnum`, AssertJ assumptions, LambdaTestUtils, and pretty IOStatistics logging.

Risks: non-counter metrics are silently ignored; disabled probes skip execution, which can hide coverage on stores without those metrics; exact counter names must be tracked.

Test signals: downstream tests fail on mismatched metric diffs and log complete instrumentation state for diagnosis.
