# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ExceptionLastSeen.java

`ExceptionLastSeen` is a package-private synchronization helper for HDFS write-path classes such as `DataStreamer` and `DFSOutputStream`. It stores the latest `IOException` observed by background work so foreground calls can rethrow it.

The important methods are synchronized `get()`, `set(Throwable)`, `clear()`, `check(boolean resetToNull)`, and `throwException4Close()`. `set()` preserves `IOException` inputs and wraps other throwables. `check()` throws the stored exception and optionally clears it. `throwException4Close()` throws the stored exception if present, otherwise throws `ClosedChannelException`.

All state is in-memory and protected by instance synchronization. Dependencies are minimal (`IOException`, `ClosedChannelException`), while integration is semantic: asynchronous write failures are bridged into user-facing output-stream operations.

Risks include `set()` relying on an assertion for non-null input, sticky exceptions when `check(false)` is used, and `throwException4Close()` always throwing. Test signals are wrapping behavior, reset and clear behavior, repeated sticky checks, and close behavior with and without a prior exception.
