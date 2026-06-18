# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/util/TestSampleQuantiles.java

## Purpose
Tests the `SampleQuantiles` streaming quantile estimator for count tracking, clear/reset, normal quantile error bounds, inverse quantile error bounds, and string formatting.

## Important APIs, Types, And Functions
Uses `SampleQuantiles`, `Quantile`, `insert()`, `snapshot()`, `clear()`, `getCount()`, `getSampleCount()`, and `MutableInverseQuantiles.INVERSE_QUANTILES`.

## Control Flow
Each test initializes an estimator. Count test checks empty snapshot, inserts one value, snapshots, and checks `toString()`. Clear test inserts 1000 values then resets. Error tests build values 1..100000, shuffle them with a fixed seed across ten repeats, insert all values, snapshot, and assert estimates fall within each quantile's allowed absolute error.

## State And Persistence Behavior
Estimator state is an in-memory sampled summary plus total counts. `clear()` must reset both total and sample counts. Snapshots do not write external data.

## Dependencies And Integration Points
Supports `MutableQuantiles` and `MutableInverseQuantiles`, where approximate percentile gauges are emitted from the estimator.

## Risks
The shuffle uses `Arrays.asList(values)` on a primitive `int[]`, which creates a single-element list and therefore does not actually shuffle individual values. The sorted input still exercises estimator bounds, but less broadly than intended. Large insert loops can be CPU-heavy.

## Test Signals
Signals include null snapshot when empty, exact one-value output for all quantiles, zero counts after clear, and estimates between `actual +/- error` for both normal and inverse quantile arrays.
