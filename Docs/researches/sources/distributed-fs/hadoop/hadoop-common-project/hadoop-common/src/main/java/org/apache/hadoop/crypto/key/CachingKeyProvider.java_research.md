# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/CachingKeyProvider.java

## Purpose
`CachingKeyProvider` wraps another `KeyProvider` with short-lived Guava caches for key versions, current keys, and metadata. It reduces burst load on backing providers such as KMS while preserving the `KeyProvider` interface.

## Important APIs and types
The class extends `KeyProviderExtension<CacheExtension>`. `CacheExtension` owns three `LoadingCache` instances: `keyVersionCache`, `currentKeyCache`, and `keyMetadataCache`. Public overrides include `getCurrentKey()`, `getKeyVersion()`, `getMetadata()`, `deleteKey()`, `rollNewVersion()`, and `invalidateCache()`.

## Control flow
Cache loaders delegate to the wrapped provider. If the provider returns null, loaders throw internal `KeyNotFoundException`; public getters translate that back to null. Other loader exceptions are unwrapped to `IOException` where possible. Mutating operations delegate to the wrapped provider and then invalidate affected cache entries. Since version-to-base-key mapping is not tracked, version cache invalidation uses `invalidateAll()` on delete and key invalidation.

## State and persistence
State is entirely in-memory cache state. It does not persist key material and relies on the wrapped provider for persistence. Cache expiry is constructor-driven: key versions and metadata expire after access; current keys expire after write.

## Dependencies and integration points
It depends on Hadoop's `KeyProviderExtension` pattern and relocated Guava cache classes. It is useful in front of remote providers where repeated metadata/current-key lookups are expensive.

## Risks
Current-key caching can temporarily return stale key versions until expiry or explicit invalidation. The version cache is coarse-invalidated because it lacks reverse indexes, which is safe but can reduce cache efficiency. Loader null translation relies on wrapping nulls as exceptions because Guava loading caches do not cache null values.

## Test signals
Tests should verify cache hits avoid backing calls, null provider responses return null, `IOException` propagation is preserved, roll/delete/invalidate clear appropriate caches, and expiry semantics differ between current-key and metadata/version caches.
