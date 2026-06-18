# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AIOStatisticsContext.java

Purpose: Tests thread-level `IOStatisticsContext` aggregation for S3A input streams, output streams, listing operations, context sharing, and task-pool execution.

Important APIs/types/functions: `IOStatisticsContext`, `IOStatisticsContextIntegration.enableIOStatisticsContext()`, `getCurrentIOStatisticsContext()`, `getThreadSpecificIOStatisticsContext()`, `setThreadIOStatisticsContext()`, `StreamCapabilities.IOSTATISTICS_CONTEXT`, `HadoopExecutors`, `SubjectInheritingThread`, `TaskPool`, and counters `STREAM_READ_BYTES`, `STREAM_WRITE_BYTES`, `OBJECT_LIST_REQUEST`.

Control flow: configuration disables prefetching and forces classic streams for deterministic stream statistics. Tests run read/write workloads in multiple executor threads, reset contexts, assert per-thread byte counters, verify context IDs and thread IDs, share a context into a worker thread, set null context to force a new context, and verify list operations update the current context both directly and through `TaskPool`.

State and persistence: maintains an executor per test, worker exceptions through inherited future-exception fields, and global/thread-local IO statistics contexts. Writes small S3 objects for read/write tests.

Dependencies and integration points: S3A stream capabilities, block output stream, classic input stream, listing iterators, Hadoop task-pool context propagation, and thread-local statistics implementation.

Risks: thread scheduling and context inheritance can be order-sensitive; prefetching is disabled because it would alter counters; context is global/thread-local and can leak between tests if not reset.

Test signals: verifies both stream-level and filesystem/listing statistics are attributed to the correct thread or explicitly shared context.
