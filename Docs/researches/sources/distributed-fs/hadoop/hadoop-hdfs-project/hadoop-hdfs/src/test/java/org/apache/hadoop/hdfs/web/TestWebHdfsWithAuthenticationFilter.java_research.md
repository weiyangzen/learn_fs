# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsWithAuthenticationFilter.java

## Purpose
This test verifies that WebHDFS requests pass through custom HTTP filters configured on the NameNode HTTP server, and that a filter rejection is surfaced to the WebHDFS client as an `IOException`.

## Important APIs, types, and functions
- `CustomizedFilter` implements `javax.servlet.Filter` and either calls `chain.doFilter` or sends HTTP 403 based on the static `authorized` flag.
- `CustomizedFilter.Initializer` extends `FilterInitializer` and registers the filter in the `FilterContainer`.
- `setUp()` configures `HttpServer2.FILTER_INITIALIZER_PROPERTY`, starts a single-node `MiniDFSCluster`, and opens a `webhdfs://host:port` `FileSystem`.
- `testWebHdfsAuthFilter()` toggles `authorized` and calls `fs.getFileStatus("/")`.

## Control flow
The class-level setup starts one cluster and one WebHDFS client. The test first sets `authorized=false`, expects `getFileStatus` to fail, then sets `authorized=true` and expects the same request to succeed. Tear-down closes the file system and cluster.

## State and persistence behavior
The only test control state is static boolean `authorized`; cluster and file system are static per class. No files are created. The cluster stores standard MiniDFS metadata and is shut down after all tests.

## Dependencies and integration points
The test connects HDFS `MiniDFSCluster`, `HttpServer2`, Hadoop `FilterInitializer`, servlet filters, WebHDFS `FileSystem`, and `NetUtils` host:port formatting. It exercises the integration point where NameNode HTTP filters wrap WebHDFS servlet handling.

## Risks and edge cases
The shared static `authorized` flag makes the filter intentionally global, so parallel execution of this exact class would be unsafe. The test validates only a read-only metadata op; redirecting write flows through DataNode filters are covered elsewhere. It catches any `IOException` for the denied request and does not assert the 403 status text.

## Test signals
Passing means a configured custom filter is invoked for WebHDFS and can both block and allow a request. Failure can indicate filter initializer wiring, NameNode HTTP configuration, WebHDFS error propagation, or MiniDFS HTTP address setup regressions.
