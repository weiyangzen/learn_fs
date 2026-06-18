# File Research: sources/block-storage/linux-dm/drivers/md/bcache/stats.h

`stats.h` declares the accounting structures used by cached devices and cache sets. `struct cache_stat_collector` contains atomic hot-path counters for cache hits, misses, bypass hits/misses, miss collisions, and bypassed sectors.

`struct cache_stats` is a sysfs-visible fixed-point snapshot with a kobject, absolute or decayed counters, and a rescale counter. `struct cache_accounting` ties the collector, timer, closure, close flag, and four stats windows together.

The public API covers initialization, sysfs kobject creation, clearing, destruction, and hot-path marking. The header declares `bch_mark_cache_readahead()` even though this grouped source set does not include an implementation in `stats.c`, which is a notable declaration/API mismatch to resolve by checking the wider bcache tree if needed.
