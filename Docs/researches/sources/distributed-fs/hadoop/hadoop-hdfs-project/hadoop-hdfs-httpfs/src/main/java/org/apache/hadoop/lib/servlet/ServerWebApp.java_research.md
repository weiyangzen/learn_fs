# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/servlet/ServerWebApp.java

## Purpose
`ServerWebApp` bridges Hadoop's internal `Server` lifecycle into a servlet container. It starts the server during `ServletContextListener.contextInitialized`, stops it during `contextDestroyed`, and resolves servlet-deployment directories and authority from Java system properties.

## Important APIs, Types, and Functions
The class extends `org.apache.hadoop.lib.server.Server` and implements `ServletContextListener`. It defines property suffixes such as `.home.dir`, `.config.dir`, `.log.dir`, `.temp.dir`, `.http.hostname`, `.http.port`, and public `.ssl.enabled`. Public and protected APIs include `setHomeDirForCurrentThread`, constructor variants for tests, static `getHomeDir`, static `getDir`, `resolveAuthority`, `getAuthority`, `setAuthority`, and `isSslEnabled`.

## Control Flow
The default constructor resolves home/config/log/temp directories from `#name#.home.dir` and related properties, defaulting config/log/temp under the home directory. `contextInitialized` calls `init()` and wraps `ServerException` as `RuntimeException` after logging to the servlet context. `getAuthority` lazily caches the address returned by `resolveAuthority`, which requires hostname and port system properties and resolves the hostname with `InetAddress.getByName`.

## State and Persistence
The main mutable state is the cached `InetSocketAddress authority` and a static test-only `ThreadLocal<String>` for overriding home directory. It reads Java system properties but does not persist changes. The inherited `Server` owns service lifecycle and configuration state.

## Dependencies and Integration Points
Concrete subclasses such as `HttpFSServerWebApp` provide the server name and services. The deployment `web.xml` files install that subclass as a listener. Shell launchers set `-Dhttpfs.home.dir`, `-Dhttpfs.config.dir`, `-Dhttpfs.log.dir`, and `-Dhttpfs.temp.dir`; the embedded web server path also relies on `httpfs.http.hostname`, `httpfs.http.port`, and `httpfs.ssl.enabled`.

## Risks
Missing required system properties fail startup. `resolveAuthority` catches `UnknownHostException` but not invalid integer ports, so malformed ports can propagate as `NumberFormatException`. Cached `authority` means system property changes after first access are ignored unless tests call `setAuthority`.

## Test Signals
The client and access-control tests call `HttpFSServerWebApp.setHomeDirForCurrentThread` before starting Jetty, exercising the test override path and servlet listener lifecycle. SSL subclasses depend on `isSslEnabled` via the web server integration.
