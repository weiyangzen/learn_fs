# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/StubDurationTracker.java

Purpose: singleton no-op `DurationTracker` for disabled or absent duration statistics.

Important APIs, types, and functions: static `STUB_DURATION_TRACKER`, `failed()`, `close()`, and `asDuration()`.

Control flow: failure and close do nothing; duration returns a neutral value.

State and persistence: no mutable state and no persistence.

Dependencies and integration points: used by `IOStatisticsSupport.stubDurationTracker()` and `IOStatisticsBinding.createTracker()` when no factory is supplied.

Risks and test signals: callers must not expect failure or close side effects. Tests should cover singleton identity, no-op methods, and duration value contract.
