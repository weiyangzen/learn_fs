<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/numa.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/numa.c

Purpose: Initializes Loongson64 NUMA node topology, node memory data, CPU masks, and zone limits.

Important APIs/types/functions: Exports `__node_distances` and `__node_cpumask`; functions include `cpu_node_probe()`, `init_topology_matrix()`, `node_mem_init()`, `prom_meminit()`, `arch_zone_limits_init()`, `pcibus_to_node()`, and `prom_init_numa_memory()`.

Control flow: Discovers nodes from `loongson_sysconf.nr_nodes`, computes local/same-package/remote distances, calls `szmem()` for each node, allocates node data, reserves kernel and low gaps on node 0, and maps non-reserved CPUs into per-node cpumasks.

State and persistence: Populates node online/possible maps, memblock node assignments, `NODE_DATA`, `max_low_pfn`, zone PFN limits, and node CPU masks.

Dependencies and integration: Relies on `loongson_sysconf`, firmware memory map parsing in `szmem()`, and generic Linux NUMA/mm initialization.

Risks: CPU numbering uses active logical CPU order after reserved physical cores, which must match SMP maps. RS780E GPU reservation is hard-coded to top 32 MiB when node 0 reaches 4G.

Test signals: Boot logs should show nodes, PFN ranges, and CPU masks; `/sys/devices/system/node` should reflect expected topology; PCI buses should all map to node 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/numa.c -->
