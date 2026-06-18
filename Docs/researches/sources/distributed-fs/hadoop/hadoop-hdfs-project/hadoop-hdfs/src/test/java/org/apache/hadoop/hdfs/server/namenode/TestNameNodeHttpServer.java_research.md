# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeHttpServer.java

## Purpose
Parameterized tests for `NameNodeHttpServer` honoring HTTP policy modes: HTTP only, HTTPS only, and both HTTP/HTTPS.

## Important APIs, Types, and Functions
- JUnit parameterized class with method source `policy()` returning `HttpConfig.Policy` values.
- Uses `KeyStoreTestUtil.setupSSLConfig`, `URLConnectionFactory.newDefaultURLConnectionFactory`, and DFS SSL resource keys.
- Starts `NameNodeHttpServer(conf, null, addr)` and verifies `getHttpAddress`, `getHttpsAddress`, and reachability through `URLConnection`.

## Control Flow
- `BeforeAll` creates a temp base dir, SSL keystore/conf files, connection factory, and DFS client/server keystore resource settings.
- For each policy, `testHttpPolicy` sets `DFS_HTTP_POLICY_KEY`, binds HTTPS address to `localhost:0`, starts a server, and checks enabled schemes are reachable while disabled schemes have null addresses.
- `tearDown` deletes temp dirs and SSL config.

## State and Persistence Behavior
- Persists temporary SSL config/keystore files under the test base directory and classpath SSL config dir.
- HTTP server bind addresses are ephemeral ports.

## Dependencies and Integration Points
- Integrates NameNode HTTP server construction, Hadoop HTTP policy config, SSL setup, URL connection factory, and NetUtils host:port formatting.

## Risks and Edge Cases
- `canAccess` catches all exceptions and returns false, so failures require policy assertions to identify reachability issues.
- Network bind/reachability can be environment-sensitive.
- Static shared `Configuration` is mutated per parameterized instance.

## Test Signals
- Good signal that configured HTTP/HTTPS endpoints are enabled or disabled consistently with policy and are actually reachable.
