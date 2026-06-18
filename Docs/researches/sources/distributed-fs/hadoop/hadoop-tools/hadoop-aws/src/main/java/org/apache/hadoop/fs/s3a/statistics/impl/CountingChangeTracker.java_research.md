<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/CountingChangeTracker.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/CountingChangeTracker.java

Purpose: simple `ChangeTrackerStatistics` implementation backed by an `AtomicLong`.

Important APIs/types/functions: constructors accept an existing `AtomicLong` or allocate one. `versionMismatchError()` increments the counter. `getVersionMismatches()` returns the current value.

Control flow: change tracking code calls the increment method on mismatch; diagnostics read the count.

State/persistence: in-memory atomic counter only. Thread-safe increments.

Dependencies/integration: implements `ChangeTrackerStatistics`; used by empty/no-op stats and can be embedded in stream statistics.

Risks/test signals: low risk. Tests should verify external counter sharing, default zero value, increments, and thread-safe behavior if concurrent change checks are possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/CountingChangeTracker.java -->
