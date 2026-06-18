# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/DurationStatisticSummary.java

Purpose: serializable summary object for duration statistics extracted from an `IOStatistics` source, intended for reporting and tests.

Important APIs and types: constructor, getters, `toString()`, static `fetchDurationSummary()`, and `fetchSuccessSummary()`. Fields include key, success flag, count, max, min, and cloned nullable `MeanStatistic`.

Control flow: constructor clones mean statistics defensively when present. `fetchDurationSummary()` builds a success or failure key using `StoreStatisticNames.SUFFIX_FAILURES`, reads counter, max, min, and mean entries from the source maps with defaults for missing values, and returns a summary.

State and persistence: immutable final fields, serializable with explicit `serialVersionUID`. No mutation after construction.

Dependencies and integration: uses `IOStatistics`, `MeanStatistic`, nullable annotation, and store statistic suffix constants.

Risks: `getMean()` returns the stored clone directly, so if `MeanStatistic` is mutable consumers may mutate the summary's copy. `toString()` omits `min`. Missing statistics produce count 0 and max/min -1, which callers must treat as incomplete rather than zero-duration.

Test signals: cover success and failure key lookup, missing data defaults, mean clone behavior, serialization, `toString()`, and immutability expectations.
