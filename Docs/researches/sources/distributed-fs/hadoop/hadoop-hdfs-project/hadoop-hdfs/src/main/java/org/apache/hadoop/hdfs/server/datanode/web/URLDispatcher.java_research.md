# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/URLDispatcher.java

## Purpose

`URLDispatcher` is the one-request Netty dispatcher that chooses between the in-process WebHDFS handler and the internal Jetty proxy for DataNode HTTP requests.

## Important APIs, Control Flow, and State

`channelRead0` checks whether the request URI starts with `WebHdfsHandler.WEBHDFS_PREFIX`. WebHDFS requests replace the dispatcher in the pipeline with a new `WebHdfsHandler(conf, confForCreate)` and immediately delegate the request. All other requests replace it with `SimpleHttpProxyHandler(proxyHost, isSecure)` and delegate. Constructor state is the Jetty proxy address, normal/create configurations, and secure flag.

There is no persistence. The handler is intentionally replaced after the first request so the rest of the connection is handled by the selected protocol path.

## Dependencies, Integration, Risks, and Tests

Dependencies include Netty pipeline APIs, `Configuration`, `WebHdfsHandler`, and `SimpleHttpProxyHandler`. It integrates directly into `DatanodeHttpServer` pipelines after filters and chunked write support.

Risks include simple prefix matching accepting unexpected paths, handler-construction exceptions closing the request, and mixed-protocol keepalive connections being pinned to the first selected handler. Tests should cover WebHDFS prefix dispatch, proxy fallback, secure flag propagation, and pipeline replacement.
