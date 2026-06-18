# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java8/org/apache/hadoop/hdfs/TestDFSClientFailover.java

## Purpose
`TestDFSClientFailover` validates HDFS HA client failover behavior, logical URI handling, connect-timeout failover, DNS avoidance for logical nameservices, legacy failover proxy wrapping, and IP failover proxy logical-URI rules.

## Important APIs, types, and functions
- `setUpCluster()` starts a simple HA MiniDFSCluster and transitions NameNode 0 active.
- `testDfsClientFailover()` writes a file, shuts down active NN0, transitions NN1 active, and verifies the same client can read status after failover.
- `InjectingSocketFactory` spies sockets and throws `ConnectTimeoutException` for a configured NameNode port.
- `spyOnNameService()` reflectively replaces Sun JDK `InetAddress.nameServices[0]` with a Mockito delegate spy, aborting if unsupported.
- DNS tests verify `FileSystem`, `FileContext`, and proxy creation do not resolve logical nameservice hostnames.
- `DummyLegacyFailoverProxyProvider` implements old `FailoverProxyProvider` for wrapping tests.

## Control flow
Each test starts with a fresh HA cluster. Failover tests configure failover file systems, write or create paths, kill/activate NameNodes, and assert behavior. Misconfiguration tests create logical URIs with missing addresses or forbidden ports and assert helpful exceptions. DNS tests install the name-service spy, perform filesystem/proxy operations, and verify no lookup for the logical host. Proxy-provider tests configure legacy or IP providers and assert `HAUtil.useLogicalUri` outcomes.

## State and persistence behavior
The MiniDFSCluster stores `/tmp/failover-test-file` and HA NameNode state per test. `clearConfig()` resets `SecurityUtil.setTokenServiceUseIp(true)` after each test. `spyOnNameService()` mutates JDK-global DNS service list and does not explicitly restore it in this file, which is a notable process-global test hook.

## Dependencies and integration points
It integrates HA MiniDFSCluster topology, `HATestUtil`, `NameNodeProxies`, `NameNodeProxiesClient`, `ConfiguredFailoverProxyProvider`, `IPFailoverProxyProvider`, DFS client config keys, socket factories, Java DNS internals, Mockito, and Java 8 `sun.net.spi.nameservice.NameService`.

## Risks and edge cases
This file lives under `src/test/java8` because it depends on JDK-internal DNS APIs that are not portable across later Java runtimes. DNS spying skips tests on incompatible JDKs but can leak global DNS mock state after success. Connect-timeout failover is sensitive to socket-factory configuration and mocked socket behavior.

## Test signals
Passing confirms HA clients fail over after active NameNode loss and connect timeouts, logical URIs reject explicit ports, misconfigured HA addresses produce actionable errors, logical nameservices are not DNS-resolved, legacy providers still trigger logical-token-service behavior, and IP failover providers do not require logical URIs.
