<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/cpumap.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/cpumap.c

Purpose: Builds a topology-aware CPU distribution map for SPARC SMP work placement.

Important APIs and control flow: CPU topology is modeled as root, NUMA node, core, and proc/strand levels using `cpu_data(cpu).core_id`, `proc_id`, and `cpu_to_node()`. `enumerate_cpuinfo_nodes()` counts sorted online topology nodes. `build_cpuinfo_tree()` allocates a flexible tree and links parent/child ranges. `iterate_cpu()` walks rovers with Niagara-optimized or generic increment policies; Niagara spreads work across cores/pipelines before sibling strands. `_cpu_map_rebuild()` rebuilds the tree and fills `cpu_distribution_map`. `map_to_cpu()` spinlock-protects lookups, rebuilds on hotplug count mismatch, and falls back to linear online mapping if allocation fails.

State, dependencies, and risks: state includes global `cpuinfo_tree`, `cpu_distribution_map`, and `cpu_map_lock`. Dependencies include per-CPU topology fields, online/possible CPU masks, `sun4v_chip_type`, GFP_ATOMIC allocation, and optional CPU hotplug. Risks include assumptions that online CPU data is sorted by node/core/proc, `simple_map_to_cpu()` edge-case behavior, stale tree during hotplug, and allocation failure reducing placement quality. Test signals are map distribution on Niagara/T-series systems, CPU hotplug rebuilds, offline CPU avoidance, allocation-failure fallback, and exported `map_to_cpu()` users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/cpumap.c -->
