# sources/distributed-fs/ceph-client/drivers/base/node.c

## Purpose
Implements `/sys/devices/system/node` devices, NUMA node attributes, CPU and memory-block links, heterogeneous-memory access metadata, memory-side cache metadata, and node state root attributes.

## Important APIs, Types, And Functions
Exports `register_node_notifier()`, `unregister_node_notifier()`, `node_notify()`, `node_set_perf_attrs()`, `node_update_perf_attrs()`, `register_cpu_under_node()`, `unregister_cpu_under_node()`, `register_memory_node_under_compute_node()`, `register_memory_blocks_under_node_hotplug()`, `unregister_memory_block_under_nodes()`, `register_node()`, and `unregister_node()`. Important local types are `struct node_access_nodes` for ranked initiator/target relationships and `struct node_cache_info` for memory-side cache levels. `node_devices[MAX_NUMNODES]` is the global node device table.

## Control Flow
`node_dev_init()` registers the `node` subsystem, creates devices for all online nodes, links present CPUs, initializes optional caches, and links boot memory blocks to nodes by walking memblock regions. `register_node()` allocates a node device, registers standard sysfs groups, installs hugetlb/compaction/reclaim node hooks, and links CPUs already assigned to the node. Hotplug memory registration walks memory blocks in a PFN range and creates bidirectional node-memory sysfs links. HMEM paths lazily create `accessN` devices and populate initiator/target links and performance attributes.

## State And Persistence
State is live kernel/sysfs state: `node_devices[]`, per-node access lists, per-node cache lists, sysfs links to CPU and memory block devices, and root node-state masks such as `possible`, `online`, `has_memory`, and `has_cpu`. Performance coordinates and cache attributes persist only as in-memory device attributes until node removal.

## Dependencies And Integration
Integrates with NUMA topology, cpumasks, memblock, memory hotplug, memory block lookup from `memory.c`, hugetlb, compaction, reclaim, VM statistics, mempolicy HMEM performance data, runtime PM no-callback devices, and optional architecture node attribute groups.

## Risks And Test Signals
Risks include dangling sysfs links during CPU/memory/node hotplug, missing `put_device()` on memory block lookup, duplicate cache level devices, incorrect handling of memory blocks spanning multiple nodes, and drift in meminfo/vmstat formatting. Test signals include NUMA sysfs layout checks, CPU hotplug link creation/removal, memory hotplug node links, HMEM initiator/target link tests, cache attribute registration tests, and validation of node state masks.
