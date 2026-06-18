# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestSocketFactory.java

## Purpose

`TestSocketFactory` validates Hadoop socket factory equality, caching, SOCKS proxy configuration, and basic socket creation behavior for `StandardSocketFactory` and `SocksSocketFactory`.

## Important APIs, Types, And Functions

The test uses `NetUtils.getDefaultSocketFactory()`, `StandardSocketFactory`, `SocksSocketFactory`, `Configuration` key `hadoop.rpc.socket.factory.class.default`, and a local `ServerRunnable` echo server. `DummySocketFactory` subclasses `StandardSocketFactory` to exercise map-key equality.

## Control Flow

`startTestServer()` launches a simple TCP server on an ephemeral port and waits until it is ready. `testSocketFactory()` creates sockets through each overload using `InetAddress` and hostname forms, writes `test\n`, and expects `TEST`. `testProxy()` compares SOCKS factories before and after applying a `hadoop.socks.server` configuration. `@AfterEach` stops the server thread and checks for captured errors.

## State And Persistence Behavior

State is an in-memory server thread with volatile readiness/error flags, a server socket, and a map keyed by socket factories. No disk state is used. Cleanup depends on closing the server socket and joining within the timeout.

## Dependencies And Integration Points

The file integrates with Hadoop `NetUtils`, socket factory implementations, Java sockets, proxy configuration, and `SubjectInheritingThread`. It protects RPC client connection caching behavior where socket factory identity participates in cache keys.

## Risks And Test Signals

Risks include equality/hash changes collapsing distinct factories, hangs in server startup/shutdown, proxy configuration not normalizing factory equality, and socket overload regressions. Signals are map size/removal checks, successful uppercase echo through all create methods, proxy equality assertions, and absence of server-thread errors.
