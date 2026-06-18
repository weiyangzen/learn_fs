# sources/distributed-fs/ceph-client/mm/memory-tiers.c

Purpose: implements the kernel memory-tiering model for NUMA systems with heterogeneous memory. It groups memory nodes into ordered tiers by abstract distance, exposes tiers through sysfs, computes demotion targets for reclaim/migration, lets device drivers register memory types and abstract-distance algorithms, and provides NUMA-balancing helpers for promotion/demotion policy.

Important APIs, types, and globals:

- `struct memory_tier` represents one tier: list linkage, member memory types, `adistance_start`, a sysfs `device`, and `lower_tier_mask` for fallback demotion allocation.
- `struct memory_dev_type` instances, defined in the public memory-tier header, describe device memory classes by abstract distance, sibling list, node mask, and kref lifetime. This file allocates and releases them through `alloc_memory_type()` and `put_memory_type()`.
- `struct node_memory_type_map` tracks the memory type assigned to a NUMA node and a `map_count` for multiple devices contributing the same node/type mapping.
- Global state includes `memory_tier_lock`, ordered list `memory_tiers`, list `default_memory_types`, per-node `node_memory_types`, `default_dram_type`, init-time `default_dram_nodes`, `numa_demotion_enabled`, optional `node_demotion[]`, and `top_tier_adistance`.
- Exported APIs include `folio_use_access_time()`, `node_is_toptier()`, `node_get_allowed_targets()`, `next_demotion_node()`, `alloc_memory_type()`, `put_memory_type()`, `init_node_memory_type()`, `clear_node_memory_type()`, `mt_find_alloc_memory_type()`, `mt_put_memory_types()`, `mt_perf_to_adistance()`, `register_mt_adistance_algorithm()`, `unregister_mt_adistance_algorithm()`, and `mt_calc_adistance()`.
- Sysfs surfaces include `/sys/devices/system/memory_tiering/memory_tierN/nodelist` and, with NUMA migration/sysfs enabled, `/sys/kernel/mm/numa/demotion_enabled`.

Core control flow:

- `memory_tier_init()` runs as a `subsys_initcall`. It registers the virtual memory-tier bus, allocates `node_demotion` under `CONFIG_NUMA_MIGRATION`, creates the default DRAM memory type, records CPU+memory nodes as default DRAM candidates, and registers a node hotplug notifier.
- `memory_tier_late_init()` runs after firmware and drivers can provide tiering information. It iterates all `N_MEMORY` nodes, skips nodes already initialized by drivers, assigns the rest to a tier via `set_node_memory_tier()`, and computes demotion targets.
- `set_node_memory_tier()` calculates an abstract distance for a node using `mt_calc_adistance()`, falls back to default DRAM type or a default memory type for that distance, initializes the node memory-type reference, sets the node in the memtype nodemask, creates or finds the matching tier, and publishes `pgdat->memtier` through RCU.
- `find_create_memory_tier()` rounds a memory type's abstract distance down to a `MEMTIER_CHUNK_SIZE` bucket, keeps the global tier list ordered by distance, registers a sysfs device for new tiers, and links the memory type into the tier.
- `clear_node_memory_tier()` handles the inverse path on memory removal: clears `pgdat->memtier`, waits for RCU readers, removes the node from its memtype, unlinks an empty memtype from its tier, and destroys an empty tier device.
- `memtier_hotplug_callback()` responds to first-memory-added and last-memory-removed node events by setting or clearing node tiers under lock and then rebuilding demotion targets.
- With NUMA migration enabled, `establish_demotion_targets()` first disables all targets, then for each memory node picks the closest nodes in the next lower tier as `preferred` targets, computes the highest tier from which promotion is disallowed based on CPU-bearing nodes, builds each tier's `lower_tier_mask`, and logs the resulting preferred/fallback masks.
- `next_demotion_node()` chooses a preferred demotion target that is also in the caller's allowed mask; if no preferred target is allowed, it searches for the closest fallback node while treating the complement of `allowed_mask` as already used.
- `node_is_toptier()` and `node_get_allowed_targets()` read the RCU-published tier pointer to answer promotion/demotion policy queries without taking the global tier lock.
- Abstract-distance algorithm support is a blocking notifier chain. Providers register with `register_mt_adistance_algorithm()`, and `mt_calc_adistance()` calls the chain until a provider stops propagation. The default DRAM performance helpers validate consistent DRAM reference coordinates and compute distances from relative latency and bandwidth.
- `demotion_enabled_store()` toggles global demotion policy from sysfs and clears kswapd hopelessness counters when demotion is enabled so reclaim can retry under the new policy.

State and persistence behavior:

- Tier membership is runtime kernel state rooted in `memory_tiers`, per-node `node_memory_types`, memory-type node masks, sysfs devices, and each node's RCU `pgdat->memtier` pointer. It persists until memory hotplug removal, driver unregistration, or shutdown.
- Memory type lifetimes are kref-managed. Node mappings increment the kref once for the first mapping of a given node/type pair and decrement it when the last mapping is cleared.
- Demotion routing state lives in `node_demotion[node].preferred` and each tier's `lower_tier_mask`; it is rebuilt after tier topology changes and synchronized with RCU so readers see either old or disabled/new-consistent state.
- `default_dram_perf` state records one reference node/source for default DRAM performance. If another default DRAM node differs by more than 10 percent in any latency or bandwidth dimension, `default_dram_perf_error` permanently disables the default performance-based abstract-distance calculation.
- `numa_demotion_enabled` is a global sysfs-controlled boolean and is not itself serialized by `memory_tier_lock`.

Dependencies and integration points:

- The implementation depends on NUMA node masks and states, memory hotplug notifiers, pgdat fields, sysfs/kobject device registration, RCU, lockdep, blocking notifier chains, kref allocation, NUMA balancing mode bits, migration/reclaim demotion logic, HMAT/access-coordinate style performance data, and kswapd state.
- Device drivers for CXL, HMEM, PMEM, or other heterogeneous memory can allocate memory types, initialize node memory types, clear them on removal, and register algorithms that calculate abstract distance.
- Reclaim and migration use `numa_demotion_enabled`, `next_demotion_node()`, `node_get_allowed_targets()`, and `node_is_toptier()` to decide whether and where demotion or promotion should occur.
- NUMA balancing integrates through `folio_use_access_time()`, which repurposes a slow-tier folio's `_last_cpupid` field as access-time storage when memory-tiering mode is active.
- Sysfs provides observability and policy control to user space; kernel logs report demotion target topology and DRAM performance mismatch diagnostics.

Risks and edge cases:

- Tier updates are globally serialized, but readers rely on RCU and comments note that `next_demotion_node()` can observe updates unless callers wrap larger consistency needs in RCU. Callers must tolerate a target becoming stale immediately after selection.
- `clear_node_memory_type()` decrements `map_count` when the stored type matches or when `memtype` is NULL; misuse by callers could underflow map counts or release the wrong type.
- `find_create_memory_tier()` links a memtype into an existing tier but only new tiers get device registration. Failures during device registration unwind the tier list, but callers still need to handle `ERR_PTR`.
- Default DRAM performance mismatch disables the default performance algorithm globally after the first significant inconsistency. This avoids misleading distances but can collapse nodes back to fallback distances.
- `mt_perf_to_adistance()` uses integer arithmetic and multiplicative division ordering, so precision loss and overflow risk should be considered for extreme latency/bandwidth values.
- If `node_demotion` allocation fails, `WARN_ON` fires and demotion-target establishment becomes a no-op; policy callers must handle `NUMA_NO_NODE` or empty masks.
- `numa_demotion_enabled` toggling is simple sysfs state with side effects on kswapd counters, so tests should check both the flag and reclaim retry behavior.

Test signals:

- Boot and hotplug tests should verify memory-tier sysfs devices, each tier's `nodelist`, and correct creation/destruction as nodes are added and removed.
- NUMA migration tests should validate preferred demotion target selection across multi-tier topologies, fallback behavior under restricted allowed masks, `node_is_toptier()` decisions, and `lower_tier_mask` contents.
- Driver integration tests should cover custom memory type allocation, node map reference counting, abstract-distance notifier registration/unregistration, and failure fallback to default DRAM type.
- Performance-distance tests should exercise valid default DRAM coordinates, missing reference data, zero latency/bandwidth rejection, >10 percent mismatch rejection, and computed abstract distances for slower/faster memory.
- Sysfs tests should read/write `demotion_enabled`, confirm invalid boolean input is rejected, and check that enabling demotion clears kswapd hopelessness state.
