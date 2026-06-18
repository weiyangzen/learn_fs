
# sources/distributed-fs/ceph-client/include/linux/numa_memblks.h

Purpose: declares early NUMA memory-block tracking and optional NUMA emulation interfaces used while converting firmware memory ranges into node topology.

Important APIs/types/functions: `NR_NODE_MEMBLKS`, `struct numa_memblk`, and `struct numa_meminfo` model start/end/node memory ranges. APIs set/reset node distances, add normal and reserved memblocks, remove memblocks, clean/merge meminfo, initialize NUMA memblocks through an architecture callback, and expose `numa_distance_cnt`. Under `CONFIG_NUMA_EMU`, emulation APIs parse command-line input, map emulated to physical nodes, compute DMA end, and rewrite CPU/node and meminfo mappings.

Control flow: architecture setup adds firmware memory ranges with node IDs, cleans the meminfo table, sets distance information, optionally rewrites topology for NUMA emulation, and then MM initialization consumes the ranges for node data and zones.

State and persistence: memblock lists are early-boot topology state and may be retained when `CONFIG_NUMA_KEEP_MEMINFO` is enabled. Emulation maps persist for runtime node interpretation.

Dependencies and integration points: depends on `linux/numa.h`, `MAX_NUMNODES`, init annotations, and architecture callbacks. It integrates firmware NUMA parsing, reserved memory tracking, distance matrices, memory hotplug node lookup, and NUMA emulation.

Risks and test signals: risks include overlapping/unsorted ranges, exceeding `NR_NODE_MEMBLKS`, distance matrix leaks/stale values, emulated-to-physical node confusion, and incorrect reserved-range handling. Test signals include ACPI/SRAT or device-tree NUMA boot, fake NUMA command-line tests, memblock overlap cleanup tests, node distance sysfs validation, and hotplug physical address mapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/numa_memblks.h -->
