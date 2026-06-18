<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/AtomicFileOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/AtomicFileOutputStream.java

## Purpose
`AtomicFileOutputStream` writes to `target.tmp`, fsyncs, closes, and then moves the temp file over the target so consumers see either the old complete file or the new complete file.

## APIs and Types
It extends `FilterOutputStream`, with constructor `AtomicFileOutputStream(File)`, override `write(byte[], int, int)`, override `close()`, and `abort()`.

## Control Flow
Construction opens `f.getName() + ".tmp"` in the same parent directory. `close` flushes, forces the file channel to disk, closes the stream, then renames temp to original. If `renameTo` fails, it deletes an existing original and calls `NativeIO.renameTo`. If flushing/closing fails, it attempts to close the file descriptor and deletes the temp file. `abort` closes without commit and deletes temp.

## State and Persistence
State is the original and temp absolute files. Persistence semantics include fsync of file contents but not an explicit parent-directory fsync. On Windows, replacement is not atomic because the original is deleted before native rename.

## Dependencies and Integration
It depends on Java file APIs, NIO `Files.delete`, Hadoop `IOUtils`, and `NativeIO`. It is used by `PersistentLongFile` and `MD5FileUtils` for durable sidecar writes.

## Risks
Concurrent writers to the same target share the same `.tmp` path and can corrupt each other. Parent directory durability is not guaranteed after rename. Windows behavior can temporarily remove the target. `abort` logs but cannot guarantee cleanup if close/delete fails. The constructor assumes a non-null parent directory.

## Test Signals
Tests should cover successful commit, overwrite existing file, failed write/flush cleanup via injected stream or filesystem shim, abort cleanup, no original replacement after abort, and platform-specific rename fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/AtomicFileOutputStream.java -->
