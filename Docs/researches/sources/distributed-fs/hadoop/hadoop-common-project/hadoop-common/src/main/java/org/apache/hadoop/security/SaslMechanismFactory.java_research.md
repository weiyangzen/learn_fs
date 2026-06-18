# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslMechanismFactory.java


Purpose: `SaslMechanismFactory` resolves the effective Hadoop SASL mechanism, allowing an environment variable to override configuration.

Important APIs and types: It exposes `getMechanism()`, `isDefaultMechanism(String)`, `isDigestMechanism(String)`, and a `main()` printer. It uses `HADOOP_SASL_MECHANISM`, `hadoop.security.sasl.mechanism`, and the configured default.

Control flow and state: The resolved mechanism is stored in a volatile static field. `getMechanism()` returns the cached value or synchronizes to read environment and a new `Configuration`, with environment taking precedence over config and config over default.

Dependencies and integration: It depends on Hadoop configuration defaults and SLF4J. SASL client/server setup can use it to choose DIGEST variants or default mechanisms.

Risks and test signals: Tests should cover env precedence, config default, cache behavior, and digest-prefix detection. Static caching means changes to environment or configuration after first access are ignored.
