# sources/distributed-fs/ceph-client/tools/perf/util/env.c

Purpose: Implements lifecycle, lazy discovery, cleanup, and query helpers for `struct perf_env`, which stores host/session environment metadata used by perf record/report/stat.

Important APIs: Initialization and teardown use `perf_env__init` and `perf_env__exit`. Discovery helpers read CPU topology, PMU mappings, CPUID, core PMU capabilities, architecture, CPU count, NUMA maps, branch counter info, and x86 vendor identity. With libbpf, BPF program info and BTF records are stored in locked rbtrees through insert/find/iterate helpers.

Control flow: Most public getters lazily populate missing fields for local operation, then return cached values. PMU capability collection handles single-core-PMU and hybrid multi-PMU systems differently. `perf_env__numa_node` builds a fast CPU-to-node array from recorded node maps. BPF insert/find paths use read/write semaphores around rbtrees and reject duplicate IDs.

State and persistence: Owns many heap fields in `perf_env`; `perf_env__exit` frees strings, arrays, cache levels, NUMA maps, memory node sets, hybrid nodes, PMU caps, cgroups, BPF trees, and CPU domain maps. Static caches in x86 vendor helpers memoize AMD/Intel answers process-wide.

Dependencies and integration: Depends on cpumap, PMU/PMUs, cgroup cleanup, rwsem, strbuf, utsname, BPF/libbpf optional code, trace beauty errno lookup, and sysfs/proc helpers behind CPU/PMU calls. It integrates with perf headers, session metadata, event reporting, stat, and architecture-specific formatting.

Risks: Lazy getters assume `env` is initialized and can allocate during read paths. `perf_env__find_br_cntr_info` chooses either legacy `cpu_pmu_caps` or first hybrid `pmu_caps`; callers need valid cap data. Static x86 vendor caches ignore different env objects after first call. BPF returned nodes remain owned by the env tree, so lifetime must outlive consumers.

Test signals: Tests should cover init/exit under valgrind/asan, duplicate BPF/BTF insertion, PMU capability parsing for single and hybrid PMUs, NUMA lookup with missing CPUs, arch normalization strings, x86 vendor caching, and behavior without libbpf/libtraceevent.
