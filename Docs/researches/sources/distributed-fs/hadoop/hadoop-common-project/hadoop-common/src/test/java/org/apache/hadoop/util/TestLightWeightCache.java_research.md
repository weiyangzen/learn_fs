# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestLightWeightCache.java

Purpose: randomized differential tests for `LightWeightCache`, a memory-conscious expiring cache backed by lightweight linked entries.

Important APIs and types: `LightWeightCache<K,E>`, `LightWeightCache.Entry`, `GSet`, `GSetByHashMap`, `FakeTimer`, `Time`, `put`, `get`, `contains`, `remove`, `clear`, `iterator`, `isExpired`, and entry expiration accessors.

Control flow: the main test runs combinations of table length, creation expiration, access expiration, data size, modulus, and size limit. `check` performs staged put, remove-and-put, remove, and repopulate cycles. `LightWeightCacheTestCase` mirrors cache operations into a non-evicting `GSetByHashMap`, advances fake time randomly, occasionally iterates the cache, and checks contains/get semantics against expired entries.

State and persistence: all state is in memory. Expiration state lives on each `IntEntry`; fake monotonic time controls eviction deterministically enough for assertions while random data exercises collision paths.

Dependencies and integration points: integrates Hadoop lightweight `GSet` contracts, fake timers, comparable entries, and randomized test data.

Risks: eviction can drop live entries, retain expired entries incorrectly, exceed size limits, corrupt linked buckets, or return stale replacements. Test signals include differential assertions against the reference map, cache size bounds, iterator/get consistency, and explicit zero-size checks after removals.
