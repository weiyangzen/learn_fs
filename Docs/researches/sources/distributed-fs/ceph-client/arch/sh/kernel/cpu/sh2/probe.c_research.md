<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/probe.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/probe.c

Purpose: identifies SH-2 CPU subtype and cache shape.

Important APIs/types/functions: `cpu_probe()`.

Control flow: sets `current_cpu_data` type/family/cache fields for configured SH7619 or J2-like CPUs.

State and persistence: persistent CPU metadata is later consumed by cpu_init and procfs.

Dependencies/integration: integrates early CPU init, cache setup, and subtype config.

Risks: incorrect probe data corrupts cache maintenance and CPU reporting.

Test signals: boot each SH-2 subtype and verify cache geometry and `/proc/cpuinfo`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/probe.c -->
