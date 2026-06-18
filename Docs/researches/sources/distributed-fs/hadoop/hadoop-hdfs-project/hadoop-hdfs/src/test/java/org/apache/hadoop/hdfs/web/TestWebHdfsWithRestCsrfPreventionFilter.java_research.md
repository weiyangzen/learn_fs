# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsWithRestCsrfPreventionFilter.java

## Purpose
This parameterized test verifies WebHDFS behavior when REST CSRF prevention is independently enabled or disabled on NameNode, DataNode, and client. It distinguishes operations handled only by the NameNode from operations redirected to DataNodes.

## Important APIs, types, and functions
- `data()` returns eight boolean combinations for NameNode CSRF, DataNode CSRF, and client CSRF settings.
- `before()` builds a MiniDFSCluster with NameNode CSRF settings, starts a DataNode with its own CSRF setting and `RestCsrfPreventionFilterHandler`, opens direct DFS and WebHDFS clients.
- `testCreate`, `testDelete`, `testGetFileStatus`, and `testTruncate` encode the expected matrix for PUT, DELETE, GET, and POST operations.

## Control flow
Each parameterized test calls `initTestWebHdfsWithRestCsrfPreventionFilter`, which stores booleans and starts a fresh cluster. Create is expected to fail without client CSRF support if either NameNode or DataNode has the filter because it performs a NameNode-to-DataNode redirected PUT. Delete and truncate fail only when NameNode CSRF is enabled and the client is not configured because they are metadata operations. Get file status always succeeds because GET is not protected by the CSRF filter.

## State and persistence behavior
Each parameter set starts and tears down a MiniDFSCluster. Tests create `/file` where needed through the direct file system before delete/truncate cases. `after()` closes both file systems and shuts down the cluster.

## Dependencies and integration points
The test integrates WebHDFS client CSRF header configuration, NameNode HTTP CSRF filter configuration, DataNode Netty/HTTP filter handler configuration, `CommonPathCapabilities.FS_TRUNCATE`, and `DFSTestUtil.createFile`.

## Risks and edge cases
The browser user-agent regex is set to `.*` so the filter always applies; production behavior may depend on user-agent matching. Assertions check for `"Missing Required Header"` in `IOException` messages, making them sensitive to server error text. The matrix intentionally uses only one DataNode and one file path per case.

## Test signals
Passing confirms client CSRF headers are emitted when enabled, unsafe WebHDFS methods are rejected by protected servers when missing headers, GET remains allowed, and DataNode protection affects redirected create but not NameNode-only metadata operations.
