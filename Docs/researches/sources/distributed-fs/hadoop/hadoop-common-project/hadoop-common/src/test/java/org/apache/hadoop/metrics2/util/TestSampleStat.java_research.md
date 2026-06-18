# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/util/TestSampleStat.java

## Purpose
Tests `SampleStat` running statistics for empty state, incremental values, min/max, variance/stddev, and reset.

## Important APIs, Types, And Functions
Uses `SampleStat`, `add()`, `reset()`, `numSamples()`, `mean()`, `variance()`, `stddev()`, `min()`, `max()`, and `SampleStat.MinMax` default constants.

## Control Flow
The test asserts initial defaults, adds value 3, checks one-sample statistics, chains `add(2).add(1)`, checks three-sample statistics, resets, and verifies defaults again.

## State And Persistence Behavior
State is in-memory running aggregate data. No persistence.

## Dependencies And Integration Points
`SampleStat` underpins mutable stat metrics where online updates must avoid storing all samples.

## Risks
The test uses a very small epsilon and exact simple values; it validates basic math but not numerical stability for large sample counts or magnitudes.

## Test Signals
Expected sequence includes mean 3 then 2, variance/stddev 0 then 1, min/max 3 then 1/3, and default min/max restored after reset.
