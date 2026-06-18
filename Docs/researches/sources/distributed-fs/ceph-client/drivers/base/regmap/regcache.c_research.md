# sources/distributed-fs/ceph-client/drivers/base/regmap/regcache.c

## Purpose
This file is the shared regcache orchestration layer. It selects cache backends, owns default-value preparation, exposes cache read/write/sync/drop/control APIs, manages dirty/bypass/cache-only state, applies register patches, and provides common block-sync and value-format helpers used by cache backends.

## Important APIs, Types, And Functions
Exports include `regcache_sort_defaults()`, `regcache_sync()`, `regcache_sync_region()`, `regcache_drop_region()`, `regcache_cache_only()`, `regcache_mark_dirty()`, `regcache_cache_bypass()`, and `regcache_reg_cached()`. Internal/public-to-regmap helpers include `regcache_init()`, `regcache_exit()`, `regcache_read()`, `regcache_write()`, `regcache_reg_needs_sync()`, `regcache_set_val()`, `regcache_get_val()`, `regcache_lookup_reg()`, `regcache_sync_val()`, and `regcache_sync_block()`.

## Control Flow And State
`regcache_init()` validates defaults, selects a backend from `cache_types`, copies explicit defaults or derives defaults from raw defaults/hardware, sets max-register when needed, initializes and populates the backend, and handles cleanup on errors. `regcache_hw_init()` can read all raw registers from hardware or individual readable/nonvolatile registers to build defaults. Reads and writes skip volatile registers. `regcache_sync()` locks the map, restores initial bypass state on exit, writes patches first, syncs either through backend-specific sync or default register iteration, clears `cache_dirty` on success, resets `no_sync_defaults`, and rewrites selector registers for paged maps. Region sync is the bounded equivalent.

`cache_only` means API writes update only cache; `cache_bypass` means writes target hardware only. `regcache_mark_dirty()` sets `cache_dirty` and `no_sync_defaults` after reset/power loss. Block sync chooses raw writes for contiguous ranges when the bus supports them and single writes otherwise.

## Dependencies And Integration Points
This file depends on backend ops from flat/rbtree/maple, `regmap` core IO (`_regmap_write`, `_regmap_raw_write`, `regmap_read`, `regmap_raw_read`), tracepoints, bsearch/sort helpers, range-tree paging selectors, and map locks.

## Risks And Test Signals
Risks include stale defaults, failing to restore bypass/async state on errors, incorrect default skipping after reset, volatile/writeable filtering errors, patch write failures, selector-cache mismatch in paged maps, and raw block boundary mistakes. Test signals include regmap KUnit cache tests, dirty/sync/default skip cases, cache-only/bypass warnings, volatile register cache rejection, hardware-read default generation, patch application failures, and async/raw-write completion checks.
