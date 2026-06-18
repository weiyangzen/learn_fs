# Group Research: group_896_linux_sources_os_linux_linux_mm_memory_failure_c_sources_os_linux_li_2032808d2629

Scope: `Docs/research_subset_a.md` / Linux `mm/memory-failure.c` and `mm/memory-tiers.c`. Both listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/memory-failure.c -->
# File Research: sources/os/linux/linux/mm/memory-failure.c

## Role

Linux high-level hardware memory error and soft-offline handler. It turns machine-check, DAX, PFN-map, hugetlb, LRU, swap-cache, page-cache, and free-page failures into containment actions: mark pages poisoned, unmap users, signal affected tasks, isolate pages from allocators, truncate/evict cache entries, migrate suspicious pages, or report unrecoverable states.

## Key Behavior

- Exposes VM sysctls for early-kill policy, memory-failure recovery panic policy, and soft-offline enablement.
- Maintains global and per-NUMA-node memory failure statistics through `num_poisoned_pages`, memory block poison counters, and `memory_failure_attr_group`.
- Serializes main recovery paths with `mf_mutex`; page lifecycle races are handled with careful refcount acquisition, page locks, retry loops, PCP disable/enable, RCU, and mapping locks.
- Supports an RCU-registered `hwpoison_filter_func` so tests or users can reject selected poison events.
- Builds `to_kill` lists by reverse-mapping anonymous, KSM, file, hugetlb, fsdax, devdax, and registered PFN address-space mappings.
- Sends `SIGBUS` with `BUS_MCEERR_AR` for action-required current-task faults, `BUS_MCEERR_AO` for advisory early-kill users, and `SIGKILL` when corrupted mappings cannot be located or unmapped safely.
- Handles already-poisoned pages by optionally walking the current process page tables to find the poisoned virtual address and signal the accessor.
- Classifies page states through `error_states[]`, then dispatches to handlers for kernel/reserved pages, dirty or clean LRU pages, mlocked/unevictable pages, swap cache pages, huge pages, and unknown states.
- Removes clean page-cache folios with filesystem `error_remove_folio()` when available or mapping eviction otherwise; dirty page-cache errors set mapping `-EIO` before cleanup.
- Keeps dirty swap-cache pages delayed in swap cache so later faults hit poison handling, while clean swap-cache pages can be removed and recovered from backing store.
- Splits large folios before normal handling; failed THP split leads to forced process kill and failed containment because the main handler operates on base pages.
- Handles hugetlb separately under `hugetlb_lock`, tracks raw poisoned subpages in a per-folio list, handles unreliable raw tracking, prevents migration of poisoned huge pages, and dissolves free huge pages when possible.
- Handles ZONE_DEVICE and DAX through device `pgmap->ops->memory_failure()` when available, otherwise falls back to generic DAX process collection, unmap, and kill.
- Provides `register_pfn_address_space()` / `unregister_pfn_address_space()` for memory ranges not backed by `struct page`, using an interval tree to locate affected mappings.
- Provides `memory_failure_queue()` for IRQ-context producers using per-CPU KFIFOs and workqueue processing.
- Provides `unpoison_memory()` for software-injected poison only; it refuses after a real hardware failure and rejects mapped, referenced, reserved, slab, pgtable, offline, or still-mapped pages.
- Provides `soft_offline_page()` to migrate or invalidate still-readable pages without killing tasks, then mark the old page poisoned and remove it from reuse.

## Dependencies

Uses folios, rmap, anon/file interval trees, KSM hooks, DAX locking, dev_pagemap, hugetlb internals, memory hotplug counters, swap cache helpers, migration, LRU isolation, page table walking, shmem detection, memcg uncharge, sysctl registration, trace events, kfifo workqueue plumbing, and architecture hooks such as `arch_memory_failure()`.

## Research Notes

This file is the kernel’s central containment layer for bad physical memory. Its design is intentionally conservative: it favors existing VM locks and slow reverse walks over fast but unsafe shortcuts because failures are rare and can arrive asynchronously against arbitrary page lifecycle states.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/memory-failure.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/memory-tiers.c -->
# File Research: sources/os/linux/linux/mm/memory-tiers.c

## Role

Linux memory-tiering infrastructure. It groups NUMA memory nodes into ordered tiers by abstract memory distance, publishes memory-tier devices in sysfs, assigns each node a memory type, computes demotion targets for reclaim/migration, and supports performance-based tier distance algorithms.

## Key Behavior

- Defines `struct memory_tier` as an ordered tier with memory types, an abstract-distance chunk, a sysfs device, and a mask of all lower-tier nodes.
- Defines per-node `node_memory_type_map` entries with a memory device type and map count so multiple devices on one node can share one type reference.
- Registers the virtual `memory_tiering` bus and exposes each tier’s `nodelist` attribute.
- Groups memory types into tiers by rounding `memtype->adistance` down to `MEMTIER_CHUNK_SIZE`, keeping `memory_tiers` sorted by increasing abstract distance.
- Assigns nodes to tiers in `set_node_memory_tier()` using registered abstract-distance algorithms, or a default DRAM memory type when no specific type exists.
- Updates `NODE_DATA(node)->memtier` with RCU and uses `synchronize_rcu()` before unlinking node/type/tier relationships.
- Exports memory type helpers: `alloc_memory_type()`, `put_memory_type()`, `init_node_memory_type()`, `clear_node_memory_type()`, `mt_find_alloc_memory_type()`, and `mt_put_memory_types()`.
- Under NUMA migration, computes demotion chains by finding the closest nodes in the next lower tier and stores preferred demotion nodes per source node.
- Builds each tier’s `lower_tier_mask` so allocation fallback can target any lower-tier memory if preferred demotion nodes are unavailable.
- Determines top-tier status by locating the highest tier containing CPU nodes; promotion is avoided from tiers that include compute.
- `next_demotion_node()` filters preferred demotion targets by an allowed mask, randomly selects among equally preferred nodes, and falls back to `find_next_best_node()`.
- Under NUMA balancing, `folio_use_access_time()` repurposes `_last_cpupid` as access-time storage for non-top-tier folios when memory-tiering balancing mode is enabled.
- Provides default DRAM performance reference handling through `mt_set_default_dram_perf()` and converts performance coordinates to abstract distance with `mt_perf_to_adistance()`.
- Rejects the default DRAM performance algorithm if DRAM node latency or bandwidth differs from the reference by more than the built-in tolerance.
- Uses a blocking notifier chain for external abstract-distance algorithms via `register_mt_adistance_algorithm()`, `unregister_mt_adistance_algorithm()`, and `mt_calc_adistance()`.
- Handles memory hotplug: first memory on a node assigns a tier and recomputes demotion targets; last memory removal clears the tier and recomputes targets.
- Adds `/sys/kernel/mm/numa/demotion_enabled` when configured, and clears kswapd hopeless-state accounting when demotion is enabled.

## Dependencies

Uses NUMA node masks and node states, `pg_data_t->memtier`, RCU, krefs, sysfs devices and kobjects, memory hotplug notifiers, blocking notifier chains, scheduler NUMA balancing mode, migration/demotion policy, and kswapd reclaim state.

## Research Notes

This file owns the policy data model for heterogeneous memory placement. Device drivers can provide memory types or distance algorithms, while the core keeps tier membership, demotion masks, hotplug updates, and user-visible toggles coherent under `memory_tier_lock` plus RCU-protected readers.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/memory-tiers.c -->