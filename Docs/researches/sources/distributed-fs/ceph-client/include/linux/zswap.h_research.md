# sources/distributed-fs/ceph-client/include/linux/zswap.h

## Purpose
`zswap.h` declares the kernel zswap frontswap-like compressed swap cache interface. It lets memory-management code store swapped folios in a compressed in-memory pool, load them back, invalidate entries, account per-LRU-vector behavior, and participate in swap device on/off and memory-cgroup cleanup. When `CONFIG_ZSWAP` is disabled, the header supplies no-op inline fallbacks so callers can compile without preprocessor-heavy call sites.

## Important APIs, Types, And Data
The global `atomic_long_t zswap_stored_pages` counts pages currently stored by zswap. Under `CONFIG_ZSWAP`, `struct zswap_lruvec_state` contains `atomic_long_t nr_disk_swapins`, a per-lruvec penalty counter for pages that had to be swapped in from disk because they were not found in zswap.

Exported functions are `zswap_total_pages()`, `zswap_store(struct folio *)`, `zswap_load(struct folio *)`, `zswap_invalidate(swp_entry_t)`, `zswap_swapon(int type, unsigned long nr_pages)`, `zswap_swapoff(int type)`, `zswap_memcg_offline_cleanup(struct mem_cgroup *)`, `zswap_lruvec_state_init(struct lruvec *)`, `zswap_folio_swapin(struct folio *)`, `zswap_is_enabled()`, and `zswap_never_enabled()`. Disabled builds replace most with inline stubs: stores fail with `false`, loads return `-ENOENT`, setup/cleanup functions are no-ops, `zswap_is_enabled()` is false, and `zswap_never_enabled()` is true.

## Control Flow
Swap-out paths call `zswap_store()` with a folio. A true result means zswap accepted and compressed the folio into its pool, while false lets normal disk swap continue. Swap-in paths call `zswap_load()`; success restores the folio from memory, and `-ENOENT` means the entry was absent and disk swap must be used. `zswap_folio_swapin()` is an accounting hook for swap-in events.

Swap-device lifecycle flows through `zswap_swapon()` before use and `zswap_swapoff()` on teardown. Individual swap entries are removed with `zswap_invalidate()`. Memory-cgroup and LRU-vector lifetime flows initialize `zswap_lruvec_state` with `zswap_lruvec_state_init()` and call `zswap_memcg_offline_cleanup()` when a memcg leaves service.

## State And Persistence Behavior
Zswap state is volatile in-memory state. Stored compressed pages remain only while the kernel, swap type, zswap pool, and relevant cgroup state remain active. `zswap_stored_pages` and `zswap_total_pages()` expose global pool occupancy. Per-lruvec `nr_disk_swapins` persists as an atomic accounting value until reset by lruvec lifecycle and is used to avoid over-shrinking after zswap misses force disk swap-ins.

No data persists across reboot. `zswap_swapoff()` and invalidation paths must drop entries and accounting for a swap type. Disabled builds persist no state beyond the always-false/true behavior of capability probes.

## Dependencies And Integration Points
The header depends on `linux/types.h`, `linux/mm_types.h`, `struct folio`, `swp_entry_t`, `struct mem_cgroup`, and `struct lruvec`. It integrates with the swap subsystem, memory reclaim/shrinker logic, cgroup offlining, and folio-based MM paths.

`zswap_lruvec_state.nr_disk_swapins` is explicitly consumed by `zswap_shrinker_count()` according to the comment, so reclaim accounting and shrinker heuristics rely on this header-level state shape. The disabled stubs make higher-level swap code independent of `CONFIG_ZSWAP` at link time.

## Risks
Callers must handle `zswap_store()` returning false and `zswap_load()` returning `-ENOENT`; those outcomes are normal, not necessarily fatal. Accounting bugs in `nr_disk_swapins` can bias reclaim by making zswap shrinkers retain or evict too much memory. Swapoff and invalidation ordering is sensitive because stale compressed entries tied to reused swap offsets could restore wrong data.

The no-op disabled stubs must remain semantically aligned with real zswap failure modes. If a caller assumes `zswap_never_enabled()` is equivalent to `!zswap_is_enabled()` at runtime, it can mis-handle systems where zswap is configured but administratively disabled or enabled later.

## Test Signals
Build tests should compile MM callers with `CONFIG_ZSWAP=y` and `CONFIG_ZSWAP=n` to catch prototype drift and fallback semantics. Functional tests should cover store/load hit, load miss with disk fallback, invalidate, swapoff cleanup, memcg offline cleanup, and total-page accounting.

Reclaim tests should observe `nr_disk_swapins` effects on shrinker counts after forced disk swap-ins. Concurrency tests should stress folio swapout/swapin, invalidation, and swapoff racing with reclaim while checking atomic counters and absence of stale-entry loads.
