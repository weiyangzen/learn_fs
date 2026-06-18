# sources/distributed-fs/ceph-client/tools/perf/util/cputopo.c

Purpose: discovers and owns CPU, NUMA, and hybrid-core topology summaries from sysfs and PMU metadata.

Important APIs/functions: `online_topology`, `cpu_topology__new/delete`, `cpu_topology__smt_on`, `cpu_topology__core_wide`, `numa_topology__new/delete`, and `hybrid_topology__new/delete`.

Control flow: CPU topology scans online CPUs, reads package/die/core sibling lists with old-file fallbacks, and stores unique strings. SMT checks sibling-list ranges. Core-wide validation ensures SMT sibling sets are fully included or excluded. NUMA topology reads node online, meminfo, and cpulist. Hybrid topology scans core PMUs and reads each `cpus` file.

State and persistence: `online_topology` caches a static snapshot. Allocated topology objects own sysfs/PMU strings.

Dependencies and integration: sysfs helpers, libperf cpumaps, cpumap max-present CPU, PMU scanning/open-file APIs, debug logging, and zalloc. Used by topology display and stat validation.

Risks: sysfs ABI varies. Some delete functions assume non-NULL pointers. `cpu_topology__core_wide` lacks allocation checks for parsed maps. Cached online topology does not update after hotplug.

Test signals: sysfs fixtures for old/new names, die present/absent, SMT on/off, core-wide subsets, NUMA parsing, hybrid PMUs, hotplug expectations, and allocation failures.
