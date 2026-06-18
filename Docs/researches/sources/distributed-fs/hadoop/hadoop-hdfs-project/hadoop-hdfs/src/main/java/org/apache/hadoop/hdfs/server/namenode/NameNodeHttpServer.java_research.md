# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeHttpServer.java

## Purpose
`NameNodeHttpServer` encapsulates the NameNode's Jetty/HttpServer2 web endpoint. It configures HTTP/HTTPS connectors, WebHDFS Jersey resources and filters, internal servlets, servlet-context attributes for NameNode services, and exposes bound addresses to the parent `NameNode`.

## Important APIs and Types
- Constructor `NameNodeHttpServer(Configuration, NameNode, InetSocketAddress)` stores the config, owning NameNode, and bind address.
- `start`, `stop`, and `join` manage the underlying `HttpServer2`.
- `initWebHdfs` configures WebHDFS path resources, parameter filters, user providers, ACL pattern validation, and optional REST CSRF prevention.
- Setters `setFSImage`, `setNameNodeAddress`, `setStartupProgress`, and `setAliasMap` publish objects into the servlet context.
- Static context getters retrieve `FSImage`, `NameNode`, `TokenVerifier`, `Configuration`, `InMemoryAliasMap`, NameNode address, startup progress, and HA state.
- `setupServlets` installs startup progress, fsck, image transfer, active-state, and network topology servlets.

## Control Flow
`start` reads the HTTP policy, derives HTTP and HTTPS bind addresses with bind-host overrides, builds the server from `DFSUtil.getHttpServerTemplate`, configures X-Frame-Options, stores the DataNode HTTPS port when HTTPS is enabled, initializes WebHDFS resources, sets base context attributes, installs internal servlets, starts the server, records connector addresses, and writes bound host:port values back to configuration.

## State and Persistence Behavior
Runtime state consists of the `HttpServer2` instance and bound `httpAddress`/`httpsAddress`. It does not persist metadata itself, but it exposes persistent metadata services through `ImageServlet` and WebHDFS endpoints and shares live `FSImage`/NameNode objects through servlet attributes.

## Dependencies and Integration Points
It depends on `HttpServer2`, `DFSUtil`, `HttpConfig.Policy`, Jersey `ResourceConfig`, WebHDFS parameter/resource classes, `RestCsrfPreventionFilter`, `ParamFilter`, `JspHelper`, `StartupProgressServlet`, `FsckServlet`, `ImageServlet`, `IsNameNodeActiveServlet`, `NetworkTopologyServlet`, and optional `InMemoryAliasMap`. `NameNode.initialize` starts it and fills attributes after loading the namesystem.

## Risks and Edge Cases
- Bind-host overrides can make advertised and bound addresses differ; tests must check both.
- WebHDFS CSRF protection is conditional and path-scoped to `/webhdfs/*`; misconfiguration changes REST write exposure.
- Servlet attribute population order matters: servlets needing `FSImage` or alias map must be used after `NameNode` sets them.
- HTTP/HTTPS connector index handling assumes the builder creates connectors in policy order.
- X-Frame options are passed through config and should reject/handle illegal values in lower HttpServer layers.

## Test Signals
`TestNameNodeHttpServer`, `TestNameNodeHttpServerXFrame`, `TestNameNodeRespectsBindHostKeys`, WebHDFS tests, and image-transfer/fsck tests are the relevant coverage. Important cases include HTTP-only, HTTPS-enabled, X-Frame enabled/disabled/invalid, bind host overrides, CSRF filter installation, and context getter correctness.
