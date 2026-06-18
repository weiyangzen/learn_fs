# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/statistics/IOStatisticAssertions.java

Purpose: Private unstable test utility class providing common AssertJ-based assertions and serialization helpers for Hadoop `IOStatistics` tests and downstream test suites.

Important APIs/types/functions: lookup helpers for counters/gauges/minimums/maximums/means, `verifyStatisticsNotNull`, `verifyStatistic*Value`, `verifyStatisticCounterValues`, fluent `assertThatStatistic*`, `assertDurationRange`, `assertThatStatisticMeanMatches`, `assertStatisticCounterIsTracked/Untracked`, `assertIsStatisticsSource`, `extractStatistics`, `statisticsJavaRoundTrip`, and inner `RestrictedInput`.

Control flow: Public lookup/assert methods first verify the `IOStatistics` reference is non-null, choose the relevant map, require the key to exist, then assert value equality or return an AssertJ assertion chain. Tracking helpers assert `containsKey`. Source helpers assert `IOStatisticsSource` implementation and non-null returned stats. `statisticsJavaRoundTrip` serializes a `Serializable` statistics object through `ObjectOutputStream`, then reads it through `RestrictedInput`, whose `resolveClass` allows only classes listed by `IOStatisticsSnapshot.requiredSerializationClasses()`.

State/persistence: Stateless static utility; round trips use in-memory byte arrays. No global mutation.

Dependencies/integration: Centralizes assertions for `IOStatistics`, `IOStatisticsSource`, `MeanStatistic`, `StoreStatisticNames` suffixes, Java serialization, and AssertJ diagnostics. The restricted deserialization helper is a security-oriented test integration point.

Risks: The type label `MAXIMUM` is misspelled as `Maxiumum` in descriptions only. Restricted deserialization depends on the required class list staying complete. Lookup methods fail if stats implementations expose lazily evaluated maps that throw on access.

Test signals: This file is itself a support API rather than a test class; downstream tests rely on its assertion failures, fluent chains, and secure serialization round-trip behavior.
