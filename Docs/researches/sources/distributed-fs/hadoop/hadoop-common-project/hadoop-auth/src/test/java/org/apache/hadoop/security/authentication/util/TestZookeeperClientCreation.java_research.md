# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestZookeeperClientCreation.java

Purpose: Tests `ZookeeperClient` builder/configurer behavior by spying on Curator `CuratorFrameworkFactory.Builder` and verifying default and customized values for connection, namespace, timeouts, retry policy, ACLs, SASL, and SSL.

Important APIs and control flow: `setup()` creates a spy `ZookeeperClient.configure()`, sets connection string `dummy`, and stubs `createFrameworkFactoryBuilder()`. Positive tests call fluent methods such as `withConnectionString`, `withZookeeperFactory`, `withNamespace`, `withSessionTimeout`, `withConnectionTimeout`, `withRetryPolicy`, `withAuthType("sasl")`, `enableSSL`, `withKeystore`, and `withTruststore`, then verify builder calls. Negative tests assert null/invalid auth, missing SASL keytab/principal/login-entry, and incomplete SSL configuration. Helper methods verify defaults: namespace null, `ConfigurableZookeeperFactory`, 60000 ms session timeout, 15000 ms connection timeout, `ExponentialBackoffRetry(1000,3)`, `DefaultACLProvider`, and default `ZKClientConfig`.

State and dependencies: tests mutate system properties for Curator timeout defaults, Java vendor, ZooKeeper login context, and JAAS `Configuration`; SASL helper restores JAAS and vendor. Dependencies include Curator, ZooKeeper client SSL config, AssertJ, Mockito, and JAAS.

Integration points: this is the configuration contract for ZooKeeper-backed signer providers and other Hadoop-auth ZooKeeper clients. SASL tests assert owner-only ACLs using principal primary name and JAAS login module selection for IBM vs non-IBM Java. SSL tests assert Netty secure client settings and keystore/truststore properties.

Risks and test signals: some tests set system properties and clear them manually; exceptions before cleanup could leak properties. The builder-spy pattern verifies configuration calls rather than opening a real client. Error-message equality is intentionally strict and can break on wording changes.
