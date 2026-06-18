<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-npcm/platsmp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-npcm/platsmp.c

Purpose: NPCM7xx SMP bring-up. It enables the Cortex-A9 SCU and writes the secondary startup physical address into the GCR scratchpad before sending an event.

Important APIs/types/functions: Main functions are `npcm7xx_smp_prepare_cpus`, `npcm7xx_smp_boot_secondary`, and the CPU method for `nuvoton,npcm750-smp`.

Control flow, state, and persistence: Control flow maps the SCU node to call `scu_enable`; boot-secondary maps `nuvoton,npcm750-gcr`, writes `__pa_symbol(npcm7xx_secondary_startup)` at `NPCM7XX_SCRPAD_REG`, and executes `dsb_sev()`.

Dependencies and integration points: Main functions are `npcm7xx_smp_prepare_cpus`, `npcm7xx_smp_boot_secondary`, and the CPU method for `nuvoton,npcm750-smp`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include DT SCU/GCR nodes, physical address translation, and `headsmp.S`. Risks are per-boot remapping overhead, missing node cleanup on some error paths, and scratchpad register offset drift. Test SMP boot, DT node absence errors, and secondary CPU mode.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 78 lines, 1791 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-npcm/platsmp.c -->
