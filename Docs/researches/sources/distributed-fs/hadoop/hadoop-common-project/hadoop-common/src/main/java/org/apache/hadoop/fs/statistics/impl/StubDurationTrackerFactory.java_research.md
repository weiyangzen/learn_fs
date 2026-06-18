# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/StubDurationTrackerFactory.java

Purpose: singleton no-op factory that always returns the stub duration tracker.

Important APIs, types, and functions: static `STUB_DURATION_TRACKER_FACTORY` and `trackDuration()`.

Control flow: any key/count request returns `StubDurationTracker.STUB_DURATION_TRACKER`.

State and persistence: no mutable state and no persistence.

Dependencies and integration points: implements `DurationTrackerFactory`; returned by `IOStatisticsSupport.stubDurationTrackerFactory()`.

Risks and test signals: key and count are intentionally ignored. Tests should cover singleton identity and repeated calls returning the same no-op tracker.
