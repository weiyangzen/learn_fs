# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/KeyProviderFactory.java

## Purpose
`KeyProviderFactory` discovers and instantiates key providers from URIs configured in Hadoop. It is the service-loader entry point for JCEKS, user, KMS, and other provider implementations.

## Important APIs and types
The class defines `KEY_PROVIDER_PATH` from `hadoop.security.key.provider.path`, abstract `createProvider(URI, Configuration)`, static `getProviders(Configuration)`, and static `get(URI, Configuration)`. A static `ServiceLoader<KeyProviderFactory>` is eagerly iterated to avoid lazy-loading synchronization issues.

## Control flow
`getProviders()` reads all configured provider-path strings, parses each as a URI, calls `get()`, and returns non-null providers. If no factory handles a URI, it throws an `IOException` naming the configuration key. `get()` iterates service-loaded factories until one returns a provider.

## State and persistence
The only state is the static service loader. Created providers own any persistent state.

## Dependencies and integration points
It depends on Java `ServiceLoader`, Hadoop `Configuration`, and provider-specific `Factory` implementations registered through service metadata. `KeyShell`, HDFS encryption-zone setup, and KMS token renewers rely on it.

## Risks
Bad URI syntax fails provider setup at runtime. Service-loader ordering can matter if multiple factories claim the same scheme. Eager static loading can surface provider class initialization errors early.

## Test signals
Tests should cover multiple configured providers, bad URI handling, unknown scheme errors, first-matching factory behavior, and service-loader registration for JCEKS/user/KMS factories.
