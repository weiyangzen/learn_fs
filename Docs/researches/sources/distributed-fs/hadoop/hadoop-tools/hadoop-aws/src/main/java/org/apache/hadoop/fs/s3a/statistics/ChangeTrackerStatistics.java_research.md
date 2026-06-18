<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/ChangeTrackerStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/ChangeTrackerStatistics.java

Purpose: minimal statistics contract for object version/change tracking.

Important APIs/types/functions: `versionMismatchError()` increments mismatch count; `getVersionMismatches()` returns the accumulated mismatch count.

Control flow: `ChangeTracker` calls this when object version or ETag policies detect a mismatch during reads.

State/persistence: interface only. Implementations typically maintain an in-memory counter.

Dependencies/integration: consumed by `S3AInputStreamStatistics.getChangeTrackerStatistics()` and `CountingChangeTracker`.

Risks/test signals: mismatch counters are important diagnostics for consistency failures. Tests should verify increments and propagation through stream statistics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/ChangeTrackerStatistics.java -->
