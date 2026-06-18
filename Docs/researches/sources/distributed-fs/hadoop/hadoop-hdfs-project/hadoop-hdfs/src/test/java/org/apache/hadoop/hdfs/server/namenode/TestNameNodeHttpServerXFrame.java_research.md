# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeHttpServerXFrame.java

## Purpose
Tests X-Frame-Options header behavior for NameNode and SecondaryNameNode HTTP servers, covering enabled, disabled, illegal option, and secondary server defaults.

## Important APIs, Types, and Functions
- Uses `NameNodeHttpServer`, `HttpServer2.XFrameOption.SAMEORIGIN`, `DFS_XFRAME_OPTION_ENABLED`, and `DFS_XFRAME_OPTION_VALUE`.
- `getServerURL` derives server URL from `HttpServer2.getConnectorAddress(0)`.
- Uses `SecondaryNameNode.startInfoServer` and `SecondaryNameNode.getHttpAddress`.

## Control Flow
- `testNameNodeXFrameOptionsEnabled` starts a server with XFrame enabled and asserts header exists and ends with `SAMEORIGIN`.
- `testNameNodeXFrameOptionsDisabled` asserts the header is absent when disabled.
- `testNameNodeXFrameOptionsIllegalOption` expects `IllegalArgumentException` for invalid value `hadoop`.
- `testSecondaryNameNodeXFrame` starts SecondaryNameNode info server and verifies default `SAMEORIGIN` header.

## State and Persistence Behavior
- No metadata persistence is tested; state is HTTP server configuration and response headers.
- Helper starts a `NameNodeHttpServer` but does not stop it, so tests rely on ephemeral ports and JVM cleanup.

## Dependencies and Integration Points
- Integrates NameNode/SecondaryNameNode HTTP server config with Hadoop `HttpServer2` X-Frame option enforcement.
- Uses real `HttpURLConnection` to inspect headers.

## Risks and Edge Cases
- `createServerwithXFrame` leaks server instances because it does not call `stop`.
- Header comparison uses `endsWith`, allowing prefixed values.
- SecondaryNameNode is started without explicit shutdown in the test body.

## Test Signals
- Focused signal for clickjacking header defaults and validation across NameNode HTTP surfaces.
