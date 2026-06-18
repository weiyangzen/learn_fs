<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterHttpServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterHttpServer.java

## Purpose
`RouterHttpServer` manages the router web server. It exposes the router UI, WebHDFS handlers, active-state probe, federated FSCK, and network-topology servlet through Hadoop `HttpServer2`.

## Important APIs, Types, and Functions
It extends `AbstractService`. `serviceInit` resolves HTTP and HTTPS bind addresses from router config. `serviceStart` builds the `HttpServer2` template with router SPNEGO/keytab settings, configures X-Frame headers, initializes WebHDFS with `RouterWebHdfsMethods`, stores router/config context attributes, registers internal servlets, starts the server, and updates the actual HTTP port if an ephemeral port was used. `serviceStop` stops the server. `getConfFromContext` and `getRouterFromContext` retrieve context attributes for servlets.

## Control Flow
The service lifecycle follows Hadoop service phases: configuration-derived addresses in init, server construction and servlet registration in start, connector address reconciliation after start, and graceful stop if a server exists.

## State and Persistence Behavior
The class holds runtime-only `Configuration`, `Router`, `HttpServer2`, and socket addresses. It persists no data. Servlet context attributes are process-local integration state.

## Dependencies and Integration Points
Dependencies include `DFSUtil.getHttpServerTemplate`, `NameNodeHttpServer.initWebHdfs`, `HttpServer2`, `JspHelper.CURRENT_CONF`, `IsRouterActiveServlet`, `RouterFsckServlet`, `RouterNetworkTopologyServlet`, `RouterWebHdfsMethods`, and router HTTP/HTTPS/SPNEGO config keys.

## Risks
Misconfigured bind hosts, SPNEGO principal, keytab, or X-Frame settings affect availability and security. Context attribute names must remain compatible with `DfsServlet` and router servlets. Ephemeral port handling updates only the HTTP address from connector zero. Servlet registration order and `requireAuth` flags matter for operational endpoints.

## Test Signals
Tests should cover address resolution, X-Frame propagation, WebHDFS initialization package, servlet registration and auth flag for FSCK, context attributes, ephemeral port update, getters, and stop behavior when startup partially failed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterHttpServer.java -->
