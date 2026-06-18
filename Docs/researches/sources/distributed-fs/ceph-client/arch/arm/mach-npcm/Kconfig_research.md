<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-npcm/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-npcm/Kconfig

Purpose: Kconfig for Nuvoton NPCM BMC platforms. It supports WPCM450 on ARMv5 and NPCM7xx on ARMv7, selecting timer, pinctrl, GIC/SCU/TWD, errata, PL310 workarounds, GPIO, and syscon as needed.

Important APIs/types/functions: Symbols are `ARCH_NPCM`, `ARCH_WPCM450`, and `ARCH_NPCM7XX`.

Control flow, state, and persistence: No runtime state exists. The file defines architecture and SoC support boundaries.

Dependencies and integration points: Symbols are `ARCH_NPCM`, `ARCH_WPCM450`, and `ARCH_NPCM7XX`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are architecture dependency mismatches and SMP errata selections. Test allmodconfig-style ARMv5 and ARMv7 NPCM builds.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 41 lines, 954 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-npcm/Kconfig -->
