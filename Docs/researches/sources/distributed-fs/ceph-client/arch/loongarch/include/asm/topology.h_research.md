<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/topology.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/topology.h

Purpose: exposes LoongArch CPU topology, NUMA, and cache/topology integration to generic scheduler code.
Important APIs and types: maps topology fields from `cpu_data`, defines node/cpu helpers, and includes generic topology fallbacks.
Control flow: ACPI PPTT or platform discovery populates `cpu_data` topology; scheduler and sysfs read the values through this header.
State and persistence: per-CPU core/package/node identifiers persist in CPU topology structures.
Dependencies and integration: integrates with ACPI topology parsing, NUMA setup, cacheinfo, scheduler domains, cpufreq, and sysfs topology files.
Risks and test signals: wrong topology degrades scheduling or misrepresents cache sharing. Signals include `/sys/devices/system/cpu` topology, scheduler domain dumps, NUMA boot, and cacheinfo validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/topology.h -->
