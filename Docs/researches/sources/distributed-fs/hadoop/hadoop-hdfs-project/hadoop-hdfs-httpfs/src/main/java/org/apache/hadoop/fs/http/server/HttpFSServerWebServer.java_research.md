<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSServerWebServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSServerWebServer.java

## Purpose
`HttpFSServerWebServer` is the standalone HttpFS Jetty/HttpServer2 launcher. It loads HttpFS default/site resources, handles deprecated environment overrides, builds the HTTP or HTTPS endpoint, configures authentication filter prefixes and admin ACLs, and exposes lifecycle methods for start/join/stop.

## Important APIs, Types, And Functions
Constants define config resources, host/port/SSL keys, administrators key, server name `webhdfs`, and servlet path `/webhdfs`. The constructor applies `deprecateEnv` overrides, determines scheme, builds the endpoint URI, removes default auth/proxy filter initializers that HttpFS replaces, and constructs `HttpServer2`. `start`, `join`, `stop`, `getUrl`, `getHttpServer`, `main`, and `addDeprecatedKeys` provide lifecycle and compatibility hooks.

## Control Flow
Static initialization registers deprecated key aliases and default resources. `main` creates a normal Hadoop `Configuration`, reads SSL server configuration, constructs the server, starts it, and blocks in `join`. `start` initializes metrics system `httpfs`; `stop` stops Jetty and shuts metrics down.

## State And Persistence
Instance state is the built `HttpServer2` and selected scheme. Configuration may be mutated by deprecated environment overrides and filter initializer cleanup. No files are written.

## Dependencies And Integration Points
It integrates with `HttpServer2`, `SSLFactory`, Hadoop auth initializers, `HttpFSAuthenticationFilter`, metrics2, ACLs, and Hadoop configuration deprecation APIs.

## Risks
Deprecated environment variables silently override config after logging warnings. Filter initializer filtering only removes exact class names. `getUrl` returns null before connector bind. Metrics shutdown here can interact with webapp metrics lifecycle.

## Test Signals
Tests should validate endpoint URL construction for HTTP/HTTPS, deprecated env override behavior, auth initializer filtering, deprecated key registration, admin ACL propagation, and lifecycle start/stop with metrics cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSServerWebServer.java -->
