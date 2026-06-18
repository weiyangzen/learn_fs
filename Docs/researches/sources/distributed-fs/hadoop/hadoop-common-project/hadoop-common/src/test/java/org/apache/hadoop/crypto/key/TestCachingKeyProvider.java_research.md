# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestCachingKeyProvider.java

## Purpose
`TestCachingKeyProvider` validates timeout-based caching and cache invalidation for `CachingKeyProvider`.

## Important APIs, Types, and Functions
The tests mock `KeyProvider` methods `getCurrentKey`, `getKeyVersion`, `getMetadata`, `rollNewVersion`, `rollNewVersion(name, material)`, and `deleteKey`. They instantiate `CachingKeyProvider(mockProv, keyTimeoutMillis, currKeyTimeoutMillis)` and use Mockito call counts to prove cache hits and misses.

## Control Flow
`testCurrentKey()` caches a non-null current key, verifies repeat access avoids the provider, sleeps beyond the configured timeout, and verifies refresh. It also verifies null current keys are not cached. `testKeyVersion()` and `testMetadata()` repeat the same pattern for version and metadata lookups. `testRollNewVersion()` and `testDeleteKey()` populate caches, perform a mutation, then assert subsequent lookups hit the underlying provider again.

## State and Persistence
State is entirely in-memory: mock return values, cache entries, TTLs, and call counters. `KMSMetadata` is used in delete tests to describe the number of cached versions to purge.

## Dependencies and Integration Points
Dependencies include `CachingKeyProvider`, `KeyProvider`, `KMSClientProvider.KMSMetadata`, Mockito, `Configuration`, and JUnit. The tests integrate cache behavior with key lifecycle operations that mutate backing provider state.

## Risks and Edge Cases
Timing-based tests depend on sleeps long enough to exceed TTLs. Null values deliberately bypass caching; this avoids hiding newly created keys but increases backend calls for missing keys. Deletion invalidation must clear current-key, key-version, and metadata caches consistently.

## Test Signals
Passing tests signal cache hits for known values, no caching for unknown keys, TTL expiry refresh, and cache purge on roll and delete.
