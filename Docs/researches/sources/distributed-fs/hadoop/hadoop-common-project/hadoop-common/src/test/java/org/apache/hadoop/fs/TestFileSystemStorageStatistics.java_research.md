## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileSystemStorageStatistics.java

Purpose: validates `FileSystemStorageStatistics` as an adapter over `FileSystem.Statistics`, including long-statistic iteration, named lookup, distance-bucketed reads, erasure-coded reads, remote read time, and classloader hygiene of the statistics cleaner thread.

Important APIs/types/functions: `FileSystem.Statistics`, `FileSystemStorageStatistics`, `StorageStatistics.LongStatistic`, `getLongStatistics`, `getLong`, `incrementBytesReadByDistance`, `incrementBytesReadErasureCoded`, and `increaseRemoteReadTime`.

Control flow: setup randomly increments multiple statistics. `testGetLongStatistics` iterates all long statistics and compares each value to `getStatisticsValue`. `testGetLong` checks every known key explicitly. `testStatisticsDataReferenceCleanerClassLoader` finds the cleaner thread and asserts its context classloader is null.

State and persistence: all statistics are in memory. Random increments make exact numbers variable, but expected values are computed from the same `FileSystem.Statistics` instance.

Dependencies/integration points: integrates FS operation counters with generic storage-statistics reporting and JVM background cleaner thread behavior.

Risks and test signals: adding/removing statistic keys requires updating the switch or the explicit key list. The cleaner-thread assertion protects against classloader leaks in long-running applications and tests.
