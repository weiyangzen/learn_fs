# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/FastSaslClientFactory.java


Purpose: `FastSaslClientFactory` caches available JVM `SaslClientFactory` instances by mechanism to avoid repeatedly enumerating security providers during RPC authentication.

Important APIs and types: It implements `SaslClientFactory`, stores `Map<String, List<SaslClientFactory>> factoryCache`, exposes cached mechanism names, and creates the first non-null `SaslClient` for the requested mechanisms.

Control flow and state: The constructor enumerates `Sasl.getSaslClientFactories()` once using the supplied props and populates the cache. `createSaslClient()` walks requested mechanisms in order, then factories for that mechanism, returning the first client that can be created.

Dependencies and integration: It depends on Java SASL and JAAS `CallbackHandler`. It is used by `SaslRpcClient` as a static factory for DIGEST/Kerberos client creation.

Risks and test signals: Provider changes after construction are not visible. Tests should cover mechanism ordering, null factory results, empty mechanisms, and behavior when provider lists differ by props.
