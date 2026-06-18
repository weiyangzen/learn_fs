# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsWithMultipleNameNodes.java

## Purpose
This test validates WebHDFS create, read, append, and redirect behavior in a federated MiniDFSCluster with multiple independent NameNodes.

## Important APIs, types, and functions
- `setupCluster(int nNameNodes, int nDataNodes)` builds a simple federated topology, waits for activation, and opens one `WebHdfsFileSystem` per NameNode HTTP address.
- `createString` and `createStrings` produce NameNode-specific content with distinct lengths.
- `testRedirect()` writes, reads, appends, and rereads the same path independently through every WebHDFS client.

## Control flow
Class setup raises log levels and starts a four-NameNode, three-DataNode federated cluster. The test loops across `webhdfs[]`, creating `/testRedirect/file` in each namespace with unique content, checks file length for each namespace, reads back exact bytes, appends unique content, then verifies final length and concatenated content in each namespace.

## State and persistence behavior
The test persists the same logical path in each federated namespace. Since each `WebHdfsFileSystem` points to a different NameNode, the content is intentionally different by namespace. Static cluster state is destroyed in `shutdownCluster()`.

## Dependencies and integration points
It integrates `MiniDFSNNTopology.simpleFederatedTopology`, NameNode WebHDFS methods, `FSDataInputStream`, `FSDataOutputStream`, and WebHDFS client redirection from NameNode to DataNode for create/read/append operations.

## Risks and edge cases
The test assumes append is available and that a shared DataNode set can serve all federated namespaces. It validates per-NameNode isolation by content differences but does not explicitly assert block-pool identity. Static cluster and clients are class-scoped, so a setup failure aborts all coverage.

## Test signals
Passing demonstrates that WebHDFS can address multiple NameNodes by HTTP authority, correctly redirect data operations, preserve namespace isolation, and append/read bytes through each federated endpoint.
