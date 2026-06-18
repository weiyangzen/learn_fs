<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ARemoteObjectReader.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ARemoteObjectReader.java

Purpose: range-block reader that fills a `ByteBuffer` from an `S3ARemoteObject` with S3A retry/statistics integration.

Important APIs/types/functions: constructor validates `S3ARemoteObject`. `read(ByteBuffer,long,int)` validates buffer, offset, and size, returns -1 if closed, clamps request size to remaining object bytes, then calls `readOneBlockWithRetries()`. `close()` sets a volatile closed flag. `readOneBlockWithRetries()` starts read statistics, invokes retrying `Invoker.retry()`, tracks `STREAM_READ_REMOTE_BLOCK_READ`, handles EOF/socket/IO exceptions, adjusts buffer limit, and records completion. `readOneBlock()` opens the S3 range and copies 64 KiB chunks into the buffer until size is satisfied or closed.

Control flow: a block manager calls `read()` for a block; the reader retries the remote read according to context invoker policy, then updates the buffer for consumers.

State/persistence: owns remote object reference, stream statistics, and a closed flag. No data cache.

Dependencies/integration: integrates with S3A `Invoker`, AWS `ResponseInputStream`, Hadoop IO statistics binding, and `S3ARemoteObject.close()`.

Risks/test signals: the code uses buffer position to compute bytes read and sets limit to that position, so callers must prepare buffer positions correctly. Tests should cover partial object tails, EOF during body read, close during read, retry accounting, and buffer limit/position outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3ARemoteObjectReader.java -->
