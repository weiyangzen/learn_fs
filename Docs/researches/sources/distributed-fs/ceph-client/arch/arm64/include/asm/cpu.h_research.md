## sources/distributed-fs/ceph-client/arch/arm64/include/asm/cpu.h

Purpose: declares per-CPU CPU identification and feature snapshot structures for arm64.

Important APIs/types/functions: defines `struct cpuinfo_32bit` and `struct cpuinfo_arm64`, declares per-CPU `cpu_data`, and prototypes `cpuinfo_store_cpu`, `cpuinfo_store_boot_cpu`, `init_cpu_features`, and `update_cpu_features`.

Control flow: implemented code stores boot and per-CPU ID registers, then updates feature state when CPUs come online.

State and persistence: `cpu_data` persists each CPU's MIDR/MPIDR, cache type, ID registers, ZCR/SMCR, and AArch32 info while the kernel runs.

Dependencies and integration: depends on CPU hotplug, sysfs CPU objects, cpufeature, topology, and scheduler bring-up.

Risks: stale or inconsistent ID snapshots cause wrong capability decisions on heterogeneous systems. Test signals are CPU hotplug, heterogeneous big.LITTLE boot, sysfs CPU info, and cpufeature sanity warnings.
