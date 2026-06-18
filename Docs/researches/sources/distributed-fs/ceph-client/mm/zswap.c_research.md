# sources/distributed-fs/ceph-client/mm/zswap.c

## Purpose
`mm/zswap.c` implements zswap, a compressed RAM cache for pages being swapped out. It intercepts swap writeout, compresses each page into a zsmalloc pool, indexes entries by swap offset, serves swapins from RAM, and writes cold entries back to the real swap device under pressure.

## Important APIs, types, and functions
Public MM integration functions include `zswap_is_enabled()`, `zswap_never_enabled()`, `zswap_total_pages()`, `zswap_store()`, `zswap_load()`, `zswap_invalidate()`, `zswap_swapon()`, `zswap_swapoff()`, `zswap_lruvec_state_init()`, `zswap_folio_swapin()`, and `zswap_memcg_offline_cleanup()`. Important types are `struct zswap_pool`, `struct zswap_entry`, and `struct crypto_acomp_ctx`. Tunables are module parameters `enabled`, `compressor`, `max_pool_percent`, `accept_threshold_percent`, and `shrinker_enabled`.

## Control flow
`zswap_setup()` creates the entry cache, CPU hotplug state for per-CPU compression contexts, shrink workqueue, memcg-aware list_lru, shrinker, and an initial compressor pool. Compressor parameter changes create or reuse pools and switch the current pool through the RCU-protected `zswap_pools` list, using `percpu_ref` to retire old pools after entries drain.

`zswap_store()` checks enablement, memcg zswap allowance, pool limits, and list_lru allocation. For each base page in the folio, `zswap_store_page()` allocates metadata, compresses or stores incompressible data through zsmalloc, inserts it into the swap xarray, frees stale entries, charges objcg memory, and adds the entry to the LRU. On failure or disablement it invalidates stale entries so writeback cannot later overwrite newer swap data.

`zswap_load()` looks up the swap xarray entry, rejects large folios, decompresses into the locked swapcache folio, marks it uptodate and dirty, erases the zswap entry, frees metadata/storage, and unlocks the folio. The shrinker walks the global LRU by memcg/node, gives referenced entries a second chance, then calls `zswap_writeback_entry()` to allocate swapcache, validate the xarray pointer, decompress, erase the entry, and issue `__swap_writepage()`.

## State and persistence
State is volatile: zswap entries in per-swap-type xarrays, compressed objects in zsmalloc pools, per-CPU crypto contexts, pool refs/list, global and memcg list_lru membership, objcg charges, debugfs counters, and rejection/writeback statistics. Swap devices remain persistent storage; zswap is only an in-memory cache and invalidates entries on swapoff or successful load/writeback.

## Dependencies and integration points
zswap depends on swapcache/swap device APIs, xarray, crypto acomp, zsmalloc, memcg/objcg zswap charging, list_lru, shrinkers, CPU hotplug, workqueues, debugfs, vm events (`ZSWPIN`, `ZSWPOUT`, `ZSWPWB`), and the folio swap path.

## Risks and invariants
The xarray entry must match the swap slot being loaded or written back; pointer revalidation prevents stale compressed data from overwriting newer swap content. Large folios are not supported on load. Pool lifetime depends on correct `percpu_ref` get/put and RCU removal. The lock ordering is `zswap_tree.lock` before pool LRU lock except writeback’s validated exception. Compression failure accounting is approximate by design.

## Test signals
Run swap workloads with zswap enabled/disabled, compressor changes at runtime, memcg writeback disabled/enabled, pool limit pressure, swapoff, CPU hotplug, and shrinker-triggered writeback. Observe `/sys/module/zswap/parameters/*`, debugfs `zswap/*`, vmstat `zswpin/zswpout/zswpwb`, objcg events, no stale-data warnings, and no decompression failures.
