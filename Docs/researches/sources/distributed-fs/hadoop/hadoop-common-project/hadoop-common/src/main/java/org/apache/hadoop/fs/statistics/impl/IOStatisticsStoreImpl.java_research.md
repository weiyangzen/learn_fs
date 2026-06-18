# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsStoreImpl.java

Purpose: concrete thread-safe-ish mutable IOStatistics store backed by concurrent maps of `AtomicLong` values and synchronized `MeanStatistic` instances.

Important APIs, types, and functions: constructor from key lists; setters/increments for counters, gauges, minimums, and maximums; min/max sample update; mean setters/samples; `reset()`, `aggregate()`, atomic reference getters, `addTimedOperation()`, and `trackDuration()`.

Control flow: construction creates atomics for registered keys and builds a dynamic statistics wrapper over those atomics. Updates for unknown keys are no-ops except reference getters, which throw. Counter increments ignore negative values. `aggregate()` folds source values into registered entries only; gauges add positive values; min/max use aggregation helpers; means add samples. `trackDuration()` creates a `StatisticDurationTracker` only if the counter key is registered.

State and persistence: in-memory maps hold mutable atomics and means. Exposed IOStatistics is live via `WrappedIOStatistics`; snapshots are required for durable copies.

Dependencies and integration points: depends on `DynamicIOStatisticsBuilder`, `IOStatisticsBinding`, `StatisticDurationTracker`, `MeanStatistic`, `Duration`, and store suffix constants. Used as the primary mutable metrics store for Hadoop filesystem code.

Risks and test signals: `reset()` sets min/max atomics to zero rather than the unset sentinel used at construction, which can affect later min/max aggregation semantics. The minimum aggregation path calls `aggregateMaximums()` before `aggregateMinimums()`, which is suspicious but usually overwritten by the second set. Tests should cover reset sentinel behavior, negative counters, positive-only gauge aggregation, concurrent min/max CAS updates, unknown key handling, and duration tracker failure metrics.
