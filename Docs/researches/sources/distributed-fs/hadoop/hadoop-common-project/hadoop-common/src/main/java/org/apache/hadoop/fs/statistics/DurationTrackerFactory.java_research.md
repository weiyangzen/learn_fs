# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/DurationTrackerFactory.java

Purpose: interface for objects that create `DurationTracker` instances for named operations.

Important APIs and types: default `trackDuration(String key, long count)` and overload `trackDuration(String key)`.

Control flow: default `trackDuration(key,count)` returns `IOStatisticsSupport.stubDurationTracker()`, allowing callers to instrument code without requiring a concrete statistics implementation. The one-argument overload delegates with count 1.

State and persistence: interface has no state. Concrete factories update statistics through trackers on close.

Dependencies and integration: used by filesystem/store code to instrument operations; imports `stubDurationTracker`.

Risks: default stub silently records nothing, so code must be wired with a real factory for metrics. Count semantics depend on implementation. Null or empty keys are not validated at interface level.

Test signals: cover default stub no-op behavior, one-arg delegation count, concrete implementation count handling, null/empty key policy, and try-with-resources usage.
