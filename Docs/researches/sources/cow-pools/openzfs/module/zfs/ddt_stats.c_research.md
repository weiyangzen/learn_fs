# File Research: sources/cow-pools/openzfs/module/zfs/ddt_stats.c

## Scope

DDT statistics and histogram aggregation. This file computes per-entry dedup stats, maintains histogram buckets, totals DDT object/log usage, caches pool dedup size/savings, reports dedup ratio, and estimates cached DDT footprint.

## Main Interfaces

- Entry/histogram helpers: `ddt_histogram_add_entry()`, `ddt_histogram_sub_entry()`, `ddt_histogram_add()`, `ddt_histogram_total()`, `ddt_histogram_empty()`.
- Object/log usage: `ddt_get_dedup_object_stats()`, `ddt_get_ddt_dsize()`.
- Pool dedup stats: `ddt_get_dedup_histogram()`, `ddt_get_dedup_stats()`, `ddt_get_dedup_dspace()`, `ddt_get_dedup_used()`, `ddt_get_dedup_saved()`, `ddt_get_pool_dedup_ratio()`.
- Cache footprint: `ddt_get_pool_dedup_cached()`.

## State And Control Flow

`ddt_stat_generate()` derives one `ddt_stat_t` from a lightweight DDT entry. It walks all phys variants, skips empty phys births, counts valid DVAs, sums logical/physical/data sizes, multiplies referenced sizes by refcount, and uses `dva_get_dsize_sync()` for allocated size.

Histogram add/sub places each entry in a bucket keyed by `highbit64(ref_blocks) - 1`. Empty or zero-ref entries contribute no bucket. Subtraction asserts the destination has sufficient counts, which catches mismatched histogram lifecycle updates.

`ddt_get_dedup_object_stats()` walks all valid DDTs, store types, and classes. It refreshes object count/dspace/mspace from `dmu_object_info()` and `ddt_object_count()`, then adds in `ddt_log_stats`. It updates `spa_dedup_dsize` with raw on-disk DDT/log footprint. `ddt_get_dedup_histogram()` combines cached store histograms plus the live log histogram. `ddt_get_dedup_dspace()` caches saved space as referenced dsize minus unique stored dsize.

`ddt_get_pool_dedup_cached()` asks each DDT object for L1/L2 cached size via `dmu_object_cached_size()` and returns the total ARC footprint.

## Dependencies

Depends on DDT phys helpers from `ddt.c`, cached DDT/log histograms, DMU object info/cache-size APIs, SPA cached dedup counters, and synchronous DVA size lookup under appropriate config locking.

## Correctness Notes

Store histograms are cached at DDT sync/load time, while log histogram is live. Consumers therefore must combine both to see current dedup stats. Object stats are raw counts, not averaged or ratio-normalized, because zdb and userspace reporting expect raw DDT object totals. The cached `spa_dedup_dspace` and `spa_dedup_dsize` are invalidated by DDT sync paths in `ddt.c`.
