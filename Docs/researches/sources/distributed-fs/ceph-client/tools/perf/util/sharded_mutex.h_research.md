# sources/distributed-fs/ceph-client/tools/perf/util/sharded_mutex.h

`sharded_mutex.h` declares a compact lock-sharding abstraction for perf. It explains the motivation: a mutex per object can be memory-expensive, so objects with stable hashes can share a global pool of mutexes, accepting collisions when the shard count is too small.

The main type is `struct sharded_mutex`, containing `cap_bits` and a flexible array `struct mutex mutexes[]`. The mutex array size is `1 << cap_bits`, allowing fast hash masking through `hash_bits()`.

Public APIs are `sharded_mutex__new(size_t num_shards)`, `sharded_mutex__delete(struct sharded_mutex *sm)`, and the inline `sharded_mutex__get_mutex(struct sharded_mutex *sm, size_t hash)`. The getter returns `&sm->mutexes[hash_bits(hash, sm->cap_bits)]`, so callers can lock the returned mutex using the normal perf mutex API.

State is owned by the heap allocation created in the C file. The header does not track object-to-lock ownership; correctness depends on callers using the same hash for related critical sections and avoiding deletion while locks may still be used.

Dependencies are `mutex.h` and `hashmap.h` for the mutex type and `hash_bits()`. Integration points are shared perf containers or caches that need coarse but scalable synchronization.

Risks include collision-induced contention, deadlocks if callers acquire multiple shard mutexes without a consistent order, invalid access after deletion, and poor behavior if `cap_bits` is derived from an unsuitable shard count. The flexible-array layout ties allocation and initialization tightly to `sharded_mutex__new()`.

Test signals include deterministic mapping for known hashes, concurrent callers sharing identical hashes, contention under intentionally small shard counts, and static/build checks that the flexible-array allocation matches the header layout.
