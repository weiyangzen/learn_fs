<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/QuantileEstimator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/QuantileEstimator.java

## Purpose
`QuantileEstimator` defines the minimal interface for streaming quantile estimators used by Hadoop metrics code.

## Important APIs and Types
The interface declares `insert(long value)`, `snapshot()`, `getCount()`, and `clear()`. `snapshot` returns a map from configured `Quantile` targets to estimated long values.

## Control Flow
There is no implementation flow here. Implementations define insertion, estimation, and reset behavior. `SampleQuantiles` is the implementation in this group.

## State and Persistence
State is implementation-defined. The interface implies estimators track a count and mutable stream summary that can be cleared.

## Dependencies and Integration Points
Metrics classes can depend on this abstraction instead of a concrete estimator. It uses Java `Map` and the local `Quantile` type.

## Risks and Test Signals
The interface does not specify null versus empty map semantics for an empty estimator, thread safety, snapshot clearing behavior, or error guarantees. Tests should be written against concrete implementations and should document those behavioral choices for callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/QuantileEstimator.java -->
