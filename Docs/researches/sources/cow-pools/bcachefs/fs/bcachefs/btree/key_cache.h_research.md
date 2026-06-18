# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/key_cache.h

## Role

This header declares the btree key cache API and defines dirty-cache pressure thresholds.

## Dirty Pressure Helpers

- `bch2_nr_btree_keys_need_flush()` returns the dirty count above `1024 + nr_keys / 2`; this is used to decide when to kick journal reclaim.
- `bch2_btree_key_cache_must_wait()` uses a higher threshold of `4096 + 3/4 nr_keys` for mandatory throttling.
- `bch2_btree_key_cache_wait_done()` uses a lower threshold of `2048 + 5/8 nr_keys` as the hysteresis condition for wait completion.

## Exported Operations

The header exports journal flush, read-only flush, cache lookup, cached path traversal, cached insert, cache drop, filesystem init/exit, diagnostic text output, and global slab init/exit.

These declarations connect the cache to iterator traversal, update commit, journal reclaim, and filesystem lifecycle code.
