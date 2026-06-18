# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsStoreBuilderImpl.java

Purpose: concrete builder that collects key declarations and creates `IOStatisticsStoreImpl`.

Important APIs, types, and functions: list fields for counters, gauges, minimums, maximums, and means; fluent `with...` methods; duration-stat helper methods that register `.min`, `.max`, and `.mean` names; `build()`.

Control flow: each declaration appends keys to internal lists. `build()` passes those lists to `IOStatisticsStoreImpl`, which creates atomics and dynamic map bindings.

State and persistence: builder maintains mutable declaration lists. The built store owns runtime metric state; the builder has no persistence.

Dependencies and integration points: depends on store implementation and statistic suffix constants. It is the normal construction path for filesystem statistics stores.

Risks and test signals: duplicate declarations can overwrite map entries during store construction and may hide configuration mistakes. Tests should cover duration key expansion, duplicate behavior, null/empty varargs, and correct map registration after build.
