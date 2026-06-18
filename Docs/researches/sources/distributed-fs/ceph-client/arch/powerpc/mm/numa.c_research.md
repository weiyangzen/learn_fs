# sources/distributed-fs/ceph-client/arch/powerpc/mm/numa.c

## Purpose
This file implements PowerPC NUMA topology discovery, CPU-to-node mapping, memory-to-node assignment, distance calculation, memory hotplug node lookup, and virtual processor home node updates. It primarily targets pSeries/LPAR/OPAL systems using device-tree associativity properties and hypervisor VPHN calls.

## Important APIs, Types, And Functions
Exported or externally visible APIs include `map_cpu_to_node()`, `unmap_cpu_from_node()`, `cpu_relative_distance()`, `__node_distance()`, `of_node_to_nid()`, `update_numa_distance()`, `of_drconf_to_nid_single()`, `dump_numa_cpu_topology()`, `mem_topology_setup()`, `initmem_init()`, `hot_add_scn_to_nid()`, `memory_hotplug_max()`, `find_and_update_cpu_nid()`, and `cpu_to_coregroup_id()`. Persistent tables are `numa_cpu_lookup_table`, `node_to_cpumask_map`, `numa_distance_table`, `distance_lookup_table`, and `numa_id_index_table`.

## Control Flow
`early_param("numa", early_numa)` handles `numa=off` and fake node boundaries. `mem_topology_setup()` initializes PFN bounds, temporarily offlines node 0, parses NUMA properties, falls back to `setup_nonnuma()`, intersects possible and online node maps, discovers possible nodes, allocates node cpumasks, resets CPU lookup, and maps all possible CPUs. `parse_numa_properties()` discovers affinity form, primary domain index, distance tables, CPU nodes, memory nodes, PCI nodes, and dynamic reconfiguration memory LMBs, assigning memblocks to NUMA nodes. `initmem_init()` allocates `NODE_DATA` for online nodes and registers CPU hotplug preparation.

## State And Persistence
The resulting node online/possible maps, memblock node assignments, `NODE_DATA`, CPU lookup table, cpumasks, and distance tables persist after boot and feed scheduler, memory allocator, hotplug, and topology code. VPHN can update CPU node association later.

## Dependencies And Integration Points
Dependencies include Open Firmware device-tree APIs, memblock, SPARSEMEM, DRCONF memory, RTAS/OPAL firmware feature flags, hypervisor calls, CPU sibling helpers, cpuhp, cpuset/topology code, and pSeries SPLPAR VPHN.

## Risks And Test Signals
Risks include malformed associativity arrays, invalid node IDs, distance-table size mismatch, fake NUMA boundary parsing, dynamic memory LMB assignment, CPU thread siblings landing on different nodes, and hotplug fallback to `first_online_node`. Test signals include `numa=off`, `numa=fake=`, form 0/1/2 firmware, OPAL and RTAS roots, memoryless node 0, CPU hotplug, LPM/VPHN updates, and memory hot-add from both memory nodes and DRCONF memory.
