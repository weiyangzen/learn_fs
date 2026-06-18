# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestZKSignerSecretProvider.java

Purpose: Integration tests for `ZKSignerSecretProvider`, validating ZooKeeper-backed shared signing-secret initialization, rollover, upgrade from older secret lengths, and coordination between multiple provider instances.

Important APIs and control flow: `@BeforeEach` starts a Curator `TestingServer`; tests configure `ZOOKEEPER_CONNECTION_STRING` and `ZOOKEEPER_PATH`. Like the random provider test, `MockZKSignerSecretProvider` overrides scheduled `rollSecret()` for Mockito verification and exposes `realRollSecret()`. `testOne` verifies single-provider current/previous secrets. `testUpgradeChangeSecretLength` seeds ZooKeeper with an old provider that generates stringified `long` secrets, then initializes the new provider and verifies preserved old secrets plus later 32-byte generated secrets. `testMultiple` initializes two providers with different seeds and tests race winners for coordinated rolls.

State and dependencies: persistent test state is the ZooKeeper znode data under `/secret`; runtime state includes background schedulers and provider local caches. Dependencies include Curator `TestingServer`, servlet context mocks, Mockito, Log4j, and Java `Random`.

Integration points: covers distributed secret sharing for authentication filters across multiple servers. It validates that all providers converge to the same secret window and that old secret-length data remains readable through upgrade.

Risks and test signals: tests are timing-sensitive through scheduler verification and rely on deterministic interleaving via manual `realRollSecret()` calls. Multi-provider scenarios intentionally model write races and should catch optimistic-lock/versioning regressions in znode updates.
