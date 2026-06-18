<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/WebImageViewer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/WebImageViewer.java

## Purpose
`WebImageViewer` loads an fsimage and exposes a read-only WebHDFS-like HTTP API for that offline namespace using Netty.

## APIs and Types
Public constructors accept an `InetSocketAddress` with optional `Configuration`. Public methods are `start(String fsimage)`, testing-visible `initServer(String fsimage)`, testing-visible `getPort()`, and `close()`. The class owns Netty bootstrap, boss/worker event-loop groups, a channel group, bound channel, mutable bound address, and configuration.

## Control Flow
Construction configures Netty NIO groups and applies Hadoop security configuration to `UserGroupInformation`. `start` rejects secure mode, initializes the server, then blocks on the channel close future until interrupted. `initServer` loads the fsimage through `FSImageLoader`, installs an HTTP request decoder, string encoder, HTTP response encoder, and `FSImageHandler`, binds to the requested address, records the actual local address, and adds the server channel to the group. `close` closes all channels and gracefully shuts down both groups.

## State and Persistence
The loaded fsimage is retained by `FSImageHandler`/`FSImageLoader` for serving requests; this class persists no new files. Network state consists of live channels and event-loop threads.

## Dependencies and Integration
It depends on Netty, Hadoop `Configuration`, `CommonConfigurationKeysPublic`, `UserGroupInformation`, `FSImageLoader`, and `FSImageHandler`. It integrates the offline image loader with WebHDFS-compatible request handling.

## Risks
Secure mode is unsupported and fails at runtime. `start` only closes on interruption, so other init failures depend on caller cleanup. Pipeline ordering includes `StringEncoder` before `HttpResponseEncoder`, which depends on handler output types. Long-lived event loops require `close` in tests to avoid leaked threads. The viewer exposes offline namespace metadata over the configured bind address without authentication.

## Test Signals
Tests should bind to port 0 and assert `getPort`, reject secure configuration, issue representative WebHDFS requests, verify `close` releases the port/threads, and exercise invalid fsimage load failure without leaked channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/WebImageViewer.java -->
