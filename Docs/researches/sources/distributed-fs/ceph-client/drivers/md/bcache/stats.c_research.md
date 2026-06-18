# sources/distributed-fs/ceph-client/drivers/md/bcache/stats.c

Purpose: implements cache accounting and sysfs exposure for total and rolling cache hit/miss, bypass, collision, and bypassed-sector statistics.

Important APIs/functions: `bch_cache_accounting_init()` initializes kobjects, closure, and periodic timer. `bch_cache_accounting_add_kobjs()` adds `stats_total`, `stats_five_minute`, `stats_hour`, and `stats_day` under a parent kobject. `bch_cache_accounting_destroy()` removes kobjects and synchronizes timer shutdown. `bch_cache_accounting_clear()` clears totals. `bch_mark_cache_accounting()`, `bch_mark_cache_miss_collision()`, and `bch_mark_sectors_bypassed()` increment per-device and per-cache-set collectors. The sysfs `SHOW(bch_stats)` method prints counters, hit ratio, and human-readable bypassed bytes.

Control flow: request paths increment cheap atomic counters in `acc->collector`. Every `accounting_delay`, `scale_accounting()` atomically drains collectors, left-shifts values by 16, adds them into total and rolling windows, rescales five-minute/hour/day windows at configured intervals using EWMA decay, and rearms the timer unless closing. Destroy sets `closing`, deletes the timer synchronously, and returns the accounting closure if it stopped a pending timer.

State and persistence: all state is in memory under `struct cache_accounting`; no on-disk persistence. Counters are exported through sysfs kobjects and are reset on device lifecycle or explicit clear of totals. Rolling statistics use shifted fixed-point representation to reduce rounding error.

Dependencies/integration: depends on `bcache.h`, `stats.h`, `btree.h`, `sysfs.h`, kobjects, timers, atomics, closures, and request accounting calls. Both cached device and cache set accounting are updated for each relevant event.

Risks/test signals: timer shutdown and closure return ordering matter during device teardown. `scale_stats(&acc->total, 0)` relies on the preincrement comparison never matching zero, so totals do not decay; this should be intentional and tested. Concurrent sysfs reads during timer updates are not heavily synchronized. Test hit/miss/bypass accounting, five-minute/hour/day decay, clear semantics, destroy while timer pending, and byte conversion for bypassed sectors.
