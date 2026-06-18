# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/HostRestrictingAuthorizationFilterHandler.java

## Purpose

`HostRestrictingAuthorizationFilterHandler` adapts servlet-oriented `HostRestrictingAuthorizationFilter` authorization checks into the DataNode Netty HTTP pipeline. It either forwards allowed requests or sends an error response and closes the connection.

## Important APIs, Control Flow, and State

`initializeState(Configuration)` reads the HDFS host restriction config, builds a `MapBasedFilterConfig`, initializes a reusable filter instance, and returns it for reflective construction by `DatanodeHttpServer`. `channelRead0` calls `handleInteraction` with `NettyHttpInteraction`. That interaction exposes remote address, query string, request URI without query, remote user parsed from `user.name`, method, `proceed`, and `sendError`.

The handler is marked `@Sharable` and holds a stateless initialized filter. `proceed` retains the Netty request before firing it to the next handler; error paths write a `DefaultHttpResponse` with `Connection: close`. There is no persistence.

## Dependencies, Integration, Risks, and Tests

Dependencies include Netty HTTP types, `HostRestrictingAuthorizationFilter`, `UserParam`, `DatanodeHttpServer.MapBasedFilterConfig`, and servlet exceptions. It integrates as an optional security filter in DataNode HTTP/HTTPS pipelines.

Risks include URI parsing returning null query on invalid URIs, request reference-count mistakes, remote user extraction from the first query value only, and filter initialization with blank restrictions potentially allowing more than intended. Tests should cover allowed and denied requests, malformed URI handling, proxy user parsing, response close headers, exception path, and sharable filter reuse across channels.
