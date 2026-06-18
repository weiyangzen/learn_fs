# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/DurationTracker.java

Purpose: contract for objects that track operation duration and update statistics when closed.

Important APIs and types: `failed()`, `close()`, and default `asDuration()`. It extends `AutoCloseable` but narrows `close()` to no checked exception.

Control flow: intended use is try-with-resources. Callers call `failed()` before `close()` when an operation fails; implementations update failure counters and duration metrics. Default `asDuration()` returns `Duration.ZERO` until implementations provide measured duration.

State and persistence: interface has no state; implementations may record start/end times and update external statistics.

Dependencies and integration: paired with `DurationTrackerFactory` and `IOStatistics` implementations.

Risks: callers must remember `failed()` on exceptional paths or failure metrics will be undercounted. Implementations need idempotent close or clear contract for double-close. Default `asDuration()` can hide missing implementation support.

Test signals: implementation tests should cover try-with-resources close, failure marking, double close, exception paths, and `asDuration()` before/after close.
