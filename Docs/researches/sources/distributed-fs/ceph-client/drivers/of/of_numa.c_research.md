# sources/distributed-fs/ceph-client/drivers/of/of_numa.c

## Purpose
`of_numa.c` parses NUMA topology from devicetree. It discovers CPU node IDs, memory ranges per NUMA node, distance matrices, and provides a runtime node-to-NID lookup for devices.

## Important APIs, types, and functions
Important functions are `of_numa_init()` and `of_node_to_nid()`. Internal parsers are `of_numa_parse_cpu_nodes()`, `of_numa_parse_memory_nodes()`, `of_numa_parse_distance_map_v1()`, and `of_numa_parse_distance_map()`.

## Control flow and state
CPU parsing scans CPU nodes for `numa-node-id` and marks parsed node IDs. Memory parsing scans `device_type = "memory"` nodes with `numa-node-id`, converts each address range through `of_address_to_resource()`, adds ranges to `numa_add_memblk()`, and marks parsed nodes. Distance parsing finds a compatible `numa-distance-map-v1` node and consumes `distance-matrix` triplets of source node, destination node, and distance, validating local and remote distance rules before setting distances. `of_node_to_nid()` walks a device's parents until it finds `numa-node-id`, then returns it only if possible.

## Dependencies and integration
This file depends on OF traversal/address conversion, `numa_memblks`, architecture NUMA constants and distance APIs, and the weak fallback in `base.c` when `CONFIG_NUMA` is enabled.

## Risks and test signals
Risks include invalid NID values, malformed memory nodes, missing resources, asymmetric or invalid distance matrix entries, and `numa=off` causing otherwise valid firmware IDs to map to `NUMA_NO_NODE`. Signals are boot NUMA logs, node masks, memory block layout, and device locality behavior.
