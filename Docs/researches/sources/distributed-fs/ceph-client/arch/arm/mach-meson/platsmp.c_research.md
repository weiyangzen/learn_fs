# sources/distributed-fs/ceph-client/arch/arm/mach-meson/platsmp.c

Purpose: Amlogic Meson SMP boot support for Meson8/8b/8m2 and Meson6 SCU-based systems.

Important APIs/types/functions: Defines Meson register offsets, `meson_smp_ops`, `meson8_smp_ops`, `meson_smp_prepare_cpus()`, `meson8_smp_prepare_cpus()`, `meson_boot_secondary()`, `meson8_boot_secondary()`, `meson_smp_map()`, and validation helpers.

Control flow: Prepare maps SCU and SRAM/sysctrl as needed, enables SCU, clears secondary CPU reset/address registers, and writes the boot address for Meson8. Boot for Meson8 writes `secondary_startup` into mailbox and wakes via SRAM/sysctrl registers; Meson6 toggles per-core reset through SCU/system registers and waits for secondary startup.

State and persistence: Global state includes mapped SCU, SRAM, and sysctrl bases plus validated physical resources. Hardware state includes SCU enable, CPU reset controls, boot mailbox, and power/clock bits.

Dependencies and integration points: Depends on DT nodes for SCU/SRAM/sysctrl, ARM SCU helpers, SMP core, and SoC-specific compatible strings.

Risks: Mapping/validation is critical because wrong SRAM/sysctrl resources mean writes to the wrong boot registers. CPU count assumptions and boot timeouts are platform-specific.

Test signals: Boot all secondary CPUs on Meson6/8 variants, check DT resource validation, and exercise CPU online/offline where supported.
