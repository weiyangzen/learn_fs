<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestSSLHttpServerConfigs.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestSSLHttpServerConfigs.java

## Purpose
JUnit 5 test suite for HTTPS `HttpServer2` SSL configuration, especially keystore key password, keystore store password, truststore password, and enabled TLS protocol propagation. It complements `TestSSLHttpServer` by using generated test keystores and checking both successful server startup and precise failure causes.

## Important APIs, Types, and Functions
The class uses `HttpServer2.Builder`, `KeyStoreTestUtil.setupSSLConfig`, `SSLFactory.SSL_ENABLED_PROTOCOLS_KEY`, Jetty `ServerConnector`, `SslConnectionFactory`, and `SslContextFactory`. `start()` prepares a clean temp keystore directory, turns on SSL debug logging, stores cipher suite state, and sets a low HTTP max thread count. `shutdown()` deletes temp files, cleans SSL config files, and restores cipher/debug settings. `setupKeyStores()` creates keystore/truststore material with configurable passwords and applies included protocols. `setupServer()` builds a HTTPS-only `HttpServer2` using explicit key/trust store values from `sslConf`. `testServerStart()` starts the server and waits until `server.isAlive()`.

## Control Flow and State
Each test creates fresh `Configuration` objects and filesystem-backed keystore artifacts under `GenericTestUtils.getTempPath`. Positive tests start and stop an HTTPS server. Negative tests intentionally pass null, empty, or incorrect password combinations and assert `IOException` messages or causes. Protocol tests build the server without starting it, inspect the first listener's SSL factory, and assert that include protocols contain only the configured protocol and that the protocol is not also excluded.

## Dependencies and Integration Points
Integrates Hadoop security SSL utilities, Jetty SSL internals, `HttpServer2` builder password handling, and static constants from `TestSSLHttpServer` for cipher/protocol settings. It depends on classpath SSL config output from `KeyStoreTestUtil`.

## Risks and Test Signals
Risk areas are password null-vs-empty semantics, wrong-password diagnostics, temporary global SSL/cipher debug state, and Jetty protocol include/exclude behavior. The suite signals regressions through server startup success, expected `IOException` text, nested cause checks such as `Cannot recover key`, and direct SSL context assertions for default and non-default protocols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestSSLHttpServerConfigs.java -->
