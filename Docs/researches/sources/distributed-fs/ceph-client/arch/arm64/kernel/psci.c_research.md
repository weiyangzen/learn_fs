# sources/distributed-fs/ceph-client/arch/arm64/kernel/psci.c

Purpose: this file provides ARM64 `cpu_operations` backed by PSCI firmware calls. It is responsible for preparing, booting, disabling, powering off, and polling secondary CPUs when PSCI is the selected CPU bring-up mechanism.

Important APIs and state: `cpu_psci_ops` exposes `.cpu_init`, `.cpu_prepare`, `.cpu_boot`, and, with hotplug, `.cpu_can_disable`, `.cpu_disable`, `.cpu_die`, and `.cpu_kill`. The implementation uses global `psci_ops` callbacks and `cpu_logical_map()` MPIDR values.

Control flow: prepare verifies `psci_ops.cpu_on` exists. Boot calls `cpu_on(cpu_logical_map(cpu), __pa_symbol(secondary_entry))` and logs failures except `-EPERM`. Hotplug disable rejects missing `cpu_off` and CPUs where a trusted OS is resident. Die calls PSCI `cpu_off()` with a power-down state. Kill optionally polls `affinity_info()` for up to about 100 ms until firmware reports the CPU off.

Dependencies and integration: integrates with generic SMP CPU ops, PSCI DT/ACPI initialization from setup, ARM64 secondary entry code, jiffies delays, and trusted-OS residency helpers.

Risks: PSCI availability and firmware behavior dominate correctness. `cpu_kill()` can race with `cpu_die()`, so it polls rather than assuming immediate state. Systems lacking `affinity_info` cannot verify shutdown. Trusted OS residency can prevent CPU offlining.

Test signals: SMP boot, CPU hotplug online/offline cycles, PSCI error logs, and suspend/kexec interactions. Firmware conformance issues show as failed boot of secondary CPUs or timeout warnings during hotplug.
