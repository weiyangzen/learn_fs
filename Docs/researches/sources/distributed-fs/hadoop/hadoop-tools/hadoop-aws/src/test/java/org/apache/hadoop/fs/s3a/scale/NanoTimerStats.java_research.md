<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/NanoTimerStats.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/NanoTimerStats.java


## Purpose
Small mutable utility that aggregates ContractTestUtils.NanoTimer durations using Welford's online variance algorithm.


## Important APIs, Types, and Functions
NanoTimerStats constructors, add(NanoTimer), add(long), reset(), getters, getVariance(), getDeviation(), toSeconds(), and toString(). It tracks operation, count, sum, min, max, mean, and m2.


## Control Flow
Callers add elapsed nanosecond values; each sample updates count/sum/mean/variance state online. reset() clears all values and toString() formats totals and descriptive statistics in seconds.


## State and Persistence Behavior
All state is in instance fields and is explicitly not synchronized. The copy constructor snapshots values from another instance.


## Dependencies and Integration Points
Depends only on ContractTestUtils.NanoTimer and standard math/formatting.


## Risks and Test Signals
Risks are non-thread-safe use and edge cases: getVariance() returns NaN for zero samples but divides by count-1 for count=1, yielding NaN through IEEE arithmetic. Test signal is primarily consumers' timing output, not direct assertions here.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/NanoTimerStats.java -->
