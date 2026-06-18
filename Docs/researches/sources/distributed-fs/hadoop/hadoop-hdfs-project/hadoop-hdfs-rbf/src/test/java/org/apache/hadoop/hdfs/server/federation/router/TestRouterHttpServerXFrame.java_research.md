# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterHttpServerXFrame.java

## Purpose

`TestRouterHttpServerXFrame.java` verifies that the Router HTTP server emits the configured `X-FRAME-OPTIONS` header. The source was read as a complete 67-line JUnit 5 test.

## Important APIs, Types, and Functions

The test uses `RouterConfigBuilder.http`, `DFSConfigKeys.DFS_XFRAME_OPTION_ENABLED`, `DFSConfigKeys.DFS_XFRAME_OPTION_VALUE`, `HttpServer2.XFrameOption.SAMEORIGIN`, `Router`, and `HttpURLConnection`. The only test method is `testRouterXFrame`.

## Control Flow

The test builds an HTTP-enabled router configuration, enables X-Frame options with value `SAMEORIGIN`, starts a router on an ephemeral HTTP address, opens an HTTP connection to the root URL, reads the `X-FRAME-OPTIONS` response header, asserts it exists and ends with `SAMEORIGIN`, then stops and closes the router in `finally`.

## State and Persistence Behavior

There is no persistent state. The router's in-memory HTTP server is started and stopped within the test.

## Dependencies and Integration Points

This checks Router HTTP server wiring to Hadoop `HttpServer2` security headers and DFS configuration keys.

## Risks and Edge Cases

Only the enabled `SAMEORIGIN` case is covered. Disabled headers, other X-Frame values, HTTPS, and non-root endpoints are not checked. The assertion uses `endsWith`, allowing prefixes in the header.

## Test Signals

Signals are successful router HTTP startup, reachable root URL, non-null `X-FRAME-OPTIONS`, and header suffix matching `SAMEORIGIN`.
