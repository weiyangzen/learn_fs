# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/client/BaseTestHttpFSWith.java

## Purpose
`BaseTestHttpFSWith` is the central parameterized compatibility harness for HttpFS, WebHDFS, and SWebHDFS client behavior against an embedded HttpFS server and proxied filesystem.

## Important APIs, Types, and Functions
Subclasses provide `getProxiedFSTestDir`, `getProxiedFSURI`, and `getProxiedFSConf`; optional overrides choose filesystem class and scheme. `createHttpFSServer` builds a temporary home with `conf`, `log`, `temp`, writes `hdfs-site.xml` and `httpfs-site.xml`, configures proxy users and auth secret, and starts Jetty with the webapp resource. `getHttpFSFileSystem` registers the chosen implementation and returns a Hadoop `FileSystem`.

## Control Flow
The `Operation` enum lists the test matrix. `operations()` returns every enum value. `testOperation` and `testOperationDoAs` are JUnit 5 parameterized tests that start the server and dispatch the selected operation normally and under a proxy `UserGroupInformation.doAs`. The large `operation` switch routes to focused private test methods.

## State and Persistence
Each test creates temporary directories/files, writes XML configuration and secret files, creates data in the proxied filesystem, and starts/stops resources through test helpers. Persistent state is isolated under JUnit test directories and MiniDFSCluster storage.

## Dependencies and Integration Points
The class integrates Hadoop `FileSystem`, MiniDFSCluster helpers, Jetty, HttpFS server webapp, HttpFS/WebHDFS/SWebHDFS clients, ACL/xattr/snapshot/erasure-coding/storage-policy APIs, JSON utilities, and security user helpers. It is the strongest integration signal for the wsrs parameter providers, JSON providers, filters, and web descriptors.

## Covered Behavior
The test matrix covers get/open/create/append/truncate/concat/rename/delete/listing/batched listing/working directory/trash roots/mkdirs/times/permission/owner/replication/checksum/content summary/quota usage/xattrs/ACLs/encryption/storage policy/erasure coding/snapshots/snapshot diffs/server defaults/access checks/storage policy satisfier/block locations/link status/status/EC policies/EC codecs/trash root listing. Many assertions compare HttpFS/WebHDFS results with direct `DistributedFileSystem` results.

## Risks
The file is very broad and can be expensive because each operation starts an embedded HttpFS server and runs both direct and doAs variants. Some operations are skipped for local filesystems, so local subclass coverage is intentionally narrower. Several exception tests accept multiple exception types, which improves compatibility but may hide overly broad error mapping.

## Test Signals
This file is itself the main signal. It validates request parsing, operation dispatch, response JSON, filesystem side effects, proxy-user handling, and advanced HDFS metadata compatibility across different client implementations.
