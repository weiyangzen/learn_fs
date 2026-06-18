# sources/distributed-fs/ceph-client/arch/arm/mach-berlin/platsmp.c

Purpose: starts and hotplugs secondary CPUs on Marvell Berlin SoCs.

Important APIs/types/functions: reset register constants, external `boot_inst` from `headsmp.S`, `berlin_perform_reset_cpu()`, `berlin_boot_secondary()`, `berlin_smp_prepare_cpus()`, optional `berlin_cpu_die()`/`berlin_cpu_kill()`, and `berlin_smp_ops`.

Control flow: prepare maps the CPU control node and writes a boot instruction/address sequence used by the secondary reset vector. Boot performs a software reset for the requested CPU. Hotplug death exits coherency and waits; kill resets the CPU and reports success.

State and persistence: global `cpu_ctrl` mapping is retained after prepare; hardware reset vector/control registers persist the programmed startup path.

Dependencies and integration: couples C SMP ops with `headsmp.S` boot instruction, OF CPU control registers, ARM v7 cache/coherency helpers, and Berlin DT machine descriptor.

Risks: reset-vector programming must match the ROM/reset expectations. Missing control mapping disables SMP. Hotplug behavior is minimal and assumes reset reliably stops the core.

Test signals: SMP boot on Berlin BG2/BG2CD/BG2Q, CPU hotplug loops under `CONFIG_HOTPLUG_CPU`, and DT control-node validation.
