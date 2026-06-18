# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/key_cache_types.h

## Role

This header defines the per-filesystem state and hashtable key type for the btree key cache.

## Data Structures

`struct bch_fs_btree_key_cache` contains:

- the rhashtable and initialization flag
- shrinker pointer and scan cursor
- two `rcu_pending` queues for normal locks and per-CPU-reader locks
- per-CPU pending object counters
- atomic key and dirty-key counters
- shrinker stats for requested/free/skipped cases

`struct bkey_cached_key` is the packed rhashtable lookup key: btree ID plus btree position, aligned to 4 bytes.

## Notable Design

The two pending queues correspond to cached entries with different SIX-lock reader implementations. This avoids reusing an object with the wrong lock flavor after SRCU-delayed free.
