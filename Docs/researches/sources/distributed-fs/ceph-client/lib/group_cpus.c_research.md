# sources/distributed-fs/ceph-client/lib/group_cpus.c

## Purpose
`group_cpus.c` groups possible CPUs into a requested number of CPU masks while preserving NUMA, cluster, and sibling locality as much as possible. It is used by subsystems that need to spread queues, interrupts, or other resources over CPUs evenly.

## Important APIs, Types, and Functions
The exported API is `group_cpus_evenly(unsigned int numgrps, unsigned int *nummasks)`. SMP helpers include `grp_spread_init_one()`, `alloc_node_to_cpumask()`, `build_node_to_cpumask()`, `get_nodes_in_cpumask()`, `alloc_groups_to_nodes()`, `alloc_nodes_groups()`, `assign_cpus_to_groups()`, `alloc_cluster_groups()`, `__try_group_cluster_cpus()`, and `__group_cpus_evenly()`. `struct node_groups` stores a node or cluster id and either CPU or group count.

## Control Flow, State, and Persistence
On SMP, the function allocates temporary masks, builds node-to-CPU masks from possible CPUs, snapshots `cpu_present_mask`, groups present CPUs first, then groups non-present possible CPUs. For each mask, if groups are fewer than NUMA nodes it assigns whole node intersections round-robin. Otherwise it allocates a proportional number of groups to nodes, then tries cluster-local grouping before falling back to sibling-aware CPU spreading. `grp_spread_init_one()` picks a CPU, then consumes topology siblings first. On UP/non-SMP, it allocates masks and assigns `cpu_possible_mask` to the first group. The returned mask array persists until the caller frees it.

## Dependencies and Integration Points
The file depends on cpumask, NUMA node masks, CPU topology sibling and cluster masks, `sort()`, slab allocation helpers, and CPU hotplug-visible masks. It exports `group_cpus_evenly()` for IRQ, block, network, or queue mapping code that wants balanced CPU affinity sets.

## Risks and Test Signals
Risks include allocation failure paths, CPU hotplug races tolerated by snapshot semantics, cluster masks that are empty or overlap unexpectedly, divide-by-zero avoidance through active CPU checks, and returning fewer initialized masks than requested. Tests should cover zero groups, one CPU/non-SMP, more groups than CPUs, fewer groups than NUMA nodes, uneven NUMA sizes, sibling and cluster topologies, possible-but-not-present CPUs, and hotplug churn during grouping.
