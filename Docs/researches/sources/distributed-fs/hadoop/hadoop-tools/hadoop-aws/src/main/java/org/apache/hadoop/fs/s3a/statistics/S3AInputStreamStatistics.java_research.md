<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/S3AInputStreamStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/S3AInputStreamStatistics.java

Purpose: comprehensive statistics contract for S3A input streams, including classic, analytics, and prefetch reads.

Important APIs/types/functions: extends `AutoCloseable`, `S3AStatisticInterface`, and `ChangeTrackerStatistics` integration. Methods record seeks, stream opens/closes, read exceptions, bytes read, read/readFully/vectored starts and completions, discarded vectored bytes, GET/HEAD requests, prefetch bytes, footer parse failure, cache hits, input policy, unbuffering, prefetch operations, file-cache block events, executor acquisition, memory allocation/free, close/open/read counters, policy counters, change tracker stats, and duration trackers for GET and inner stream close.

Control flow: input streams call this at every lifecycle, request, seek, and buffer/prefetch event. Consumers can retrieve `IOStatistics` for reporting.

State/persistence: interface only. Implementations hold live counters/gauges/durations for a stream and may roll them into filesystem-level stats on close.

Dependencies/integration: used throughout S3A read paths, including prefetch streams and `S3ARemoteObject`.

Risks/test signals: high fan-out API means omissions are easy during new read implementations. Tests should cover close accounting, read/seeks, cache/prefetch events, vectored reads, change mismatch, and duration trackers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/S3AInputStreamStatistics.java -->
