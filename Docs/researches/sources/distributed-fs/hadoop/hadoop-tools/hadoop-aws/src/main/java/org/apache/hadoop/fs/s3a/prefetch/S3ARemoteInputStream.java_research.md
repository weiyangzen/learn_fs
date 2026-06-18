<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ARemoteInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ARemoteInputStream.java

Purpose: abstract base `InputStream` for prefetch remote streams. It implements common seek/read/close/statistics behavior while subclasses decide how to ensure a current buffer.

Important APIs/types/functions: constructor creates `ChangeTracker`, records input policy/readahead, builds `BlockData`, `FilePosition`, `S3ARemoteObject`, and `S3ARemoteObjectReader`. Public APIs include `getIOStatistics()`, `getS3AStreamStatistics()`, `setReadahead()`, `hasCapability()`, `available()`, `getPos()`, `seek()`, `read()`, `read(byte[],int,int)`, `close()`, `markSupported()`, and unsupported `mark/reset/skip`. Protected helpers expose file, reader, attributes, position, block data, context, and offset formatting.

Control flow: reads check close/EOF, call subclass `ensureCurrentBuffer()`, copy bytes from `FilePosition.buffer()`, advance `nextReadPos`, and update stream/filesystem byte counters. Seek is lazy and only changes `nextReadPos`; the next read moves buffers.

State/persistence: maintains volatile `closed`, current file position, next-read offset, block metadata, callbacks, remote object, reader, change tracker, input policy, and IO statistics. Close releases references, closes reader and callbacks, invalidates file position, and closes statistics.

Dependencies/integration: depends on S3A read context, object attributes, callbacks, change detection policy, Hadoop prefetch `BlockData`/`FilePosition`, and IOStatistics.

Risks/test signals: buffer position and `nextReadPos` must remain consistent across partial reads and seeks. Tests should cover EOF, negative/past-EOF seek, available behavior, byte/stat counters, close idempotence, and subclass buffer transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ARemoteInputStream.java -->
