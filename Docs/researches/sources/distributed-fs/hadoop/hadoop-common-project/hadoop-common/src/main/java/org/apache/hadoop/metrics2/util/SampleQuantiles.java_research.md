<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/SampleQuantiles.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/SampleQuantiles.java

## Purpose
`SampleQuantiles` implements the CKMS/GK-style streaming estimator for targeted high-percentile approximate quantiles used by metrics histograms and latency tracking.

## Important APIs and Types
It implements `QuantileEstimator`. Public synchronized APIs are `insert`, `snapshot`, `getCount`, `clear`, test-visible `getSampleCount`, and `toString`. Internal `SampleItem` stores a sampled value, lower-rank delta `g`, and rank error `delta`.

## Control Flow
`insert` appends values to a 500-slot buffer, increments the total count, and when full, sorts and merges the batch into the ordered sample list before compression. `allowableError` computes the CKMS bound for a rank across configured quantiles. `compress` merges adjacent samples whose combined rank gap remains within error. `snapshot` flushes the buffer, returns null when empty, and queries each target quantile by scanning rank ranges.

## State and Persistence
State is in-memory: total count, ordered sample list, insertion buffer, buffer count, and configured quantiles. Methods that mutate or read estimator state are synchronized.

## Dependencies and Integration Points
Metrics code uses this through `QuantileEstimator` to summarize streams without storing every value. It depends on Hadoop `Preconditions`, test annotations, and shaded Guava `Joiner`.

## Risks and Test Signals
Invalid quantile values can divide by zero or produce bad error bounds. `snapshot` mutates state by flushing the buffer. Tests should cover empty snapshot null, monotonic count, exact small streams, buffer flush boundaries, compression reducing samples, target accuracy bounds, clear, toString, and concurrent synchronized access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/SampleQuantiles.java -->
