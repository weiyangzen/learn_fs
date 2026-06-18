<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/DelegationTokenLoadingCache.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/DelegationTokenLoadingCache.java

Source read size: 118 lines, 3478 bytes.

## Purpose
Map-like wrapper around a Guava `LoadingCache` for delegation-token metadata. It lets SQL-backed secret managers avoid loading every token into memory while preserving the `currentTokens` map contract expected by the base manager.

## Important APIs, Types, and Functions
The constructor configures `expireAfterWrite`, `maximumSize`, and a `CacheLoader` backed by a `Function<K,V>`. Implemented `Map` methods include `size()`, `isEmpty()`, `containsKey()`, `get()`, `put()`, `remove()`, `putAll()`, `clear()`, `keySet()`, `values()`, and `entrySet()`. `containsValue()` is intentionally unsupported.

## Control Flow, State, and Persistence Behavior
`get()` invokes the loader on a miss and returns null on any loader exception. `containsKey()` only checks present cache entries and does not trigger loading. `entrySet()` and related views expose only cached entries, not the entire persistent store. Persistent data remains in the backing store used by the supplied function.

## Dependencies and Integration Points
Used by `SQLDelegationTokenSecretManager` as its `currentTokens` implementation. Depends on Hadoop's shaded Guava cache and Java functional interfaces.

## Risks and Test Signals
Risks include subtle differences from a full `Map`: cleanup scans only cached entries unless SQL overrides candidate cleanup, `get()` hides loader failures, and `size()` is approximate/cast to int. Test cache miss loading, expiry eviction, max-size eviction, put/remove invalidation, `containsKey()` no-load behavior, unsupported `containsValue()`, and SQL manager cancellation loading a token before base validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/DelegationTokenLoadingCache.java -->
