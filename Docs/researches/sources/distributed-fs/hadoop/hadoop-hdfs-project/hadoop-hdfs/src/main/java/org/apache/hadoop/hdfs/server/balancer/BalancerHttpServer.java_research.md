# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/BalancerHttpServer.java

## Purpose
`BalancerHttpServer` starts the optional web server used by the HDFS balancer for HTTP/HTTPS status pages and servlet/JSP integration.

## Important APIs and types
Main methods are `start`, `setBalancerAttribute`, `stop`, `getHttpAddress`, and `getHttpsAddress`. It stores the current balancer under the `current.balancer` attribute and publishes configuration under `JspHelper.CURRENT_CONF`.

## Control flow
`start` resolves HTTP and HTTPS socket addresses from balancer-specific DFS keys, creates an `HttpServer2.Builder` through `DFSUtil.getHttpServerTemplate`, applies X-Frame options, builds and starts the server, then updates configuration with the actual bound connector addresses based on the selected HTTP policy. `stop` wraps server stop exceptions in `IOException`.

## State and persistence
Runtime state is configuration, bound HTTP/HTTPS addresses, and the `HttpServer2` instance. It persists nothing.

## Dependencies and integration points
It integrates with Hadoop `HttpServer2`, DFS HTTP policy and security template, SPNEGO/keytab configuration, `JspHelper`, `NetUtils`, and `Balancer` status exposure.

## Risks and edge cases
Connector index handling depends on HTTP policy ordering. If the server binds to port 0, the config is updated only after startup. Stop can throw if the underlying server stop fails. The balancer attribute must be set after a `Balancer` instance is created for UI code to see current state.

## Test signals
Tests should verify HTTP-only, HTTPS-only, and dual connector address updates; X-Frame config propagation; SPNEGO/keytab key usage; balancer attribute visibility; and stop behavior with and without a started server.
