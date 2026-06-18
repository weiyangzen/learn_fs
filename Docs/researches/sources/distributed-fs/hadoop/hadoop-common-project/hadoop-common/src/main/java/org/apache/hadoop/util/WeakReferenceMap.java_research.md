# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/WeakReferenceMap.java

Purpose: `WeakReferenceMap<K,V>` maps keys to weakly referenced values and recreates values on demand, offering an alternative to long-lived strong maps or `ThreadLocal` storage where values may be reclaimed by GC.

Important APIs/types/functions: constructor accepts a non-null factory and optional `referenceLost` callback. `get(K)` resolves current value, removes and reports cleared references, then calls `create`. `create(K)` builds a strong local value, stores it as a weak reference, retrieves and resolves the map value, and retries if GC or a race loses the value during creation. `put`, `remove`, `containsKey`, `lookup`, `resolve`, `prune`, `clear`, `size`, `getReferenceLostCount`, and `getEntriesCreatedCount` provide map operations and counters.

Control flow: reads use `ConcurrentHashMap`. `get` first resolves without locking; on cleared weak reference it conditionally removes the old reference and calls `noteLost`. Creation increments a counter, requires a non-null factory result, writes a new weak reference, retrieves the current map entry, and loops if the resolved value is null. `prune` iterates the concurrent map and removes entries whose weak references have cleared.

State and persistence behavior: state is in-memory only: a concurrent map of weak references, factory callback, optional loss callback, atomic counters, and a `LogExactlyOnce` for creation-time reference loss. Values can disappear whenever no strong references exist outside the map.

Dependencies and integration points: depends on Java weak references, concurrent collections, atomics, Java functional interfaces, SLF4J, `LogExactlyOnce`, and Hadoop audience annotations. It is intended for cache-like integration points where recreation is acceptable.

Risks: map `size()` includes cleared weak references until get/remove/prune cleans them. Concurrent `create` calls for the same key can construct multiple values; the last put wins and losers may be discarded. Callback side effects run synchronously in caller threads. Values must tolerate recreation and identity changes. `put(key, null)` stores a weak reference to null and subsequent `get` creates a new value.

Test signals: tests should force GC-cleared references, verify `prune` and lost counters/callbacks, exercise concurrent creates, assert non-null factory enforcement, and verify returned value matches the current map value under races.
