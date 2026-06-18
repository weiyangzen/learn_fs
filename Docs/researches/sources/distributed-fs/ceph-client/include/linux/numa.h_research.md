
# sources/distributed-fs/ceph-client/include/linux/numa.h

Purpose: provides generic NUMA node helper declarations and config-dependent fallbacks for node validity, node-data allocation, nearest-node lookup, memory hotplug node mapping, and memblock filling.

Important APIs/types/functions: `NUMA_NO_MEMBLK`, `numa_valid_node()`, `NODE_DATA()`, `alloc_node_data()`, `alloc_offline_node_data()`, `numa_nearest_node()`, `nearest_node_nodemask()`, `memory_add_physaddr_to_nid()`, `phys_to_target_node()`, `numa_fill_memblks()`, and `numa_map_to_online_node()` are the main interfaces. `__initdata_or_meminfo` changes section placement depending on `CONFIG_NUMA_KEEP_MEMINFO`.

Control flow: early architecture NUMA parsing allocates per-node `pglist_data`, maps memory ranges to nodes, and later memory hotplug asks for the node that should own a physical address. Non-NUMA builds collapse most helpers to node 0 or `NUMA_NO_NODE`.

State and persistence: state is boot-time NUMA topology and per-node memory data in `node_data[]`. It persists for kernel runtime and changes only through memory hotplug or architecture-specific updates.

Dependencies and integration points: depends on node masks, memblock/init attributes, `MAX_NUMNODES`, and memory hotplug. It integrates architecture NUMA discovery, MM initialization, sysfs node attributes, and hotplug node selection.

Risks and test signals: risks include invalid node IDs, non-NUMA fallback mismatches, wrong physical-address-to-node mapping for hotplug, and initdata lifetime issues when meminfo is kept. Test signals include NUMA boot on multi-node systems, memory hotplug tests, nearest-node behavior with offline nodes, and compile coverage with `CONFIG_NUMA` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/numa.h -->
