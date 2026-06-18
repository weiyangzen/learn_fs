# sources/distributed-fs/ceph-client/tools/perf/util/env.h

Purpose: Defines `struct perf_env` and related topology, NUMA, memory, hybrid PMU, PMU capability, sched-domain, compression, and BPF metadata contracts.

Important APIs and types: Key structs include `cpu_topology_map`, `cpu_cache_level`, `numa_node`, `memory_node`, `hybrid_node`, `pmu_caps`, `domain_info`, `cpu_domain_map`, and `perf_env`. Function prototypes expose env lifecycle, CPUID/PMU/topology readers, arch formatting, BPF metadata accessors, NUMA lookup, PMU cap lookup, branch counter info, and x86 vendor helpers. `perf_env` also embeds clock conversion metadata and optional BPF rbtrees protected by rwsems.

Control flow and state: The header defines the persistent in-memory shape that is serialized in perf data headers and consumed by report/stat paths. Counters describe how many elements are valid in associated dynamic arrays.

Dependencies and integration: Includes Linux types/rbtree, cpumap, and rwsem. It is shared across perf record, report, stat, BPF event, cgroup, topology, and header code.

Risks: Many fields are raw pointers with paired count fields, so allocation/free and serialization must stay synchronized. Optional libbpf fields alter layout under build configuration. Callers must not assume fields are populated unless they invoked the corresponding reader or loaded them from a perf data file.

Test signals: Build matrix with/without libbpf, header serialization round trips for env fields, and teardown tests for every dynamically allocated substructure.
