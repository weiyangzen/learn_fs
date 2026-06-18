# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/web/TestDatanodeHttpXFrame.java

## Purpose

`TestDatanodeHttpXFrame` validates X-Frame-Options handling on the DataNode HTTP server. It ensures the header is emitted with the default `SAMEORIGIN` value when enabled, omitted when disabled, and rejected when configured with an invalid option value.

## Important APIs and types

- `DFS_XFRAME_OPTION_ENABLED` and `DFS_XFRAME_OPTION_VALUE` control the behavior.
- `MiniDFSCluster` starts a real DataNode web server.
- `HttpServer2.XFrameOption.SAMEORIGIN` is the expected default value.
- `HttpURLConnection` fetches the DataNode info port root page and reads response headers.

## Control flow

Each test creates a one-DataNode cluster with the desired X-Frame settings. The enabled test connects to `http://localhost:<infoPort>`, reads the `X-FRAME-OPTIONS` header, asserts it exists, and checks it ends with `SAMEORIGIN`. The disabled test asserts the header is absent. The invalid-value test expects cluster creation to throw `IllegalArgumentException` when the option value is set to `Hadoop`.

## State and persistence behavior

The cluster and DataNode HTTP server are real and are shut down after each test. No files are intentionally created beyond MiniDFSCluster test data.

## Dependencies and integration points

The test integrates HDFS X-Frame config keys, `HttpServer2` option parsing, DataNode info server startup, and HTTP response headers. It protects clickjacking-related admin UI hardening.

## Risks and edge cases

- The test uses the root page only; it does not verify every DataNode servlet path.
- It checks `endsWith` instead of exact equality, allowing extra header prefix text.
- The method name `testNameNodeXFrameOptionsDisabled` is misleading because it creates a DataNode cluster.
- Invalid value coverage uses one invalid string only.

## Test signals

Strong signals are real HTTP response header inspection, both enabled and disabled modes, default SAMEORIGIN value, invalid configuration rejection, and cluster cleanup after each test.
