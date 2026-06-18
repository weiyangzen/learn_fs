# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/DynamicIOStatisticsBuilder.java

Purpose: one-shot builder for dynamic IOStatistics backed by functions, atomics, and metrics counters.

Important APIs, types, and functions: `build()`, `withLongFunctionCounter/Gauge/Minimum/Maximum()`, atomic long/int variants, `withMutableCounter()`, and mean-statistic function registration.

Control flow: the builder maintains a single active `DynamicIOStatistics` instance. Every `with...` method obtains the active instance and registers a function; `build()` returns it and nulls the active reference so future use throws `IllegalStateException`.

State and persistence: builder state is transient and invalid after build. Built statistics retain references to supplied atomics/functions and therefore reflect live external state.

Dependencies and integration points: depends on `AtomicLong`, `AtomicInteger`, Hadoop metrics `MutableCounterLong`, and `MeanStatistic`. Used by `IOStatisticsBinding` and `IOStatisticsStoreImpl` to expose atomic maps dynamically.

Risks and test signals: the one-shot lifecycle must be enforced and external function references must remain valid. Tests should cover all source types, post-build failure, live updates from atomics, and evaluator exception behavior.
