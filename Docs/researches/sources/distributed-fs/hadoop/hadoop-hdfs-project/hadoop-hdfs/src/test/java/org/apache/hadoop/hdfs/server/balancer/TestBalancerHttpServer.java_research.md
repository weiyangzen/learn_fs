# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerHttpServer.java

## Purpose
`TestBalancerHttpServer` verifies that the balancer HTTP server honors the configured HTTP policy and binds/connects correctly. In this test, HTTP is enabled and HTTPS is configured but expected not to be reachable under `HTTP_ONLY`.

## Important APIs, Types, and Functions
The file uses `BalancerHttpServer`, `DFSConfigKeys.DFS_HTTP_POLICY_KEY`, `DFS_BALANCER_HTTP_ADDRESS_KEY`, `DFS_BALANCER_HTTPS_ADDRESS_KEY`, `HttpConfig.Policy.HTTP_ONLY`, `URLConnectionFactory`, `KeyStoreTestUtil`, and `NetUtils.getHostPortString`. `checkConnection` performs the actual URL open/connect/read probe.

## Control Flow
`setUp` creates a temp base directory, configures balancer HTTP and HTTPS bind addresses to `localhost:0`, generates SSL config even though the policy is HTTP-only, and creates a default URL connection factory. `testHttpServer` starts `BalancerHttpServer`, asserts an HTTP connection succeeds against `getHttpAddress`, asserts an HTTPS connection fails or has no address, and stops the server in `finally`.

## State and Persistence Behavior
State includes generated keystore material under the temp directory, static test configuration, and a running server socket during the test. The server is explicitly stopped, and SSL/test directories are cleaned after all tests.

## Dependencies and Integration Points
The test integrates the balancer's web server wrapper with Hadoop HTTP policy configuration, SSL test utilities, and Java URL connection behavior. It validates externally observable server reachability rather than internal fields.

## Risks and Test Signals
Risks include free-port binding races, localhost resolution differences, connection timeout slowness, and false negatives if `conn.getContent()` behavior changes. Signals are AssertJ truth checks: HTTP must connect, HTTPS must not connect under the selected policy.
