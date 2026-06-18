<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/BestEffortLongFile.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/BestEffortLongFile.java

## Purpose
`BestEffortLongFile` stores one long value on disk in binary form without fsync, intended for frequently updated values where exact persistence is not correctness-critical.

## APIs and Types
It implements `Closeable` and exposes constructor `(File, defaultVal)`, `get()`, `set(long)`, and `close()`.

## Control Flow
`get` and `set` call `lazyOpen`. `lazyOpen` reads existing bytes if present, validates exact 8-byte length, decodes with Guava `Longs`, or uses the default. It then opens a `RandomAccessFile` in `rw` mode and stores its channel. `set` rewrites an 8-byte buffer at file position 0 using `IOUtils.writeFully` and updates the cached value.

## State and Persistence
State includes the target file, default value, cached long, lazily opened channel, and reusable 8-byte buffer. Writes are not fsynced and are binary, not textual. The file remains open until `close`.

## Dependencies and Integration
It depends on Hadoop `IOUtils` and shaded Guava `Files`/`Longs`. It complements `PersistentLongFile` where performance matters more than durability.

## Risks
Partial or corrupted files with nonzero non-8-byte length cause `IOException`. No locking protects concurrent processes or threads. The file is not truncated before writing, but fixed 8-byte writes keep valid files at the expected length. Directory creation is not handled.

## Test Signals
Tests should cover absent file default, valid persisted value, invalid length failure, set/get round trip, reopen after close, and behavior when parent directories are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/BestEffortLongFile.java -->
