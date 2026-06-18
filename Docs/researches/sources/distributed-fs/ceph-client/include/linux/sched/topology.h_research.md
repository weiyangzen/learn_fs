# sources/distributed-fs/ceph-client/include/linux/sched/topology.h

Purpose: declares scheduler-domain topology structures, generated domain flags, domain partitioning APIs, topology-level callbacks, and CPU capacity helpers.

Important APIs and types: generated `SD_*` flag indexes/bits, `struct sd_flag_debug`, topology mask/flag functions, `struct sched_domain_attr`, `struct sched_domain_shared`, `struct sched_domain`, `sched_domain_span()`, `partition_sched_domains()`, domain allocation/free helpers, `cpus_equal_capacity()`, `cpus_share_cache()`, `cpus_share_resources()`, `struct sd_data`, `struct sched_domain_topology_level`, `set_sched_topology()`, `sched_update_asym_prefer_cpu()`, `SDTL_INIT()`, `rebuild_sched_domains_energy()`, arch capacity/pressure hooks, and `task_node()`.

Control flow: topology code generates domains from architecture topology levels, allocates per-CPU domain/group data, partitions domains for cpusets, and rebuilds energy-aware scheduling state when capacity/frequency models change.

State and persistence: scheduler domains and groups are runtime topology state, RCU-freed on rebuild. Shared domain counters track idle/busy information.

Dependencies and integration points: depends on topology, idle definitions, `sd_flags.h`, cpumasks, NUMA, SMT/cluster/mc/package topology, energy model, and cpufreq schedutil.

Risks and test signals: risks include span flexible-array layout assumptions, stale RCU domains after rebuild, wrong flag propagation, asymmetric capacity misclassification, and energy-domain rebuild omissions. Test topology debugfs/proc output, CPU hotplug, cpuset partitions, NUMA/SMT/cache topologies, EAS systems, and arch capacity hooks.
