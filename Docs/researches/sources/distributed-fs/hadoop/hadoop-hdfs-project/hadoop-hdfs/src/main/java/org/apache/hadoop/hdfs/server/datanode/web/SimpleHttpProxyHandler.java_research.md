# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/SimpleHttpProxyHandler.java

## Purpose

`SimpleHttpProxyHandler` is a small Netty session-layer proxy from the external DataNode HTTP listener to the internal Jetty info server. It handles non-WebHDFS requests and rewrites HTTP redirect locations to HTTPS when the external listener is secure.

## Important APIs, Control Flow, and State

`channelRead0` stores the request URI, creates a client `Bootstrap` on the same event loop, connects to the Jetty host, and on success removes the inbound `HttpResponseEncoder`, copies headers into a new full request, sets `Connection: close`, and writes it to the proxied channel. `Forwarder` writes proxied server responses back to the client and reads the next response chunk only after successful flush. In secure mode, the outbound pipeline decodes HTTP responses, runs `SslRedirectRewriter` to replace leading `http://` `Location` values with `https://`, and adds a response encoder to the client pipeline.

State includes the current URI and proxied channel. `channelInactive` and `exceptionCaught` close the proxied channel. No data is persisted, and the handler assumes upper layers restrict malicious requests and that proxied responses are modest.

## Dependencies, Integration, Risks, and Tests

Dependencies include Netty bootstrap/channel/HTTP codecs and `DatanodeHttpServer.LOG`. It integrates with `URLDispatcher` as the fallback path for UI and servlet requests.

Risks include request body loss because a new empty `DefaultFullHttpRequest` is created, pipeline encoder removal/addition ordering, redirect rewriting only for lowercase `http://` prefix, proxy buffering/backpressure assumptions, and connection-close-only behavior. Tests should cover successful proxying, connection failure response, secure redirect rewriting, client/proxy channel close interactions, and non-WebHDFS URI dispatch.
