<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-npcm/headsmp.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-npcm/headsmp.S

Purpose: NPCM7xx secondary CPU startup shim. It compensates for boot ROM not entering secondaries in SVC mode, masks interrupts, and jumps to generic ARM secondary startup.

Important APIs/types/functions: The single symbol is `npcm7xx_secondary_startup`, using `safe_svcmode_maskall` and `secondary_startup`.

Control flow, state, and persistence: State changes are CPU mode and interrupt masks; no memory state is stored by the file.

Dependencies and integration points: The single symbol is `npcm7xx_secondary_startup`, using `safe_svcmode_maskall` and `secondary_startup`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include ARMv7 assembler support and the SMP boot code writing this physical address to the GCR scratchpad. Test secondary CPU boot and hotplug on NPCM7xx.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 19 lines, 428 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-npcm/headsmp.S -->
