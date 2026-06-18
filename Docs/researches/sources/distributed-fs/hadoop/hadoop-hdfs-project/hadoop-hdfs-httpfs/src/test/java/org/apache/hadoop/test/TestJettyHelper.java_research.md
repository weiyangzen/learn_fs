# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestJettyHelper.java

## Purpose
JUnit 5 extension that creates and tears down an embedded Jetty server for methods annotated with `@TestJetty`. It supports HTTP and optional HTTPS keystore configuration.

## Important APIs, Types, And Functions
Constructors choose HTTP or SSL mode. `createJettyServer()` binds a `ServerConnector` to `localhost` and a free ephemeral port. Static accessors `getAuthority()`, `getJettyServer()`, and `getJettyURL()` use an inheritable thread-local helper. `beforeEach` and `afterEach` implement JUnit extension lifecycle.

## Control Flow
On `beforeEach`, the helper checks the current method for `@TestJetty`; when present it creates a `Server` but does not start it. It then stores itself in `TEST_JETTY_TL`. Tests configure handlers and call `start()`. On `afterEach`, the thread-local is removed and a running server is stopped.

## State, Persistence, And Dependencies
Per-test server state is held in the helper instance and exposed through `InheritableThreadLocal`. Port selection briefly opens a `ServerSocket(0)` and then closes it before Jetty binds. HTTPS uses `SslContextFactory.Server` and keystore fields supplied to the constructor.

## Integration Points
Depends on Jetty `Server`, `ServerConnector`, `HttpConfiguration`, `HttpConnectionFactory`, optional `SslConnectionFactory`, and Hadoop `JettyUtils.HEADER_SIZE`. Test code obtains URL/authority through this helper rather than constructing ports manually.

## Risks
The free-port probe has a race between closing the probe socket and Jetty binding. The thread-local is set even for unannotated tests, but accessors still reject missing `server`. SSL tests rely on valid keystore path/type/password. Stop failures are wrapped in runtime exceptions during teardown.

## Test Signals
Expected signals are successful loopback binding, correct HTTP/HTTPS URL construction, header-size configuration, and guaranteed server stop after each annotated test.
