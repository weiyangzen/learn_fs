# sources/distributed-fs/ceph-client/mm/vmscan.c

## Purpose

`vmscan.c` is the Linux VM reclaim engine. It is responsible for reclaiming memory from LRU-managed folios, page cache, swap-backed anonymous memory, slab shrinkers, NUMA nodes, memory cgroups, and background reclaim through `kswapd`. In this source tree it lives under `sources/distributed-fs/ceph-client/mm/`, but the implementation is generic kernel memory-management code rather than Ceph-specific logic.

The file implements both the classic active/inactive LRU reclaim path and the optional multigenerational LRU path guarded by `CONFIG_LRU_GEN`. It exposes allocator-facing reclaim (`try_to_free_pages()`), memcg reclaim (`try_to_free_mem_cgroup_pages()`), hibernation reclaim (`shrink_all_memory()`), NUMA node reclaim (`node_reclaim()`), proactive reclaim parsing (`user_proactive_reclaim()`), kswapd lifecycle (`kswapd_run()`, `kswapd_stop()`, `wakeup_kswapd()`), debug/sysfs controls for MGLRU, and helpers that isolate, reclaim, demote, reactivate, or rescue folios.

## Important APIs, Types, and Globals

- `struct scan_control` is the central per-reclaim invocation state. It carries the reclaim target (`nr_to_reclaim`, `target_mem_cgroup`, `nodemask`, `reclaim_idx`), behavior flags (`may_writepage`, `may_unmap`, `may_swap`, `proactive`, `hibernation_mode`, `no_demotion`), pressure balancing inputs (`anon_cost`, `file_cost`, `priority`, `order`, `proactive_swappiness`), progress counters (`nr_scanned`, `nr_reclaimed`), writeback/congestion counters, memcg protection retry state, compaction readiness, and an embedded `reclaim_state`.
- `vm_swappiness` is the global swappiness tunable, registered through the `vm.swappiness` sysctl. `sc_swappiness()` selects memcg swappiness or proactive override when available.
- `pageout_t` captures dirty-folio writeout outcomes: keep, activate, success, or clean.
- `enum folio_references` classifies reference checks as reclaimable, clean-only reclaimable, keep, or activate.
- `enum scan_balance` selects anon/file scan policy: equal, fractional, anon-only, or file-only.
- `lru_gen_min_ttl` and MGLRU static keys/caps persist global MGLRU state when `CONFIG_LRU_GEN` is enabled.
- NUMA controls include `node_reclaim_mode`, `sysctl_min_unmapped_ratio`, and `sysctl_min_slab_ratio`, registered through `vm.zone_reclaim_mode` when `CONFIG_NUMA` is enabled.

Primary exported or externally visible functions include:

- `zone_reclaimable_pages()`, `lruvec_lru_size()`, `drop_slab()`, `reclaim_throttle()`, `__acct_reclaim_writeback()`.
- `remove_mapping()`, `folio_putback_lru()`, `folio_isolate_lru()`, `reclaim_clean_pages_from_list()`, `reclaim_pages()`.
- `try_to_free_pages()`, `try_to_free_mem_cgroup_pages()`, `mem_cgroup_shrink_node()` under memcg, `shrink_all_memory()` under hibernation, `node_reclaim()` under NUMA.
- `kswapd_run()`, `kswapd_stop()`, `wakeup_kswapd()`, `kswapd_clear_hopeless()`, `kswapd_try_clear_hopeless()`, `kswapd_test_hopeless()`.
- MGLRU hooks such as `lru_gen_add_mm()`, `lru_gen_del_mm()`, `lru_gen_migrate_mm()`, `lru_gen_online_memcg()`, `lru_gen_offline_memcg()`, `lru_gen_release_memcg()`, `lru_gen_soft_reclaim()`, `max_lru_gen_memcg()`, `lru_gen_reparent_memcg()`, `lru_gen_init_pgdat()`, `lru_gen_init_lruvec()`, `lru_gen_init_memcg()`, and `lru_gen_exit_memcg()`.
- `check_move_unevictable_folios()` is exported GPL and rescues now-evictable folios from the unevictable list.

## Classic LRU Reclaim Flow

The classic reclaim path starts from a caller-constructed `scan_control` and descends through zones, nodes, memcgs, lruvecs, LRU list selection, folio isolation, and folio reclamation.

`try_to_free_pages()` is the direct allocator entry point. It initializes `scan_control`, optionally throttles direct reclaim through `throttle_direct_reclaim()`, installs `current->reclaim_state`, emits tracepoints, and calls `do_try_to_free_pages()`. `do_try_to_free_pages()` loops priorities from `DEF_PRIORITY` downward, calls `shrink_zones()`, then retries with a full memcg walk, forced deactivation, or overridden `memory.low` if earlier passes made no progress for those reasons.

`shrink_zones()` walks eligible zones in the allocation zonelist and invokes `shrink_node()` once per relevant pgdat. It honors cpusets, high-order compaction readiness, buffer-head pressure, memcg soft-limit reclaim, and the caller's nodemask/reclaim index. `shrink_node()` handles node-level accounting, MGLRU dispatch, memcg iteration through `shrink_node_memcgs()`, writeback/congestion tagging, direct-reclaim throttling, reclaim/compaction continuation, and kswapd hopeless-counter reset.

`shrink_node_memcgs()` iterates memcgs under the target cgroup, calculates `memory.min` and `memory.low` protection, skips or soft-overrides protected groups as appropriate, then calls `shrink_lruvec()` and `shrink_slab()` per lruvec. Partial memcg walks are used for direct reclaim latency, while kswapd and forced full walks traverse more completely.

`shrink_lruvec()` chooses scan targets with `get_scan_count()`, then repeatedly calls `shrink_list()` for inactive and active anon/file LRUs. Scan balance is affected by swap availability, demotion availability, swappiness, reclaim priority, cache-trim mode, tiny file LRU detection, refault costs, and memcg proportional protection. Active LRUs are handled by `shrink_active_list()` when deactivation is allowed; inactive LRUs are handled by `shrink_inactive_list()`.

`shrink_inactive_list()` throttles if too many direct reclaimers have isolated pages, drains per-CPU LRU additions, isolates candidates with `isolate_lru_folios()`, accounts `PGSCAN*`, calls `shrink_folio_list()`, returns unreclaimed folios with `move_folios_to_lru()`, accounts demotion/steal stats, nudges flusher threads for unqueued dirty folios, and emits `trace_mm_vmscan_lru_shrink_inactive`.

`shrink_folio_list()` is the core folio eviction loop. For each isolated folio it:

- locks the folio and skips poisoned large folios or non-evictable folios;
- honors `may_unmap`, dirty/writeback state, writeback-throttling rules, and reclaim flags;
- classifies references with `folio_check_references()` unless references are ignored;
- optionally demotes cold folios to lower-tier memory through `demote_folio_list()`;
- allocates swap for anonymous swap-backed folios, splitting large folios when necessary;
- unmaps mapped folios with `try_to_unmap()`, including huge PMD handling and synchronous unmap for large folios;
- avoids reclaiming DMA-pinned folios;
- writes dirty anonymous, shmem, or swapcache folios through `pageout()` when allowed;
- releases buffers with `filemap_release_folio()`;
- removes folios from page cache or swap cache through `__remove_mapping()`;
- uncharges and frees reclaimed folios in folio batches;
- activates, keeps, or returns rejected folios to the caller's list.

The removal path is carefully ordered. `__remove_mapping()` locks either swap cluster state or `mapping->i_pages`, freezes the expected refcount before checking dirty state, records workingset eviction shadows when appropriate, removes from swap cache or file mapping, handles DAX and exiting mappings, and invokes `free_folio` callbacks. The refcount/dirty ordering is a key data-integrity guard against racing GUP or page dirtying.

## Multigenerational LRU Flow

When `CONFIG_LRU_GEN` is enabled and MGLRU is active, memcg and root reclaim can use generation-based aging and eviction instead of the classic active/inactive list scan.

MGLRU maintains per-lruvec generation sequences, per-generation anon/file/zone folio lists, historical refault/eviction/protection counters, per-memcg LRU queues, optional page-table-walk state, and Bloom filters for PMD/PTE locality. `lru_gen_init_pgdat()` initializes per-node memcg queues, and `lru_gen_init_lruvec()` initializes generation timestamps, lists, and sequence state.

Aging is driven by `try_to_inc_max_seq()`. With page-table walking enabled, it obtains an `lru_gen_mm_walk`, iterates memcg-owned `mm_struct`s with `iterate_mm_list()`, walks VMAs and page tables through `walk_mm()`, `walk_pud_range()`, `walk_pmd_range()`, and `walk_pte_range()`, clears young bits, detects dirty PTEs/PMDs, and promotes hot folios through `walk_update_folio()` and `folio_update_gen()`. Bloom filters reduce page-table scanning by carrying forward PMD tables with enough young PTEs. If MM walking is unavailable or allocation fails, `iterate_mm_list_nowalk()` advances walker state and aging falls back.

Eviction is driven by `try_to_shrink_lruvec()`, `get_nr_to_scan()`, and `evict_folios()`. The logic selects anon/file type with PID-like refault feedback (`read_ctrl_pos()`, `positive_ctrl_err()`, `get_type_to_scan()`), picks protected tiers with `get_tier_idx()`, isolates cold folios with `scan_folios()` and `isolate_folio()`, re-sorts promoted/protected/ineligible/writeback folios in `sort_folio()`, then calls the same `shrink_folio_list()` used by classic reclaim. This preserves common writeback, unmap, mapping removal, demotion, and free behavior.

MGLRU also provides runtime state changes and observability:

- `lru_gen_change_state()` switches between classic and MGLRU state, migrating folios between classic LRU lists and generation lists under cgroup, CPU, memory-hotplug, and per-lruvec locks.
- `/sys/kernel/mm/lru_gen/enabled` exposes and toggles core/MM-walk/nonleaf-young capabilities.
- `/sys/kernel/mm/lru_gen/min_ttl_ms` stores a minimum working-set TTL and can trigger OOM behavior if all generations are younger than the TTL.
- debugfs files `lru_gen` and `lru_gen_full` show generation state and accept manual aging/eviction commands via `lru_gen_seq_write()`.

## Kswapd, Background Reclaim, and Compaction

`kswapd_init()` calls `swap_setup()`, starts one kswapd thread per memory node with `kswapd_run()`, and registers VM sysctls. `kswapd()` marks itself `PF_MEMALLOC | PF_KSWAPD`, loops between sleep and `balance_pgdat()`, handles freezer stop conditions, and records requested allocation order and highest zone index from wakers.

`wakeup_kswapd()` records the highest zone and order needing help, skips unmanaged or cpuset-disallowed zones, avoids waking if the node is already balanced and not boosted, may wake `kcompactd` for compaction-only cases, and otherwise wakes the node's kswapd waitqueue. `kswapd_try_to_sleep()` performs a short sleep check, wakes throttled direct reclaimers when safe, resets compaction isolation state before sleep, wakes kcompactd, emits sleep tracepoints, and adjusts per-cpu vmstat thresholds while kswapd sleeps or wakes.

`balance_pgdat()` is kswapd's reclaim loop. It accounts watermark boosts, sets `ZONE_RECLAIM_ACTIVE`, limits boosted reclaim to avoid writeback/swap, does background aging (`kswapd_age_node()`), applies memcg v1 soft-limit reclaim, calls `kswapd_shrink_node()`, wakes pfmemalloc waiters when reserves recover, lowers priority when reclaim is ineffective, avoids increasing failure counts for boost-only failure, clears active flags, reduces zone watermark boosts, wakes kcompactd, snapshots refaults, and exits memstall/fs-reclaim context.

High-order allocation interaction is handled by `in_reclaim_compaction()`, `should_continue_reclaim()`, `compaction_ready()`, `compact_gap()`, and kcompactd wakeups. Direct reclaim tries to stop once compaction or allocation can proceed, while kswapd may drop high-order reclaim back to order-0 after reclaiming enough base pages.

## State and Persistence Behavior

Most state is in kernel memory and persists for the lifetime of nodes, memcgs, lruvecs, zones, and tasks:

- Per-invocation reclaim state lives in `struct scan_control` and `current->reclaim_state`. `set_task_reclaim_state()` asserts against accidental overwrite or double-clear.
- Per-node state lives in `pg_data_t`: kswapd task pointer, kswapd order/highest-zone wake parameters, reclaim waitqueues, writeback throttle counters, failure counters, flags such as `PGDAT_WRITEBACK` and `PGDAT_RECLAIM_LOCKED`, MGLRU mm-walk storage, and memcg LRU queues.
- Per-zone state includes watermarks, watermark boosts, `ZONE_RECLAIM_ACTIVE`, free page counters, and reclaimable LRU statistics.
- Per-lruvec state includes classic LRU lists and costs, congestion flags, refault snapshots, MGLRU generation state, MGLRU historical feedback counters, MGLRU folio lists, and optional mm-walk/Bloom filter state.
- Per-memcg state affects reclaim through soft limits, `memory.min`, `memory.low`, swappiness, swap limits, cgroup writeback mode, online/offline/reparenting hooks, and memcg LRU queues.
- Per-folio state is encoded in flags and list membership: LRU, active, unevictable, referenced, workingset, reclaim, dirty, writeback, swapcache, lazyfree, mlocked, generation number, and reference-tier bits.
- Runtime tuning persists in sysctl variables (`vm_swappiness`, `node_reclaim_mode`) and MGLRU sysfs globals until changed or rebooted. Debugfs commands mutate live MGLRU aging/eviction state.

No on-disk data structures are written by this file directly, but reclaim can initiate swap writeout, shmem writeout, filesystem error propagation through `mapping_set_error()`, and filesystem/page-cache folio release callbacks. Write errors are deliberately recorded against the address space so later `fsync()`, `msync()`, or `close()` can observe them.

## Dependencies and Integration Points

This file sits at the center of kernel memory management and depends heavily on:

- Page allocator and zone APIs: watermarks, zonelists, compaction, kcompactd, cpusets, NUMA node masks, memory hotplug, pgdat and zone state.
- LRU and folio APIs from `mm_inline.h`, `internal.h`, and `swap.h`: `lruvec`, `folio_*`, `lruvec_add_folio()`, `lruvec_del_folio()`, generation helpers, deferred split queues, and LRU accounting.
- Reverse mapping and page table walking: `folio_referenced()`, `try_to_unmap()`, `page_vma_mapped_walk`, young-bit clearing, MMU notifiers, and `walk_page_range()`.
- Swap and shmem: swap cache, swap allocation/freeing, `swap_writeout()`, `shmem_writeout()`, swap cluster locking, swap limits, and swap-backed folio handling.
- Filesystems and address spaces: mapping locks, xarray page cache, writeback, buffer heads, DAX checks, `filemap_release_folio()`, inode LRU, and mapping error propagation.
- Memcg: cgroup reclaim, v1 soft limits, cgroup writeback, memory protection, memcg statistics, memcg LRU size accounting, memcg lifecycle and reparenting.
- Slab shrinkers: `shrink_slab()` and `reclaim_state->reclaimed`.
- VM pressure, PSI, delay accounting, tracepoints, vmstat counters, sysctl, sysfs, debugfs, freezer, kthreads, and OOM.

The file integrates with external users through allocator slow paths (`try_to_free_pages()`), memory cgroup interfaces (`try_to_free_mem_cgroup_pages()` and proactive reclaim), `/proc/sys/vm/*`, `/sys/kernel/mm/lru_gen/*`, debugfs MGLRU files, node sysfs reclaim attributes, and exported LRU helper APIs used by other MM subsystems.

## Risks and Edge Cases

- Reclaim correctness depends on subtle locking and refcount ordering. `__remove_mapping()` must freeze the refcount before dirty checks to avoid data loss from racing pins or writers.
- Dirty/writeback handling is deadlock-prone. The code distinguishes global reclaim, cgroup v1 reclaim, cgroup writeback, `__GFP_IO`, `__GFP_FS`, swap-backed folios, mapping writeback deadlock risk, and kswapd writeback throttling.
- Large folios and THP paths require careful accounting when folios split during swap allocation or shmem writeout. Several branches adjust `nr_scanned` and `nr_pages` after splits.
- DMA-pinned folios are deliberately not reclaimed after unmapping checks because pinned pages may still be modified and can break filesystem assumptions.
- Demotion changes the meaning of "reclaimed": demoted pages are counted as progress even though they remain allocated on another memory tier. Incorrect target-node masks or memcg filtering would skew tiering behavior.
- Memcg protection can cause no-progress reclaim and false OOM risk. The retry logic for full memcg walks, forced deactivation, and `memory.low` override is essential.
- MGLRU state transitions are complex because folio generation bits, list placement, LRU sizes, memcg reparenting, and concurrent page-table promotion can diverge. `lru_gen_change_state()` and reparenting paths are high-risk areas.
- Bloom-filter and page-table-walk optimizations trade precision for overhead. Incorrect young-bit clearing or MMU notifier handling could cause excessive reclaim or page-fault storms.
- Kswapd failure accounting is deliberately conservative. Resetting hopeless state at the wrong time can cause either premature direct reclaim/OOM fallback or endless kswapd spinning.
- Node reclaim can hurt locality-sensitive workloads if thresholds or `node_reclaim_mode` are misconfigured; it also uses `PGDAT_RECLAIM_LOCKED` to avoid concurrent local reclaim.
- Proactive reclaim accepts userspace input and must reject malformed sizes, invalid swappiness, conflicting memcg/node targets, and interrupted reclaim cleanly.

## Test Signals

Useful validation signals for this file include:

- Kernel MM selftests and boot tests with `CONFIG_MEMCG`, `CONFIG_LRU_GEN`, `CONFIG_NUMA`, `CONFIG_COMPACTION`, `CONFIG_TRANSPARENT_HUGEPAGE`, `CONFIG_HIBERNATION`, and cgroup writeback combinations.
- Stress workloads that exercise allocator direct reclaim, kswapd reclaim, memcg hard/soft limits, `memory.low`/`memory.min`, `memory.reclaim`, swap exhaustion, no-swap reclaim, shmem/tmpfs swapout, high-order THP allocation, and NUMA memory tiering.
- Tracepoints from `trace/events/vmscan.h`: direct reclaim begin/end, memcg reclaim begin/end, LRU isolate/shrink, write folio, reclaim throttling, kswapd wake/sleep/failure/reset, and node reclaim begin/end.
- Vmstat counters: `PGSCAN_*`, `PGSTEAL_*`, `PGDEMOTE_*`, `PGACTIVATE`, `PGDEACTIVATE`, `PGREFILL`, `ALLOCSTALL`, `PAGEOUTRUN`, `PGSCAN_DIRECT_THROTTLE`, `UNEVICTABLE_*`, `THP_SWPOUT_FALLBACK`, `PGLAZYFREED`, and writeback throttle counters.
- Sysctl/sysfs/debugfs checks: `vm.swappiness`, `vm.zone_reclaim_mode`, `/sys/kernel/mm/lru_gen/enabled`, `/sys/kernel/mm/lru_gen/min_ttl_ms`, `debugfs/lru_gen`, `debugfs/lru_gen_full`, and per-node `reclaim`.
- Fault injection or device-error tests verifying `handle_write_error()` records mapping errors and reclaim does not drop dirty data.
- Race-oriented tests around GUP pins, folio dirtying, writeback completion, folio splitting, memcg migration/reparenting/offline, memory hotplug, kswapd stop/start, and MGLRU enable/disable transitions.
- Performance signals: reclaim latency, page-fault rate after reclaim, refault/workingset counters, PSI memory stall time, kswapd CPU usage, direct reclaim stalls, dirty/writeback congestion, and compaction success after reclaim.
