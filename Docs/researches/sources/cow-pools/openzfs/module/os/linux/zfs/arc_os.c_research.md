# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/arc_os.c

## Purpose

Linux-specific ARC memory integration. It computes ARC memory limits, plugs ARC eviction into the Linux shrinker, handles memory pressure throttling, updates tuning when module parameters change, and reacts to memory hotplug.

## Memory Sizing

- `arc_default_max(min, allmem)`: default ARC max is based on total memory, keeping at least 1 GiB outside ARC on larger systems while enforcing a 5/8 total-memory style cap.
- `arc_all_memory()`: total usable memory, excluding highmem when configured.
- `arc_free_memory()`: free memory estimate, using free plus inactive file pages on normal builds.
- `arc_available_memory()`: free memory minus `arc_sys_free`.
- `arc_set_sys_free()`: computes system reserve from Linux watermark logic, boosts it, and adds a fraction of total memory.

## Shrinker Integration

- `arc_evictable_memory()`: estimates ARC bytes that can be evicted, accounting for clean/dirty ARC and page-cache proportional minimums.
- `arc_shrinker_count()`: reports reclaimable pages and honors `zfs_arc_shrinker_limit` for kswapd.
- `arc_shrinker_scan()`: marks ARC warm, pauses growth, reduces ARC target, waits for eviction when safe under `__GFP_FS`, updates reclaim accounting, and bumps direct/indirect memory-pressure stats.
- `arc_lowmem_init()` / `arc_lowmem_fini()`: register/unregister `zfs-arc-shrinker`.

## Throttling

- `arc_memory_throttle(spa, reserve, txg)`: throttles transaction work under low memory. It distinguishes kswapd/pageout context from normal context, using `spa_lowmem_page_load`, `arc_reclaim_needed()`, and returns `ERESTART` or `EAGAIN` when pressure is high.

## Parameter Hooks

- `param_set_arc_u64()`
- `param_set_arc_min()`
- `param_set_arc_max()`
- `param_set_arc_int()`
- `param_set_arc_no_grow_shift()`
- `param_set_l2arc_dwpd_limit()`

These parse module parameter changes and call ARC retuning or L2ARC DWPD reset behavior where needed.

## Memory Hotplug

With `CONFIG_MEMORY_HOTPLUG`:
- `arc_hotplug_callback()` responds to `MEM_ONLINE`, recomputes ARC limits, dirty-data maximum, and `arc_sys_free`.
- `arc_register_hotplug()` / `arc_unregister_hotplug()` manage the notifier.

## Module Parameters

- `zfs_arc_shrinker_limit`: pages reclaimable at once through shrinker.
- `zfs_arc_shrinker_seeks`: relative ARC eviction cost for shrinker policy.
