<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/probe.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/probe.c

Purpose: identifies SH-2A CPU subtype and capabilities.

Important APIs/types/functions: `cpu_probe()`.

Control flow: fills `current_cpu_data` with subtype, family, cache, and feature information based on config/CPU.

State and persistence: persistent metadata drives cache init, procfs, and feature-dependent code.

Dependencies/integration: integrates with `cpu_init()`, FPU support, and subtype setup files.

Risks: wrong cache or feature flags break cache maintenance/FPU reporting.

Test signals: boot each SH2A subtype and check cpuinfo/cache/FPU behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/probe.c -->
