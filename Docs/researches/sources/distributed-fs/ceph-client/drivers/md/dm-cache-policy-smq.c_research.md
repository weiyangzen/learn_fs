# sources/distributed-fs/ceph-client/drivers/md/dm-cache-policy-smq.c

## Purpose
`dm-cache-policy-smq.c` implements the stochastic multi-queue cache replacement policy for DM cache. It decides cache hits, promotions, demotions, and writebacks using multi-level queues for cache and hotspot entries, periodic hit sampling, sentinels for age thresholds, and a background-work tracker.

## Important APIs, Types, and Functions
Core data structures are `struct entry`, `struct entry_space`, `struct ilist`, `struct queue`, `struct stats`, `struct smq_hash_table`, `struct entry_alloc`, and `struct smq_policy`. The policy vtable functions are `smq_lookup()`, `smq_lookup_with_work()`, `smq_get_background_work()`, `smq_complete_background_work()`, `smq_set_dirty()`, `smq_clear_dirty()`, `smq_load_mapping()`, `smq_invalidate_mapping()`, `smq_get_hint()`, `smq_residency()`, `smq_tick()`, `smq_allow_migrations()`, and destroy/config helpers. Module init registers policy types `smq`, `mq`, `cleaner`, and alias `default`.

## Control Flow
Lookup first checks the cache hash table. Hits update cache statistics, requeue the entry upward once per tick period, and return the inferred cblock. Misses update the hotspot queue keyed by a larger hotspot block, assess whether the hotspot level crosses read/write promotion thresholds, and possibly queue promotion work. Background work retrieval first issues already queued work; if idle or cleaner mode needs more clean blocks, it queues writeback before issuing. Completion clears pending state and either installs promoted mappings, frees demoted entries, or requeues writeback entries.

## State and Persistence
SMQ state is volatile policy state protected by `mq->lock`: cache entries, hotspot entries, clean/dirty queues, hash tables, hit bitsets, queue statistics, sentinel generation flags, migration flags, and the background tracker. Persistence is indirect: `smq_load_mapping()` restores mappings and dirty state from metadata, and `smq_get_hint()` returns an entry level that metadata can persist as a 32-bit policy hint. Registered policy type versions and hint size form the compatibility identity for persisted hints.

## Dependencies and Integration Points
The policy uses the background tracker, cache policy internal wrappers, typed block APIs, Linux hashing/jiffies/vmalloc/math helpers, and DM policy registration. The cache target calls the policy vtable to map I/O, request background migrations, mark dirty/clean state after writes or writebacks, load mappings from metadata, and save hints on commit.

## Risks and Edge Cases
The implementation is lock-sensitive: nearly all policy mutation must happen under the spinlock, while `smq_load_mapping()` is intended for single-threaded load. The code has an explicit FIXME in `smq_invalidate_mapping()` for invalidating blocks with pending background work. Promotion allocates the destination cache entry before work starts; failed queueing or failed completion must free it or residency leaks. Cleaner policy disables migrations but tries to clean all dirty entries. The `mq` compatibility policy accepts old tunables but ignores them, so user space may believe knobs still matter unless it reads warnings/status.

## Test Signals
Test signals include cache hit/miss mapping decisions, promotion queueing only above thresholds or for fast writes, demotion when free targets are unmet, writeback when idle/cleaner requires cleaning, completion success and failure for all work types, loading mappings with valid and invalid hints, preserving policy hints across clean shutdown, rejecting duplicate background work, status output for `mq` compatibility tunables, and module registration/unregistration for all aliases.
