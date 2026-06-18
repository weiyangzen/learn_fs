# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/FileIoProvider.java

Purpose: `FileIoProvider` is the DataNode's central filesystem operation wrapper. It delegates actual Java/native file operations while adding profiling hooks, fault-injection hooks, and asynchronous disk-error checks on failures.

Important APIs and types: `OPERATION` categorizes operations. Public methods cover `flush`, `sync`, `dirSync`, `syncFileRange`, `posixFadvise`, deletion, `transferToSocketFully`, stream/file creation, share-delete input streams, open-and-seek, random access files, recursive delete, replace/rename/move/native copy, mkdirs, listings, hard-link counts, and existence checks. Wrapped stream classes intercept `read` and `write` on `FileInputStream`, `FileOutputStream`, and `RandomAccessFile`.

Control flow: each operation records a begin timestamp via `ProfilingFileIoEvents`, invokes `FaultInjectorFileIoEvents`, performs the underlying filesystem call, reports success latency, and on exceptions calls `onFailure` before rethrowing. `transferToSocketFully` suppresses disk-error handling for common network errors such as broken pipe and connection reset. Stream factory methods close partially opened streams when wrapping fails.

State and persistence: the provider has no durable state, but operations mutate block files, metadata files, and directories. It holds profiling/fault hooks plus an optional `DataNode`; `onFailure` calls `datanode.checkDiskErrorAsync(volume)` when both DataNode and volume are available. Wrapped streams preserve the associated volume for later read/write instrumentation.

Dependencies and integration points: it integrates with `FsVolumeSpi`, `DataNode`, `ProfilingFileIoEvents`, `FaultInjectorFileIoEvents`, `NativeIO`, `IOUtils`, `FileUtil`, `Storage`, `HardLink`, Commons IO `FileUtils`, Java NIO `Files`, and `SocketOutputStream`. `LocalReplica`, dataset code, block send/receive paths, and disk-balancer moves rely on it for consistent disk instrumentation.

Risks: wrapped `read` methods pass `numBytesRead` to profiling and may pass `-1` at EOF, so metrics consumers must tolerate it. `getMetadataOutputStream` in `LocalReplica` bypasses this provider, so not every metadata write is instrumented. Failure handling catches `Exception`, so runtime exceptions also trigger disk checks. Some methods intentionally retain old behavior compatibility, so replacing them with a single move/delete primitive could change semantics.

Test signals: cover hook ordering and lengths for each operation, stream wrapper read/write metrics, failure-triggered volume checks, broken-pipe transfer suppression, partial factory cleanup, mkdirs failure semantics, delete-with-exists behavior, hard-link count errors, and null volume/DataNode handling.
