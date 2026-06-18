# File Research: sources/block-storage/linux-dm/drivers/md/bcache/stats.c

`stats.c` implements bcache cache-hit and bypass accounting exposed through sysfs. It tracks absolute totals and three rolling windows: five minutes, one hour, and one day. Atomic collectors accumulate hot-path counters, and a timer periodically transfers collector values into shifted counters and rescales EWMAs.

Sysfs attributes include hits, misses, bypass hits, bypass misses, hit ratio, miss collisions, and bypassed bytes. `bch_stats_show()` converts internal fixed-point counters by shifting down 16 bits and computes hit ratio with `DIV_SAFE()`.

`bch_cache_accounting_add_kobjs()` installs `stats_total`, `stats_five_minute`, `stats_hour`, and `stats_day` kobjects under a parent. `bch_cache_accounting_init()` initializes kobjects, closure, timer, and starts periodic accounting. `bch_cache_accounting_destroy()` puts kobjects, marks closing, and coordinates timer completion with the closure.

Hot-path marking helpers update per-device and cache-set collectors: `bch_mark_cache_accounting()` for hit/miss and bypass dimensions, `bch_mark_cache_miss_collision()` for replacement collisions, and `bch_mark_sectors_bypassed()` for bypassed sector totals. `bch_cache_accounting_clear()` resets only total counters; rolling windows are independently decayed by the timer.
