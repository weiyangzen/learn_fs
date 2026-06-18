# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/KeyProviderCache.java

`KeyProviderCache` caches `KeyProvider` instances by URI, closes providers on eviction, and invalidates all cached providers during JVM shutdown.

The constructor builds a Guava cache with `expireAfterAccess`, a removal listener that closes providers, and a shutdown hook. `get(Configuration, URI)` returns null for null URI, otherwise returns or creates a provider with `KMSUtil.createKeyProviderFromUri()`. `invalidateCache()` is testing-visible, `setKeyProvider()` injects a provider under the configured URI, and `createKeyProviderURI()` parses `hadoop.security.key.provider.path`.

State is an in-memory `Cache<URI, KeyProvider>` with process-local lifetime. Eviction and invalidation close providers through the listener. Dependencies include Hadoop relocated Guava cache, `KMSUtil`, `ShutdownHookManager`, `FileSystem.SHUTDOWN_HOOK_PRIORITY`, and `CommonConfigurationKeysPublic`.

Risks include `get()` swallowing creation exceptions and returning null, close failures being logged but not propagated, and `setKeyProvider()` relying on assertions around parsed URI. Test signals include provider reuse, expiry close, invalidation, null URI behavior, malformed URI handling for injection, shutdown hook behavior, and provider creation failure.
