# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsAggregator.java

Purpose: public evolving interface for objects that aggregate `IOStatistics` from other sources.

Important APIs and types: single method `aggregate(@Nullable IOStatistics statistics)` returning boolean.

Control flow: callers pass a possibly-null statistics reference. Implementations decide whether to aggregate all categories or selected values and return true only when a non-null reference was aggregated.

State and persistence: interface has no state; implementations maintain aggregate counters/gauges/min/max/means.

Dependencies and integration: used by metrics collectors and composite stream/filesystem classes that merge child statistics.

Risks: aggregation policy is deliberately flexible, so consumers must know implementation semantics. Null handling is part of the contract. Concurrency and idempotence are implementation-specific.

Test signals: cover null input returning false, non-null returning true, selected/all category aggregation, repeated aggregation behavior, mean/min/max combination semantics, and thread safety for concrete implementations.
