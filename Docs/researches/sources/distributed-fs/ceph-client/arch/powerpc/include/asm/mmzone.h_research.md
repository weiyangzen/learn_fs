# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mmzone.h

Purpose: provides PowerPC NUMA and memory-hotplug declarations for memory-zone management.

Important APIs/types/functions: under `CONFIG_NUMA`, declares `numa_cpu_lookup_table`, `node_to_cpumask_map`, and memory hotplug max helpers. With memory hotplug, `memory_hotplug_max()` and `hot_add_drconf_memory_max()` are external; otherwise `memory_hotplug_max()` maps to `memblock_end_of_DRAM()`.

Control flow: NUMA and hotplug code query these helpers to cap addable memory and map CPUs to nodes.

State and persistence: NUMA lookup tables and node CPU masks persist globally after topology setup. Memory hotplug limits reflect boot and dynamic reconfiguration state.

Dependencies and integration points: depends on cpumask and memblock infrastructure; integrates NUMA topology, DR memory hotplug, and memory zone sizing.

Risks: incorrect hotplug maximums can reject valid DR memory or allow invalid ranges. CPU-to-node mapping must be initialized before NUMA users query it.

Test signals: NUMA boot topology checks, CPU-node mapping validation, memory hotplug add/remove, dynamic reconfiguration memory tests, and non-NUMA fallback builds.
