<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/FileSystemAccess.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/FileSystemAccess.java

## Purpose
`FileSystemAccess` is the service interface that mediates all Hadoop `FileSystem` access for HttpFS.

## Important APIs, Types, And Functions
Nested `FileSystemExecutor<T>` defines `T execute(FileSystem fs) throws IOException`. Service methods are `execute(String user, Configuration conf, FileSystemExecutor<T> executor)`, `createFileSystem(String user, Configuration conf)`, `releaseFileSystem(FileSystem fs)`, and `getFileSystemConfiguration()`.

## Control Flow
`HttpFSServer` uses `execute` for short operations and `createFileSystem`/`releaseFileSystem` through the release filter for streaming responses. `FSOperations` supplies concrete executors.

## State And Persistence
The interface has no state. Implementations may cache filesystems and own configuration.

## Dependencies And Integration Points
It depends on Hadoop `Configuration`, `FileSystem`, and `IOException`, and is implemented by `FileSystemAccessService`.

## Risks
Callers must release unmanaged filesystems. Implementations may require the configuration to come from `getFileSystemConfiguration`, as `FileSystemAccessService` does.

## Test Signals
Contract tests should assert executor invocation under the requested user, exception wrapping, unmanaged filesystem release, and configuration validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/FileSystemAccess.java -->
