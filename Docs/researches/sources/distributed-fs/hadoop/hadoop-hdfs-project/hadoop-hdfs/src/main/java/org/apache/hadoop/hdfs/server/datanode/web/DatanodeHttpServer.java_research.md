# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/DatanodeHttpServer.java

## Purpose

`DatanodeHttpServer` starts and owns the DataNode HTTP/HTTPS surface. It runs a small Jetty `HttpServer2` for UI/servlets behind an internal proxy port and Netty front-end listeners that dispatch WebHDFS requests directly or proxy other requests to Jetty.

## Important APIs, Control Flow, and State

The constructor configures Jetty thread counts, admin ACL, SPNEGO host, x-frame settings, servlet/context attributes, the block scanner report servlet, and `DataNodeUGIProvider`. It creates a `confForCreate` with umask `000` for WebHDFS create semantics, starts Netty boss/worker groups, determines HTTP policy, reflectively creates configured filter handlers, and builds HTTP and/or HTTPS `ServerBootstrap` pipelines. HTTP pipelines add request decoder, response encoder, optional filters, `ChunkedWriteHandler`, and `URLDispatcher`. HTTPS additionally installs `SslHandler`.

`start` binds enabled Netty servers, updates the configuration with actual HTTP/HTTPS addresses, and logs endpoints. `close` gracefully shuts down event loops, destroys SSL state, closes any externally supplied JSVC channel, and stops Jetty. `getFilterHandlers` loads classes from configured/default handler keys, invokes static `initializeState(Configuration)`, and constructs handlers using the returned state type. `MapBasedFilterConfig` provides just enough servlet `FilterConfig` for Netty-backed security filters.

## Dependencies, Integration, Risks, and Tests

Dependencies include Netty, Jetty `HttpServer2`, `SSLFactory`, `DFSUtil` HTTP policy, `DataNode`, `BlockScanner.Servlet`, `DataNodeUGIProvider`, and filter handler classes. Integration points are WebHDFS, DataNode web UI, CSRF/host restriction filters, SPNEGO configuration, and privileged external socket binding.

Risks include reflection misconfiguration aborting startup, security filters missing if configuration resolves null, lifecycle leaks on partial constructor failure, external channel bind no-op semantics, SSL initialization failures, and proxy/WebHDFS dispatch depending on URI prefixes. Tests should cover HTTP-only, HTTPS-only, dual policy, external channel, filter initialization, address updates, close cleanup, and WebHDFS/proxy pipeline behavior.
