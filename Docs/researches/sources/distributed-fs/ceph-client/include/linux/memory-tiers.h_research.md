<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memory-tiers.h -->
# sources/distributed-fs/ceph-client/include/linux/memory-tiers.h

## Purpose
This header defines NUMA memory-tier metadata and APIs for abstract memory distance, DRAM defaults, node demotion, and performance-to-tier mapping.

## Important APIs, types, and functions
Constants define tier chunk sizing and default DRAM abstract distance. `struct memory_dev_type` tracks memory types, tier siblings, driver list membership, abstract distance, node mask, and kref. NUMA APIs include `alloc_memory_type`, `put_memory_type`, node type init/clear, adistance notifier registration, `mt_calc_adistance`, `mt_set_default_dram_perf`, `mt_perf_to_adistance`, type allocation/list helpers, demotion target helpers, `node_get_allowed_targets`, and `node_is_toptier`; non-NUMA builds return stubs.

## Control flow
Memory providers allocate or find memory types based on abstract distance, assign nodes to types, and register adistance/performance data. NUMA migration code queries demotion targets and top-tier status to move pages from faster to slower memory tiers under pressure.

## State and persistence
Runtime state includes memory type lists, tier sibling links, node masks, krefs, default DRAM type/nodes, and demotion enablement. It is rebuilt at boot/hotplug and not stored persistently.

## Dependencies and integration points
It depends on nodemasks, krefs, mm zones, notifier blocks, NUMA, NUMA migration, and HMAT/access-coordinate style performance data. It integrates hotplug, reclaim/demotion, CXL/driver-managed memory, and NUMA policy.

## Risks and test signals
Risks include abstract-distance bucket misclassification, stale node masks on hotplug, notifier ordering errors, demotion loops, and stub behavior on non-NUMA builds. Test memory type allocation/release, DRAM performance defaults, hotplug node type changes, demotion target calculation with allowed masks, and NUMA_MIGRATION disabled paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memory-tiers.h -->
