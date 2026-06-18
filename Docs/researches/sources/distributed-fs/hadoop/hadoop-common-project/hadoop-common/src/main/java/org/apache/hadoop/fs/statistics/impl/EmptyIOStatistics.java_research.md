# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/EmptyIOStatistics.java

Purpose: singleton immutable no-data IOStatistics implementation for callers that want to return non-null statistics.

Important APIs, types, and functions: map accessors return `Collections.emptyMap()` for every statistic category; static `getInstance()` returns the singleton.

Control flow: all calls are immediate no-ops/read-only empty map returns.

State and persistence: no mutable state. Singleton lifetime is process-wide.

Dependencies and integration points: extends `AbstractIOStatisticsImpl`; exposed through `IOStatisticsBinding.emptyStatistics()`.

Risks and test signals: returned empty maps are immutable, so mutation attempts should fail. Tests should cover singleton identity, empty string rendering, and safe use where nullable statistics used to be returned.
