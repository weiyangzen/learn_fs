# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/statistics/TestEmptyIOStatistics.java

Purpose: Tests behavior of the singleton/empty `IOStatistics` implementation and null-safe statistics logging/wrapping.

Important APIs/types/functions: `IOStatisticsBinding.emptyStatistics`, `IOStatisticsSupport.snapshotIOStatistics`, `IOStatisticAssertions.statisticsJavaRoundTrip`, `IOStatisticsBinding.wrap`, `IOStatisticsLogging.ioStatisticsToString`, `ioStatisticsSourceToString`, and counter assertion helpers.

Control flow: Tests assert unknown counters are untracked, tracked/value assertions on unknown counters throw `AssertionError`, an empty snapshot has no keys before and after Java serialization, empty stats stringify to a nonblank value, wrapping returns the same stats instance, and null sources/statistics stringify to an empty string.

State/persistence: Single final `empty` stats reference; no mutable external state.

Dependencies/integration: Ensures empty stats work with snapshotting, Java serialization, source wrapping, logging, and assertion utilities.

Risks: Exact string content is not checked for non-null empty stats, only nonblank. Null logging behavior is asserted as empty string, so callers may depend on that compatibility.

Test signals: Empty key sets, assertion failures for missing counters, identity preservation through wrap, and null-safe empty string logging.
