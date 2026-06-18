# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/PairedDurationTrackerFactory.java

Purpose: duration tracker factory that forwards one operation lifecycle into two underlying factories, typically local and global statistics.

Important APIs, types, and functions: constructor accepts two factories; `trackDuration()` returns a private paired tracker; paired tracker implements `failed()`, `close()`, `asDuration()`, and `toString()`.

Control flow: `trackDuration()` creates trackers from both delegates. Failure and close are invoked on both. Duration and string output come from the first wrapped tracker, which is created from the global factory in this implementation.

State and persistence: stores two factory references; per-operation tracker stores two duration trackers. No persistence.

Dependencies and integration points: depends on `DurationTrackerFactory` and `DurationTracker`; exposed by `IOStatisticsBinding.pairedTrackerFactory()`.

Risks and test signals: if the first delegate throws during close, the second may not close. Tests should cover ordering, failure propagation to both trackers, duration source selection, null delegate behavior, and close exception handling expectations.
