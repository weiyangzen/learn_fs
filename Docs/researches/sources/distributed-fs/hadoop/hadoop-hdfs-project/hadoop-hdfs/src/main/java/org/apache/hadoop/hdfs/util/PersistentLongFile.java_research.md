<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/PersistentLongFile.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/PersistentLongFile.java

## Purpose
`PersistentLongFile` stores one long value as text in a file, updating it atomically and durably through `AtomicFileOutputStream`.

## APIs and Types
The class exposes constructor `(File, defaultVal)`, `get()`, `set(long)`, and static `writeFile`/`readFile` helpers.

## Control Flow
`get` lazily loads once from `readFile`, defaulting when the file does not exist. `set` writes only if the cached value differs or has not been loaded, then updates the cache. `writeFile` writes decimal text plus newline through `AtomicFileOutputStream`, aborting in finally if close did not complete. `readFile` parses the first line as a long and wraps number format errors as `IOException`.

## State and Persistence
State is file, default value, cached long, and loaded flag. Persistence is textual and intended durable because the atomic stream flushes and forces file contents before rename.

## Dependencies and Integration
It depends on `AtomicFileOutputStream`, Hadoop `IOUtils`, and SLF4J. It contrasts with `BestEffortLongFile` for correctness-critical values.

## Risks
No synchronization protects concurrent callers. Parent directory creation is not handled. A malformed existing file causes hard failure rather than defaulting. Atomic stream limitations, such as no parent-directory fsync and shared `.tmp` path, apply here.

## Test Signals
Tests should cover absent file default, read existing value, set/write/reopen, no rewrite for same loaded value if observable, malformed file failure, abort cleanup on injected write failure, and concurrent write expectations if documented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/PersistentLongFile.java -->
