# sources/distributed-fs/ceph-client/arch/arm/kernel/psci_smp.c

Purpose: adapts PSCI firmware calls to the ARM `smp_operations` interface for secondary CPU boot and CPU hotplug power-off.

Important APIs/types/functions: `psci_smp_available`, `psci_smp_ops`, `psci_boot_secondary`, and hotplug helpers `psci_cpu_disable`, `psci_cpu_die`, `psci_cpu_kill`.

Control flow: boot calls `psci_ops.cpu_on` with the target MPIDR and identity-mapped secondary startup address. Disable rejects missing `cpu_off` or trusted OS residency. Die invokes `cpu_off` with a power-down state and panics if it returns. Kill polls `affinity_info` up to ten times.

State and persistence: no local persistent state; relies on global `psci_ops` and CPU logical map.

Dependencies and integration: selected by `setup_arch` when DT PSCI is available and platform SMP ops are absent. Integrates with ARM hotplug, secondary startup assembly, XIP address translation, and PSCI firmware.

Risks: wrong entry address or MPIDR prevents boot; firmware may deny CPU_OFF; affinity polling races with shutdown. Test signals include secondary boot, CPU online/offline cycles, PSCI DT probing, trusted OS denial paths, and hotplug logs.
