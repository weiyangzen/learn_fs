<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/cpumap.h -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/cpumap.h

Purpose: Local header for SPARC CPU distribution mapping.

Important APIs and control flow: under `CONFIG_SMP`, declares `cpu_map_rebuild()` and `map_to_cpu()` and maps `cpu_map_init()` to rebuild. Without SMP, `cpu_map_init()` is a no-op and `map_to_cpu()` returns `raw_smp_processor_id()`.

State, dependencies, and risks: SMP state is owned by `cpumap.c`; non-SMP has no extra state. Dependencies include `CONFIG_SMP` and raw CPU-id helpers. Risks are callers assuming `map_to_cpu()` can select arbitrary CPUs on UP builds and missing rebuild calls after topology changes. Test signals are compile coverage for SMP and UP builds and exported mapping behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/cpumap.h -->
