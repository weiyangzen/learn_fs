# Group Research: group_911_linux_sources_os_linux_linux_mm_vmscan_c_87476ed209b4

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/vmscan.c -->
# File Research: sources/os/linux/linux/mm/vmscan.c

## Purpose
Implements Linux memory reclaim scanning. This file is the central reclaim engine for folios on LRU lists: direct reclaim from allocating tasks, background reclaim by `kswapd`, memory-cgroup reclaim, soft-limit reclaim, hibernation reclaim, NUMA node reclaim, proactive user-triggered reclaim, and the multi-generation LRU implementation when `CONFIG_LRU_GEN` is enabled.

## Read Coverage
Read the complete file, 8068 lines / 229140 bytes. The file is in subset A through `sources/os/linux/linux`.

## Main Responsibilities
- Track reclaim policy and per-invocation accounting through `struct scan_control`.
- Decide whether reclaim targets global memory, root cgroup memory, or a specific memory cgroup.
- Balance anonymous versus file-cache reclaim using swappiness, refault costs, memory.low/min protection, cache-trim mode, and file-cache scarcity detection.
- Isolate folios from active/inactive LRU lists, process them outside `lru_lock`, and return unreclaimed folios to the correct LRU.
- Reclaim individual folios by checking references, evictability, dirty/writeback state, mappings, DMA pins, swap availability, buffer-head release, page-cache removal, swap-cache removal, and final free batching.
- Demote cold folios to lower NUMA memory tiers before freeing when demotion is available and allowed.
- Throttle reclaimers on too many isolated folios, writeback congestion, no-progress reclaim, or depleted `PFMEMALLOC` reserves.
- Drive slab shrinkers alongside LRU reclaim.
- Implement multi-generation LRU aging, eviction, memcg rotation, state transitions, sysfs controls, and debugfs inspection/commands.
- Run `kswapd` per memory node, including sleep/wake logic, watermark balancing, reclaim boosts, compaction handoff, and hopeless-node tracking.
- Provide exported helpers for explicit page-list reclaim, clean-page reclaim, LRU isolation/putback, kswapd lifecycle, proactive reclaim, and unevictable-list rescue.

## Core Data Structures and Tunables
- `struct scan_control`: per-reclaim invocation state. It stores reclaim target, target memcg, anon/file reclaim costs, swappiness override, LRU deactivation policy, write/unmap/swap/demotion permissions, cgroup protection retry flags, priority/order/reclaim zone, scanned/reclaimed counters, dirty/writeback statistics, and `reclaim_state` for slab/outside-LRU accounting.
- `vm_swappiness`: global default swappiness, exposed as `vm.swappiness`.
- `node_reclaim_mode`, `sysctl_min_unmapped_ratio`, `sysctl_min_slab_ratio`: NUMA node reclaim controls under `CONFIG_NUMA`.
- `enum folio_references`: classifies an isolated folio as reclaimable, reclaimable only if clean, keep, or activate.
- `pageout_t`: result of writing dirty anonymous/shmem/swapcache folios from reclaim.
- `struct reclaim_stat`: populated by `shrink_folio_list()` and consumed by inactive-list and MGLRU eviction paths for dirty/writeback, activation, demotion, unmap failure, lazyfree failure, and pageout accounting.
- MGLRU state uses `struct lru_gen_folio`, `struct lru_gen_mm_state`, `struct lru_gen_mm_walk`, per-generation folio lists, Bloom filters, PID-like refault feedback, and per-node memcg LRUs.

## Traditional LRU Reclaim Flow
- `get_scan_count()` computes scan targets for inactive/active anon and file LRUs. It respects swap/demotion availability, swappiness, cgroup reclaim semantics, priority, cache-trim mode, tiny file-cache detection, and proportional memory protection.
- `shrink_lruvec()` is the traditional per-lruvec scanner. It gets scan counts, iterates active/inactive LRUs in `SWAP_CLUSTER_MAX` chunks, calls `shrink_list()`, and uses proportional reclaim logic to avoid overscanning one LRU after the reclaim goal is met.
- `shrink_list()` routes active LRUs to `shrink_active_list()` and inactive LRUs to `shrink_inactive_list()`.
- `shrink_active_list()` isolates active folios, checks recent references, preserves executable file-backed folios when referenced, deactivates others to inactive lists with `PG_workingset`, and updates deactivation/refill accounting.
- `shrink_inactive_list()` throttles if too many folios are already isolated, isolates eligible inactive folios, invokes `shrink_folio_list()`, moves survivors back to LRU, updates scan/steal/demotion counters, notes reclaim cost, wakes flusher threads if all isolated dirty folios were unqueued, and emits vmscan tracepoints.
- `isolate_lru_folios()` is the hot path under `lru_lock`: it scans an LRU list, skips zones above `reclaim_idx`, tries to take stable references, clears `PG_lru`, updates LRU sizes, and records skipped/scanned/taken counts.
- `move_folios_to_lru()` returns survivor folios to the proper LRU, rescues newly unevictable folios, drops isolation references, and batches final frees for folios whose refcount reaches zero.

## Folio Reclaim Path
- `shrink_folio_list()` is the core per-folio reclaim engine shared by traditional LRU and MGLRU. It locks isolated folios, rejects unevictable or disallowed mapped folios, checks dirty/writeback state, handles writeback races, evaluates references, tries demotion, allocates swap for anonymous swapbacked folios, unmaps PTEs, rejects DMA-pinned folios, performs pageout when allowed, releases buffer/private data, removes folios from page cache or swap cache, uncharges memcg batches, flushes TLB batches, and frees folios.
- `folio_check_references()` uses rmap/reference information, `PG_referenced`, executable mappings, VM_LOCKED VMAs, and MGLRU reference bits to decide keep/activate/reclaim behavior.
- `pageout()` only writes anonymous swapcache and shmem/tmpfs-like reclaim targets; dirty filesystem page cache is activated for writeback machinery instead of issuing random writeback from reclaim.
- `writeout()` delegates to `shmem_writeout()` or `swap_writeout()`, handles synchronous write errors through `mapping_set_error()`, traces vmscan writes, and accounts `NR_VMSCAN_WRITE`.
- `__remove_mapping()` safely removes a locked, clean, unbusy folio from file page cache or swap cache. It freezes refcounts, checks dirty state after freezing to avoid data loss races, records workingset shadow entries when appropriate, updates swap/memcg state, calls filesystem `free_folio`, and re-adds shrinkable inodes to the inode LRU.
- `remove_mapping()` is the public wrapper for non-reclaim removal and drops the page-cache reference on success.
- Lazyfree folios can be freed directly when the isolation reference is the only remaining reference.
- Large folios and THP are handled with split fallbacks for partial mappings, swap allocation failures, and shmem writeout splits; accounting is adjusted when a folio splits during reclaim.

## Demotion and Swap Decisions
- `can_reclaim_anon_pages()` allows anon reclaim if swap is available under global or memcg limits, or if NUMA demotion can move the folio to a lower memory tier.
- `can_demote()` verifies global demotion enablement, `scan_control.no_demotion`, node target availability, and cgroup node filters.
- `demote_folio_list()` migrates selected cold folios to an allowed lower-tier node with `MR_DEMOTION`; undemoted folios are retried for actual reclaim unless proactive reclaim is running.
- `alloc_demote_folio()` first tries `__GFP_THISNODE` on the target node to avoid placing hot pages in slower tiers before target-node pressure has been handled.

## Memory Cgroup Handling
- `cgroup_reclaim()` distinguishes memcg-targeted reclaim from global reclaim; `root_reclaim()` treats direct/global and root-cgroup reclaim specially.
- `sc_swappiness()` uses memcg swappiness, global `vm_swappiness`, or proactive reclaim override.
- `apply_proportional_protection()` reduces scan pressure based on `memory.min` and `memory.low`, records low-protection skips, and enforces a minimum scan batch for forward progress.
- `shrink_node_memcgs()` walks the target cgroup subtree, calculates protection, skips hard-protected groups, optionally honors soft protection, reclaims each lruvec, runs slab shrinkers, emits vmpressure, and can use partial walks for direct reclaim latency.
- `do_try_to_free_pages()` retries with full memcg walks, forced deactivation, or low-protection override before declaring no reclaim progress.
- `try_to_free_mem_cgroup_pages()` is the main memcg reclaim entry point, including proactive reclaim support and optional swappiness override.
- `mem_cgroup_shrink_node()` is a soft-limit-only helper that reclaims from one memcg/lruvec at priority zero.

## Multi-Generation LRU
- The `CONFIG_LRU_GEN` block implements aging and eviction with generations instead of active/inactive list rotation.
- Static keys `lru_switch` and `lru_gen_caps[]` control core MGLRU, page-table walking, and non-leaf accessed-bit clearing.
- Aging increments `max_seq`; eviction advances `min_seq[type]`. Generations are tracked per anon/file type and zone.
- Bloom filters remember PMD/PTE-table locations likely to contain young pages, reducing future page-table walk cost.
- `lru_gen_add_mm()`, `lru_gen_del_mm()`, and `lru_gen_migrate_mm()` maintain per-memcg `mm_struct` lists for page-table walkers.
- `iterate_mm_list()`, `walk_mm()`, `walk_pud_range()`, `walk_pmd_range()`, and `walk_pte_range()` scan user page tables, clear young/accessed bits, detect dirty PTEs/PMDs, update folio generations, and batch LRU size updates.
- `lru_gen_look_around()` is the rmap-side feedback path: when reclaim sees a young PTE, it scans nearby PTEs for spatial locality and updates generations/Bloom filters.
- PID-like refault feedback in `read_ctrl_pos()`, `positive_ctrl_err()`, `get_tier_idx()`, and `get_type_to_scan()` protects tiers/types with higher refault rates and chooses whether anon or file should be scanned.
- `scan_folios()` sorts cold-generation folios into promoted, protected, ineligible, writeback, skipped, or isolated categories; isolated folios still use `shrink_folio_list()`.
- `evict_folios()` runs MGLRU eviction, then retries clean unmapped survivors that may have missed reclaimable rotation.
- `try_to_shrink_lruvec()`, `shrink_one()`, and `shrink_many()` combine MGLRU aging/eviction with memcg fairness and slab reclaim.
- `lru_gen_change_state()` converts between traditional LRU lists and generation lists while holding cgroup/cpu/memory-hotplug coordination locks.
- MGLRU exposes `/sys/kernel/mm/lru_gen/enabled`, `/sys/kernel/mm/lru_gen/min_ttl_ms`, and debugfs files `lru_gen` and `lru_gen_full`. Debugfs write commands can trigger aging (`+`) or eviction (`-`) for a memcg/node/sequence.
- `lru_gen_init_pgdat()`, `lru_gen_init_lruvec()`, `lru_gen_init_memcg()`, and `lru_gen_exit_memcg()` initialize and clean MGLRU state.

## Direct Reclaim
- `try_to_free_pages()` is the allocator-facing entry point. It builds a `scan_control`, optionally throttles direct reclaim, sets task reclaim state, traces begin/end, and calls `do_try_to_free_pages()`.
- `throttle_direct_reclaim()` protects `PFMEMALLOC` reserves when network-backed storage or low reserves make direct reclaim dangerous; kernel threads and fatal-signal exits avoid throttling.
- `shrink_zones()` iterates the allocation zonelist, applies cpuset and compaction readiness checks, invokes memcg soft-limit reclaim during global reclaim, and calls `shrink_node()` once per pgdat.
- `consider_reclaim_throttle()` wakes no-progress waiters when reclaim efficiency is acceptable or throttles direct reclaim at high priority with no progress.
- `should_continue_reclaim()` keeps reclaiming for high-order reclaim/compaction only while progress is being made and inactive pages remain useful for compaction.

## Node and Kswapd Reclaim
- `kswapd()` is the per-node background reclaim thread. It runs with `PF_MEMALLOC | PF_KSWAPD`, sleeps on `pgdat->kswapd_wait`, handles freezer/stop requests, and calls `balance_pgdat()` when woken.
- `wakeup_kswapd()` records the highest zone/order requested, skips unneeded reclaim if the node is balanced and not boosted, optionally wakes kcompactd, and wakes kswapd otherwise.
- `balance_pgdat()` performs node balancing with priority descent, watermark-boost accounting, optional writeback/swap suppression for boosted reclaim, background aging, memcg soft-limit reclaim, `kswapd_shrink_node()`, direct-reclaim wakeups, freezer checks, cache-trim retry, failure accounting, and compaction handoff.
- `pgdat_balanced()` checks whether any eligible zone satisfies high or promotion watermarks, with special handling for defrag mode and vmstat drift.
- `prepare_kswapd_sleep()` and `kswapd_try_to_sleep()` verify watermarks, wake pfmemalloc waiters, reset compaction isolation, wake kcompactd, manage short/full sleeps, and adjust per-cpu vmstat thresholds while kswapd sleeps.
- `kswapd_try_clear_hopeless()`, `kswapd_clear_hopeless()`, and `kswapd_test_hopeless()` track repeated node reclaim failures and prevent useless kswapd spinning.
- `kswapd_run()` starts a kswapd thread for a node; `kswapd_stop()` stops it during memory hot-remove.

## NUMA Node Reclaim
- Under `CONFIG_NUMA`, `node_reclaim()` may reclaim from the local node before falling back to remote allocation when `zone_reclaim_mode` permits it.
- It only scans blocking allocations, avoids `PF_MEMALLOC`, avoids CPU-bearing remote nodes, and serializes per pgdat with `PGDAT_RECLAIM_LOCKED`.
- `node_pagecache_reclaimable()` estimates clean/unmapped file-cache reclaimability, subtracting dirty file folios because reclaim no longer writes filesystem cache from this path.
- `__node_reclaim()` runs `shrink_node()` at `NODE_RECLAIM_PRIORITY` while slab or unmapped-file thresholds justify reclaim.

## Proactive and Special Reclaim
- `user_proactive_reclaim()` parses a byte target plus optional `swappiness=<n>` or `swappiness=max`, then repeatedly reclaims in batches from either a memcg or a NUMA node until the target is met, interrupted, busy, or retry-limited.
- A node sysfs write attribute `reclaim` exposes proactive node reclaim when `CONFIG_SYSFS && CONFIG_NUMA`.
- `shrink_all_memory()` handles hibernation reclaim with broad reclaim permissions and hibernation-mode throttling behavior.
- `reclaim_pages()` and `reclaim_folio_list()` reclaim an explicit list of folios, grouped by node and with demotion disabled.
- `reclaim_clean_pages_from_list()` reclaims clean file folios from a supplied list, used by compaction-style callers.
- `drop_slab()` and `drop_slab_node()` iterate memcgs/nodes and call shrinkers until slab freeing converges.

## Public and Exported Interfaces
- `zone_reclaimable_pages()`
- `lruvec_lru_size()`
- `drop_slab()`
- `reclaim_throttle()`
- `__acct_reclaim_writeback()`
- `remove_mapping()`
- `folio_putback_lru()`
- `reclaim_clean_pages_from_list()`
- `folio_isolate_lru()`
- `reclaim_pages()`
- MGLRU functions such as `lru_gen_add_mm()`, `lru_gen_del_mm()`, `lru_gen_migrate_mm()`, `lru_gen_online_memcg()`, `lru_gen_offline_memcg()`, `lru_gen_release_memcg()`, `lru_gen_soft_reclaim()`, `recheck_lru_gen_max_memcg()`, `max_lru_gen_memcg()`, `lru_gen_reparent_memcg()`, `lru_gen_init_pgdat()`, `lru_gen_init_lruvec()`, `lru_gen_init_memcg()`, and `lru_gen_exit_memcg()`.
- `try_to_free_pages()`
- `mem_cgroup_shrink_node()`
- `try_to_free_mem_cgroup_pages()`
- `wakeup_kswapd()`
- `kswapd_clear_hopeless()`
- `kswapd_try_clear_hopeless()`
- `kswapd_test_hopeless()`
- `shrink_all_memory()` when hibernation is enabled.
- `kswapd_run()` and `kswapd_stop()`
- `node_reclaim()` when NUMA is enabled.
- `user_proactive_reclaim()`
- `check_move_unevictable_folios()` exported with `EXPORT_SYMBOL_GPL`.
- `reclaim_register_node()` and `reclaim_unregister_node()` for NUMA node sysfs reclaim attributes.

## Concurrency, Locking, and Accounting
- LRU list isolation uses `lruvec->lru_lock`; expensive reclaim work happens after folios are isolated to avoid long lock holds.
- Folio locks protect mapping/writeback/removal decisions. `__remove_mapping()` additionally uses mapping `i_pages` locks, inode locks, or swap cluster locks.
- Refcount freezing in `__remove_mapping()` prevents races with speculative references and dirtying.
- RCU is used around memcg lookup and MGLRU memcg list traversal.
- Per-task `current->reclaim_state` connects slab/outside-LRU reclamation and MGLRU page-table walking state to the reclaim invocation.
- Batch freeing uses `folio_batch`, `mem_cgroup_uncharge_folios()`, `try_to_unmap_flush()`, and `free_unref_folios()` to amortize uncharging and TLB/free work.
- Reclaim progress is reported through vmstat events (`PGSCAN_*`, `PGSTEAL_*`, `PGDEMOTE_*`, `PGACTIVATE`, `PGDEACTIVATE`, etc.), node/lruvec counters, memcg events, vmpressure, PSI memstall accounting, delay accounting, and `trace/events/vmscan.h`.

## Important Behaviors and Edge Cases
- Filesystem-backed dirty page cache is generally not written from reclaim; reclaim activates/marks it and relies on normal writeback.
- Legacy memcg writeback lacks normal dirty throttling, so reclaim may wait on writeback where global/new memcg reclaim would rotate and throttle differently.
- Dirty/writeback-heavy inactive lists wake flusher threads and can throttle reclaimers.
- Direct reclaim avoids throttling kernel threads and tasks with fatal signals.
- `__GFP_FS` and `__GFP_IO` gates prevent reclaim from entering filesystems or swap paths in contexts that could deadlock.
- DMA-pinned folios are not reclaimed after unmapping because they may still be modified or pin filesystem metadata.
- Memory.low is skipped on the first pass but can be overridden on retry to avoid false OOM; memory.min remains hard protection.
- `cache_trim_mode` prefers reclaiming inactive file cache when it appears safe, but kswapd retries with it disabled if it makes no progress.
- `file_is_tiny` prevents runaway file-cache reclaim feedback from starving anonymous reclaim.
- Kswapd boost reclaim avoids writeback and swap to reduce fragmentation/pressure without issuing poor I/O.
- MGLRU `min_ttl_ms` can force OOM rather than reclaim generations younger than the configured working-set protection window.
- MGLRU state switching requires draining/converting all evictable folios between traditional and generational lists under broad synchronization.
- Node reclaim only runs in limited NUMA contexts and focuses on unmapped file cache and slab thresholds.

## Dependencies and Integration Points
- Core MM: folios, LRU vectors, page cache, swap cache, rmap, page table walking, migration, compaction, memory tiers, mempolicy/cpuset filters, and unevictable logic.
- Memory cgroups: reclaim targeting, protection, swappiness, swap limits, cgroup writeback, soft-limit reclaim, memcg lifecycle, and reparenting.
- Writeback and filesystems: dirty/writeback state, `address_space` operations, inode LRU, buffer heads, shmem/swap writeout, and mapping error propagation.
- Scheduler and kernel threads: kswapd lifecycle, freezer support, wait queues, task flags, PSI, delay accounting, and reclaim-state hooks.
- VM observability: vmstat, tracepoints, vmpressure, sysctl, sysfs, debugfs, and node device attributes.

## Research Notes
This file is the main policy and execution hub for reclaim. The traditional path and MGLRU path differ in aging and victim selection, but both converge on `shrink_folio_list()` for the hard part of reclaiming an isolated folio. The file’s most important invariants are avoiding reclaim-context deadlocks, preserving dirty data under concurrent references, balancing anon/file pressure fairly, respecting memcg protections, and keeping kswapd/direct reclaim from causing excessive latency or futile I/O.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/vmscan.c -->