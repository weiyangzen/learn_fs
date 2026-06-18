<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/Quantile.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/Quantile.java

## Purpose
`Quantile` describes one target quantile and acceptable error bound for the streaming `SampleQuantiles` estimator.

## Important APIs and Types
It is a private comparable class with public final fields `quantile` and `error`. It implements `equals`, `hashCode`, `compareTo`, and `toString`.

## Control Flow
Construction stores the two doubles. Equality compares exact `doubleToLongBits` for both fields. Ordering uses Guava `ComparisonChain` by quantile first and error second. `toString` formats a percent-style description.

## State and Persistence
Instances are immutable and can be used as keys in maps, such as `TreeMap<Quantile, Long>` returned by `SampleQuantiles.snapshot`.

## Dependencies and Integration Points
It integrates with `SampleQuantiles` and `QuantileEstimator` consumers. It depends on Hadoop-shaded Guava for comparison chaining.

## Risks and Test Signals
There is no validation that quantile and error are within sensible ranges, so callers must avoid zero, negative, greater-than-one, or NaN values that can break estimator math. Tests should cover equality bit semantics, ordering, hash stability, string formatting, and invalid-value behavior through `SampleQuantiles`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/Quantile.java -->
