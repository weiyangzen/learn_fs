# File Research: sources/cow-pools/bcachefs-tools/fs/btree/key_cache_types.h

## Purpose
`key_cache_types.h` defines the persistent per-filesystem key-cache container and its hash key type.

## Main Types
- `struct bch_fs_btree_key_cache`: owns the rhashtable, shrinker, shrink iterator, two RCU pending queues, per-CPU pending counters, atomic key/dirty counts, and shrinker statistics.
- `struct bkey_cached_key`: packed/aligned hash key consisting of btree ID and bpos.

## Important Behaviors
- Pending queues are split by whether cached locks use per-CPU readers.
- `nr_keys` and `nr_dirty` are atomics used for cache pressure decisions and shutdown validation.
- Shrinker stats distinguish freed entries from dirty, recently accessed, and lock-failed skips.

## Dependencies and Coupling
- Includes `util/rcu_pending.h` and is consumed by `key_cache.h/.c` and broader filesystem btree state.

## Research Notes
- The type file makes clear that key-cache lifecycle is both hash-table based and RCU-delayed; readers of `key_cache.c` should track both dimensions.
