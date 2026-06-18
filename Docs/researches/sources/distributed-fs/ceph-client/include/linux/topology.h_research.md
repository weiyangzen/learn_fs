<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/topology.h -->
# sources/distributed-fs/ceph-client/include/linux/topology.h

## Purpose
provides generic CPU/NUMA topology accessors, fallback topology IDs/masks, node-distance constants, NUMA iteration helpers, scheduler NUMA hooks, and CPU capacity scale accessors.

## Important APIs, Types, and Functions
The file is 342 lines and exports these visible symbol families: types/enums none; macros/constants `LOCAL_DISTANCE`, `REMOTE_DISTANCE`, `DISTANCE_BITS`, `RECLAIM_DISTANCE`, `PENALTY_FOR_NODE_WITH_CPUS`, `TOPOLOGY_DIE_SYSFS`, `TOPOLOGY_CLUSTER_SYSFS`, `TOPOLOGY_BOOK_SYSFS`, `TOPOLOGY_DRAWER_SYSFS`, `topology_is_primary_thread`; function-like macros `nr_cpus_node`, `node_distance`, `topology_physical_package_id`, `topology_die_id`, `topology_cluster_id`, `topology_core_id`, `topology_book_id`, `topology_drawer_id`, `topology_ppin`, `topology_sibling_cpumask`, `topology_core_cpumask`, `topology_cluster_cpumask`, `topology_die_cpumask`, `topology_book_cpumask`, and 3 more; inline helpers `numa_node_id`, `cpu_to_node`, `set_numa_node`, `set_cpu_numa_node`, `set_numa_mem`, `numa_mem_id`, `cpu_to_mem`, `set_cpu_numa_mem`, `topology_is_primary_thread`, `sched_numa_hop_mask`, `topology_get_cpu_scale`; external prototypes `arch_update_cpu_topology`, `raw_cpu_read`, `per_cpu`, `cpu_to_node`, `set_numa_mem`, `numa_node_id`, `topology_sibling_cpumask`, `cpumask_of_node`, `sched_numa_find_nth_cpu`, `cpumask_nth_and`, `ERR_PTR`, `for_each_node_numadist`, `sched_numa_hop_mask`, `topology_set_cpu_scale`.

## Control Flow
Architecture topology code supplies overrides; generic code uses fallback package/core/cluster/die/book/drawer IDs and masks where absent. Scheduler and MM code query node distances, CPU-to-node/memory mappings, NUMA hop masks, and CPU capacity scale.

## State and Persistence Behavior
Runtime state includes per-CPU NUMA node/memory IDs, `node_reclaim_distance`, per-CPU `cpu_scale`, and architecture-provided topology masks. The header provides accessors and iteration macros over that state.

## Dependencies and Integration Points
It depends on arch topology, cpumasks, nodemasks, mmzone, SMP/percpu, and optional CONFIG_NUMA and memoryless-node support. Direct includes are `linux/arch_topology.h`, `linux/cpumask.h`, `linux/nodemask.h`, `linux/bitops.h`, `linux/mmzone.h`, `linux/smp.h`, `linux/percpu.h`, `asm/topology.h`.

## Risks and Edge Cases
Fallback masks can hide missing architecture topology. NUMA distance iteration requires RCU protection, and wrong CPU-to-node mappings degrade scheduling, reclaim, and locality decisions.

## Test Signals
Boot NUMA and non-NUMA configs, validate sysfs topology, scheduler NUMA hop masks, memoryless node mappings, CPU hotplug topology updates, and capacity scale values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/topology.h -->
