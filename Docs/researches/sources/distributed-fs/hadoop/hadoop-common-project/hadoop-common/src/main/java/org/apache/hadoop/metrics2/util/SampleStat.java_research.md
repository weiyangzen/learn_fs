<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/SampleStat.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/SampleStat.java

## Purpose
`SampleStat` computes running sample count, total, mean, variance, standard deviation, min, and max for metrics that aggregate observations.

## Important APIs and Types
The class exposes `reset`, `copyTo`, `add(double)`, `add(long, double)`, `numSamples`, `total`, `mean`, `variance`, `stddev`, `min`, `max`, and `toString`. Nested public `MinMax` tracks minimum and maximum.

## Control Flow
Single-sample `add` updates min/max then delegates to weighted add. Weighted add updates sample count and applies a weighted incremental Welford variance algorithm using `xTotal / nSamples`. Accessors return zero mean/variance for insufficient samples.

## State and Persistence
State is mutable in memory: sample count, mean, variance accumulator `s`, and min/max. There is no synchronization.

## Dependencies and Integration Points
Mutable metrics such as rates and stats use this to compute snapshot values without storing raw samples. Ganglia-related comments explain why `MinMax` defaults use float range values.

## Risks and Test Signals
`add(long, double)` does not update min/max and divides by `nSamples`, so callers must not pass zero. `Float.MIN_VALUE` is the smallest positive float, so negative-only samples will update max correctly only after `add` is called, but reset defaults are unusual. Tests should cover Welford accuracy, copy/reset, weighted adds, min/max behavior, negative values, no-sample accessors, and zero-weight rejection by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/SampleStat.java -->
