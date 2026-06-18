## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/FSImageHandler.java

Purpose: `FSImageHandler` is the Netty HTTP handler that exposes a read-only subset of WebHDFS against an offline protobuf fsimage loaded by `FSImageLoader`.

Important APIs and control flow: `channelActive` registers channels with a `ChannelGroup`. `channelRead0` accepts only HTTP GET, parses the URI with `QueryStringDecoder`, validates that the path starts with the WebHDFS prefix, uppercases the `op` parameter, and dispatches to `FSImageLoader` methods for `GETFILESTATUS`, `LISTSTATUS`, `GETACLSTATUS`, `GETXATTRS`, `LISTXATTRS`, and `GETCONTENTSUMMARY`. Responses are JSON UTF-8 with `Content-Length` and connection close. `exceptionCaught` converts exceptions to JSON and maps argument errors to 400, missing paths to 404, IO errors to 403, and other failures to 500.

State, persistence, and dependencies: state is the shared immutable-ish `FSImageLoader` and active channel group. Dependencies are Netty HTTP classes, WebHDFS constants, `JsonUtil`, and Hadoop string utilities.

Integration points: instantiated by `WebImageViewer` for `OfflineImageViewerPB -p Web`.

Risks and test signals: tests should cover method rejection, missing/invalid `op`, path-prefix validation, xattr query parameters, exception-to-status mapping, and JSON response bodies. Security scope is intentionally local/offline; no authentication or HTTPS is provided. Large responses are materialized as a full string before being wrapped in a `ByteBuf`.
