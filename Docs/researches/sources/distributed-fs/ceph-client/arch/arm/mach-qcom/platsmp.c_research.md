# sources/distributed-fs/ceph-client/arch/arm/mach-qcom/platsmp.c

Purpose: Qualcomm ARM secondary CPU bring-up and CPU hotplug support for several legacy enable-methods.

Important APIs/types/functions: release routines are `scss_release_secondary()`, `cortex_a7_release_secondary()`, `kpssv1_release_secondary()`, and `kpssv2_release_secondary()`. Boot wrappers call `qcom_boot_secondary()`. `qcom_smp_prepare_cpus()` programs the cold boot address through `qcom_scm_set_cold_boot_addr(secondary_startup_arm)`. `CPU_METHOD_OF_DECLARE` registers DT enable methods.

Control flow: prepare-cpus asks secure firmware to set the secondary boot vector and disables present CPUs if that fails. Per-CPU boot performs a one-time power/reset sequence using DT phandles to ACC/SAW/L2 nodes, records `cold_boot_done`, then sends a wakeup IPI. Hotplug `qcom_cpu_die()` waits in WFI.

State and persistence: per-CPU `cold_boot_done` avoids repeating cold release. Hardware state is in ACC, SAW, GCC, and power-gate registers.

Dependencies and integration points: depends on DT CPU nodes, Qualcomm SCM firmware, MMIO mapping, ARM SMP ops, and power/reset register layouts for MSM8660, Cortex-A7, KPSS v1, and KPSS v2.

Risks: power sequences are SoC-specific and delay/barrier sensitive. Missing DT phandles disable CPU bring-up. SCM failure disables SMP entirely. CPU hotplug only idles, so platform power-down is limited.

Test signals: secondary CPU online for each compatible string, SCM failure path, DT phandle validation, CPU hotplug WFI path, and stress with repeated CPU onlining.
