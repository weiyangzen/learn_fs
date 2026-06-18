# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/client/TestHttpFSFWithWebhdfsFileSystem.java

## Purpose
This subclass runs the base compatibility matrix using Hadoop's standard `WebHdfsFileSystem` client implementation against the HttpFS server.

## Important APIs, Types, and Functions
It extends `TestHttpFSWithHttpFSFileSystem` and overrides only `getFileSystemClass()` to return `WebHdfsFileSystem.class`.

## Control Flow
All setup, operation dispatch, and assertions are inherited. The overridden class causes `BaseTestHttpFSWith.getHttpFSFileSystem(Configuration)` to register `fs.webhdfs.impl` as `WebHdfsFileSystem` and use the inherited `webhdfs` scheme.

## State and Persistence
State is inherited from the base test: temporary configs, Jetty server, and filesystem test data.

## Dependencies and Integration Points
It verifies compatibility between the HttpFS server endpoint and Hadoop's built-in WebHDFS client stack.

## Risks
Because behavior is entirely inherited, failures are attributable to client implementation differences or server compatibility rather than local logic. This is intentional but can make test triage broad.

## Test Signals
The full `Operation` matrix runs with `WebHdfsFileSystem`, checking that HttpFS honors WebHDFS client expectations and response formats.
