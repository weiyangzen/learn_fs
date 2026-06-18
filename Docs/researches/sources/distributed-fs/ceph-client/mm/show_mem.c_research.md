# sources/distributed-fs/ceph-client/mm/show_mem.c

Purpose: provides generic memory reporting helpers used by sysinfo, `/proc/meminfo`-style consumers, and diagnostic `show_mem` output during OOM or manual memory dumps. It estimates available memory, fills `struct sysinfo`, and prints detailed node/zone/free-area state.

Important APIs/types/functions: exports `_totalram_pages`, `totalreserve_pages`, `totalcma_pages`, `si_mem_available`, and `si_meminfo`; under NUMA it also provides `si_meminfo_node`. Internal helpers include `show_node`, `show_mem_node_skip`, `show_migration_types`, `node_has_managed_zones`, `show_free_areas`, and `__show_mem`.

Control flow: `si_mem_available` sums low watermarks, starts from global free pages minus reserves, adds a conservative portion of active/inactive file cache, adds a conservative portion of reclaimable slab and miscellaneous kernel reclaimable pages, and clamps negative estimates to zero. `si_meminfo` and `si_meminfo_node` fill page counts directly from global or per-node vmstat counters. `__show_mem` prints a header, delegates the detailed dump to `show_free_areas`, then totals present, reserved, highmem/movable-only, CMA, hwpoisoned, and optional allocation-profiling information.

State and persistence behavior: this file owns only global accounting variables; most values are snapshots read from vmstat, zone, node, hugetlb, swap, CMA, and optional profiling state. Output is intentionally approximate and racy because it is diagnostic. `show_free_areas` briefly locks each zone only while copying buddy free-list counts and migratetype occupancy, avoiding long lock holds during printing.

Dependencies and integration points: depends on zone/node iteration, vmstat counters, cpuset nodemask filtering, highmem, hugetlb, swap reporting, block-device page accounting, CMA, memory failure counters, and optional allocation profiling codetags. It is called from OOM/reclaim diagnostics and other kernel paths needing a memory snapshot.

Risks: the available-memory heuristic can over- or under-estimate under unusual reclaimability, watermarks, memcg pressure, pinned file cache, or unreclaimable slab conditions. Diagnostic output is large and can be expensive on systems with many nodes/zones/orders. Filtering by current cpuset is intentionally imprecise. Any counter unit mismatch would directly confuse operator-facing memory diagnostics.

Test signals: compare `si_meminfo` and `si_mem_available` against `/proc/meminfo` fields under memory pressure, file-cache growth, slab growth, swap activity, CMA reservation, and NUMA cpuset filtering. OOM and SysRq memory dumps should include per-node and per-zone lines, migration type letters, hugepage info, swap-cache info, and optional profiling rows without lockdep or printk-format warnings.
