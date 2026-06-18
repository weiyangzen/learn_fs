<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/cacheinfo.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/cacheinfo.c

Purpose: populates Linux cacheinfo structures from LoongArch CPU cache descriptors.
Important APIs and types: implements `init_cache_level`, `populate_cache_leaves`, `cache_cpumap_setup`, and cache-sharing comparison helpers.
Control flow: CPU/cache sysfs setup calls `init_cache_level`, then `populate_cache_leaves` fills each cache leaf from `cpu_data[cpu].cache_leaves`; sharing maps are built by comparing cache leaves across online CPUs.
State and persistence: per-CPU cacheinfo leaves and shared CPU masks persist for sysfs and scheduler/topology consumers.
Dependencies and integration: depends on `linux/cacheinfo.h`, topology, `cpu-info.h`, and boot-populated cache descriptors.
Risks and test signals: wrong shared maps mislead scheduler and userspace. Signals include `/sys/devices/system/cpu/cpu*/cache`, hotplug cacheinfo refresh, and topology tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/cacheinfo.c -->
