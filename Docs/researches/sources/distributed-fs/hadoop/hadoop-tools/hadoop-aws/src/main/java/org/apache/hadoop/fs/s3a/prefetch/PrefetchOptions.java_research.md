<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/PrefetchOptions.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/PrefetchOptions.java

Purpose: immutable holder for prefetch block size and prefetch queue depth.

Important APIs/types/functions: constructor validates `prefetchBlockSize > 0` and `prefetchBlockCount > 0`; getters expose both values.

Control flow: `PrefetchingInputStreamFactory` builds this once during service init and passes it into every `S3APrefetchingInputStream`.

State/persistence: final in-memory values only. No persistence or mutability.

Dependencies/integration: uses Hadoop `Preconditions.checkArgument`; consumed by prefetch stream constructors and block manager setup.

Risks/test signals: bad config values fail early. Tests should cover zero/negative rejection and propagation of configured values into in-memory versus caching stream decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/PrefetchOptions.java -->
