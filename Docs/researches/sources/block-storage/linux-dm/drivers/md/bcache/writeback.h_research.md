# File Research: sources/block-storage/linux-dm/drivers/md/bcache/writeback.h

`writeback.h` defines writeback thresholds, rate-update bounds, fragmentation thresholds, dirty-initialization thread limits, and shared writeback helpers. The default writeback cutoff is 40 percent cache use, sync cutoff is 70 percent, with module-parameter maxima of 70 and 90 respectively.

`struct bch_dirty_init_state` and `struct dirty_init_thrd_info` coordinate multi-threaded dirty-sector initialization during attach. The state tracks the cache set, device, total threads, shared root-key index, lock, started/enough atomics, waitqueue, and per-thread metadata.

Inline helpers sum dirty sectors across stripes, map offsets to stripe indexes with range checking, test whether any stripe covered by a request is dirty, determine whether an incoming write should be handled in writeback mode, wake the writeback thread, and mark a cached device as having dirty data. `should_writeback()` blocks writeback outside writeback cache mode, during detach, above the sync cutoff, and for discards; it forces writeback for expensive partial-stripe overlaps and otherwise considers sync/meta/priority writes or low cache usage.

The header exports writeback cutoff module parameters and declares dirty-sector accounting, dirty initialization, cached-device writeback initialization, and writeback startup functions.
