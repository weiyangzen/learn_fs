<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSReleaseFilter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSReleaseFilter.java

## Purpose
`HttpFSReleaseFilter` connects the generic filesystem-release servlet filter to the HttpFS service registry. Its only role is to ensure unmanaged `FileSystem` instances created for request streaming are released at servlet request completion.

## Important APIs, Types, And Functions
The class extends `FileSystemReleaseFilter` and overrides `getFileSystemAccess()` to return `HttpFSServerWebApp.get().get(FileSystemAccess.class)`.

## Control Flow
`HttpFSServer.createFileSystem` creates an unmanaged filesystem for operations like `OPEN`, stores it in `FileSystemReleaseFilter.setFileSystem(fs)`, and the filter later calls the returned `FileSystemAccess` service to release it.

## State And Persistence
The class has no fields. State is maintained by the parent filter, likely request-local/thread-local, and by `FileSystemAccessService`'s cache.

## Dependencies And Integration Points
It depends on `HttpFSServerWebApp`, `FileSystemAccess`, and `FileSystemReleaseFilter`. It is part of the streaming response cleanup path.

## Risks
If the webapp singleton is not initialized or the `FileSystemAccess` service is missing, request cleanup can fail. Correct filter ordering is required so it wraps requests that call `setFileSystem`.

## Test Signals
Tests should verify that a filesystem set during request handling is released exactly once and that open-stream responses do not leak unmanaged filesystem counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSReleaseFilter.java -->
