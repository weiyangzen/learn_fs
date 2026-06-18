# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/EmptyIOStatisticsStore.java

Purpose: singleton no-op implementation of the mutable `IOStatisticsStore` contract.

Important APIs, types, and functions: all map accessors return empty maps; setters, increments, samples, reset, and aggregate are no-ops; unknown reference getters return no usable statistic references; duration tracking returns a stub tracker.

Control flow: mutation methods either do nothing or return zero/false. Duration methods avoid allocating real operation trackers.

State and persistence: no mutable state and no persistence. Singleton lifetime is process-wide.

Dependencies and integration points: implements `IOStatisticsStore`; exposed through `IOStatisticsBinding.emptyStatisticsStore()`. Used when code requires a non-null store but statistics are disabled or unavailable.

Risks and test signals: code that expects reference getters to succeed must not be passed the empty store. Tests should cover no-op mutations, empty map immutability, aggregate false, and stub duration tracker behavior.
