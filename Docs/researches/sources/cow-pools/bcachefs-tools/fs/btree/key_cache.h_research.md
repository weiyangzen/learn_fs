# File Research: sources/cow-pools/bcachefs-tools/fs/btree/key_cache.h

## Purpose
`key_cache.h` declares the btree key-cache API and inline policy helpers for dirty-cache pressure.

## Main Responsibilities
- Defines thresholds for when dirty cached keys should trigger flush pressure (`bch2_nr_btree_keys_need_flush()`), when callers must wait, and when wait is complete.
- Defines rhashtable comparison parameters for cache lookup keyed by btree ID and bpos.
- Provides inline `bch2_btree_key_cache_find()`.
- Declares cached traversal, cached insert/drop, journal flush, read-only flush, filesystem init/exit, text reporting, and global slab init/exit functions.

## Important Behaviors
- Dirty limits scale with total cache size and have hysteresis: kick threshold, must-wait threshold, and wait-done threshold differ.
- The rhashtable key is `struct bkey_cached_key`, and matching requires both identical btree ID and exact bpos equality.

## Dependencies and Coupling
- Includes btree key definitions and references journal, transaction, path, insert-entry, and filesystem key-cache structures.
- Implemented by `key_cache.c`; called by iterator and update/commit paths.

## Research Notes
- The threshold helpers are part of writeback/reclaim behavior, not just telemetry; changes can affect journal pressure and transaction latency.
