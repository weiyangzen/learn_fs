# sources/distributed-fs/ceph-client/arch/arm/mach-axxia/platsmp.c

Purpose: implements secondary CPU bring-up for LSI Axxia AXM55xx systems.

Important APIs/types/functions: defines reset-controller offsets `SC_CRIT_WRITE_KEY` and `SC_RST_CPU_HOLD`; `write_release_addr()`, `axxia_boot_secondary()`, `axxia_smp_prepare_cpus()`, and `axxia_smp_ops`.

Control flow: prepare maps the reset controller from the `syscon` compatible node and parks all secondary CPUs in reset while writing the physical `secondary_startup` release address. Booting a CPU clears that CPU's hold bit after using the critical-write key.

State and persistence: persistent mapped syscon state is used for subsequent CPU starts; the reset controller holds per-CPU release state.

Dependencies and integration: depends on OF syscon lookup, ARM `secondary_startup`, `smp_operations`, and Axxia reset register ABI.

Risks: incorrect reset-controller mapping or release address leaves secondary CPUs parked. The code assumes physical startup address fits the platform register and that CPU numbering matches reset bits.

Test signals: SMP boot on AXM55xx DT, CPU hotplug where applicable, and logs for reset-controller lookup failures.
