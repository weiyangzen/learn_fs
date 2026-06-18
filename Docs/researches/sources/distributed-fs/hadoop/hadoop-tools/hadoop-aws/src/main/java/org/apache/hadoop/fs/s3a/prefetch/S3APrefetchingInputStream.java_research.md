<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3APrefetchingInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3APrefetchingInputStream.java

Purpose: public `ObjectInputStream` wrapper for the prefetch implementation. It selects the in-memory or caching remote stream, synchronizes public stream methods, and preserves statistics access after close.

Important APIs/types/functions: constructor validates `S3ObjectAttributes`, callbacks, and statistics, then chooses `S3AInMemoryInputStream` when file size is within one block and `S3ACachingInputStream` otherwise. Overrides `available()`, `getPos()`, `read()`, `read(byte[],int,int)`, `close()`, `seek()`, `setReadahead()`, `hasCapability()`, `getS3AStreamStatistics()`, `getIOStatistics()`, `seekToNewSource()`, and `markSupported()`.

Control flow: all read/seek/available methods check `isClosed()` then delegate to `inputStream`. Close closes and nulls the delegate, then calls `super.close()`. `getPos()`, `getS3AStreamStatistics()`, and `getIOStatistics()` cache last values so callers can inspect after close.

State/persistence: holds one delegate stream, last read position, cached IO statistics, and cached S3A stream statistics. Underlying delegate may keep memory or local cache state.

Dependencies/integration: integrates `ObjectReadParameters`, `InputStreamType.Prefetch`, S3A stream statistics, Hadoop stream capabilities, and the prefetch remote streams.

Risks/test signals: synchronized methods serialize access but do not make the underlying resources reusable after close. Tests should verify delegate choice, post-close diagnostics, capability reporting, leak finalizer behavior, unsupported mark/new-source behavior, and correct exception on closed stream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3APrefetchingInputStream.java -->
