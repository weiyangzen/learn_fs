# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/curator/TestSecureZKCuratorManager.java

Purpose: Tests `ZKCuratorManager` and `HadoopZookeeperFactory` behavior when ZooKeeper client/server communication is configured for SSL/TLS. It also verifies Hadoop's `SecurityUtil.TruststoreKeystore` default and explicit configuration handling.

Important APIs/types/functions: `setup()` builds an Apache Curator `TestingServer` with secure client port settings, creates Hadoop secure config via `setUpSecureConfig()`, and starts a `ZKCuratorManager` with secure mode. `testSecureZKConfiguration()` creates a raw `ZooKeeper` through `HadoopZookeeperFactory`; `validateSSLConfiguration()` inspects `ZKClientConfig`. `testTruststoreKeystoreConfiguration()` validates empty-string normalization and explicit keystore/truststore values.

Control flow: Static secure setup writes ZooKeeper system properties for Netty server connection factory, server-side keystore/truststore, request timeout, `jute.maxbuffer`, SSL debugging, and X509 auth provider, then sets Hadoop `CommonConfigurationKeys` for client truststore/keystore paths. The test creates a secure ZooKeeper client and asserts both configured file/password properties and hard-coded secure-client properties such as `SECURE_CLIENT=true` and Netty client socket class.

State and persistence behavior: Test state includes a temporary ZooKeeper data directory, global JVM system properties, a live Curator testing server, and a `ZKCuratorManager`. `teardown()` closes curator and server, but system properties set in `setUpSecureConfig()` are process-global and may affect later ZooKeeper tests unless overwritten.

Dependencies and integration points: Depends on Apache Curator test server, ZooKeeper Netty server/client classes, Hadoop `Configuration`, `CommonConfigurationKeys`, and `SecurityUtil.TruststoreKeystore`. It validates the TLS configuration bridge from Hadoop config to ZooKeeper client config.

Risks: The test is sensitive to certificate resource paths and uses hard-coded secure port `2281`, which can conflict on shared hosts. Process-global ZooKeeper SSL properties and `javax.net.debug=ssl` can be noisy or leak between tests. Secure startup depends on Netty classes and local test keystore/truststore files being present.

Test signals: Successful secure server startup, exact ZooKeeper client config property values for keystore/truststore, secure client flag and Netty socket class, plus empty-string/default truststore-keystore behavior are the main validation signals.
