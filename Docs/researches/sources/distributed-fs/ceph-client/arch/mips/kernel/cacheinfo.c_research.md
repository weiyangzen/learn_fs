<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cacheinfo.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/cacheinfo.c

### Purpose
`cacheinfo.c` exposes MIPS cache topology to Linux generic cacheinfo sysfs by translating `cpuinfo_mips` cache descriptors into cache leaves and sharing masks.

### Important APIs, Types, And Functions
It defines `populate_cache()` macro, `init_cache_level()`, `fill_cpumask_siblings()`, `fill_cpumask_cluster()`, and `populate_cache_leaves()`.

### Control Flow
Initialization rejects CPUs with uninitialized D-cache data. It counts leaves for split I/D or unified L1, optional victim, secondary, and tertiary caches. Population fills each leaf's type, level, line size, sets, ways, size, and shared CPU mask, using sibling masks for per-core caches and cluster masks for scache.

### State, Persistence, And Dependencies
State is stored in per-CPU `struct cpu_cacheinfo` and `struct cacheinfo` arrays. It depends on `current_cpu_data`, `cpu_data[]`, sibling/cluster helpers, and generic cacheinfo APIs.

### Integration Points
Sysfs cache topology, scheduler/topology consumers, tooling that reads cache sizes, and CPU probe/cache-probe code that fills `cpuinfo_mips` all connect here.

### Risks
The function uses `current_cpu_data` rather than `cpu_data[cpu]`, so callers must run in the expected CPU context. Missing or wrong cache probe data produces absent or incorrect sysfs topology.

### Test Signals
Boot tests should compare `/sys/devices/system/cpu/*/cache` against known hardware for split/unified L1, victim cache, cluster-shared scache, and tertiary cache systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cacheinfo.c -->
