# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/statistics/TestIOStatisticsSnapshot.java

Purpose: Tests `IOStatisticsSnapshot` as a mutable, serializable, JSON-serializable container for all statistic map types.

Important APIs/types/functions: `IOStatisticsSnapshot`, maps `counters/gauges/minimums/meanStatistics`, `MeanStatistic`, `IOStatisticsSnapshot.serializer`, `JsonSerialization`, `IOStatisticAssertions.statisticsJavaRoundTrip`, `IOStatisticsBinding.wrap`, and `verifyDeserializedInstance`.

Control flow: `setup` populates a snapshot with counter `c1`, gauge `g1`, minimum `m1`, and mean statistics `mean0`/`mean1`. Tests verify tracked values, unknown counter assertion failure, logging stringification, `toString` containing key/value pairs, wrap identity, JSON round trip, and Java serialization round trip. `verifyDeserializedInstance` centralizes post-deserialization assertions.

State/persistence: Per-test snapshot object is mutated in setup. Serialization uses in-memory JSON and byte arrays.

Dependencies/integration: Covers snapshot interoperability with JSON serializer, Java serialization, logging, source wrapping, and shared assertion utilities.

Risks: Does not cover maximums in this fixture. `mean0` has zero samples with sum one, preserving empty-mean equality semantics. Stringification tests check only fragments.

Test signals: Exact statistic values after direct access, JSON deserialize, and Java deserialize; assertion failure for unknown key; wrap identity.
