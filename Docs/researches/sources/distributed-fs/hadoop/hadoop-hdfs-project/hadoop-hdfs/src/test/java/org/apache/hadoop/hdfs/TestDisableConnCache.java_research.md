# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDisableConnCache.java

## Purpose
`TestDisableConnCache` is a regression test for disabling HDFS client peer/socket caching. It verifies that setting the client socket cache capacity to zero prevents reads from leaving cached peers in the `DFSClient` context.

## Important APIs, Types, and Functions
The class defines `BLOCK_SIZE`, `FILE_SIZE`, and one test method, `testDisableCache()`. It uses `HdfsConfiguration`, `HdfsClientConfigKeys.DFS_CLIENT_SOCKET_CACHE_CAPACITY_KEY`, `BlockReaderTestUtil`, `FileSystem.newInstance`, `DFSTestUtil.readFile`, and `DistributedFileSystem.dfs.getClientContext().getPeerCache().size()`.

## Control Flow
The test builds a configuration with socket-cache capacity `0`, starts a one-datanode `BlockReaderTestUtil` mini setup, writes `/testConnCache.dat`, opens a new FileSystem instance using the same configuration, reads the file, and asserts the peer cache size remains zero. Cleanup closes the FileSystem and shuts down the utility in a `finally` block.

## State and Persistence Behavior
The only durable-ish state is a temporary HDFS test file inside the mini cluster. The behavior under test is client-side in-memory peer-cache state after a read. There is no NameNode restart or persisted metadata assertion.

## Dependencies and Integration Points
This test integrates the client config key, block reader setup, DFSClient client context, peer cache implementation, and normal read path. It is directly relevant to resource-management behavior in clients that intentionally disable socket reuse.

## Risks
The test accesses `DistributedFileSystem.dfs` internals and `ClientContext.getPeerCache()`, so refactors of client context visibility or peer-cache accounting may require updates. The assertion should remain about externally intended capacity-zero behavior, not a particular cache implementation.

## Test Signals
Passing means a full file read does not populate the peer cache when capacity is zero. Failure suggests disabled caching is ignored or the peer cache reports retained peers despite the configuration.
