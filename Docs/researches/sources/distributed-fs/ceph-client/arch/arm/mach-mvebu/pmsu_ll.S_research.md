<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pmsu_ll.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pmsu_ll.S

Purpose: Low-level MVEBU resume and boot workaround assembly. It contains resume entry points for Armada 370/XP and Armada 38x plus a tiny BootROM replacement snippet copied to SRAM.

Important APIs/types/functions: Symbols include `armada_38x_scu_power_up`, `armada_370_xp_cpu_resume`, `armada_38x_cpu_resume`, and `mvebu_boot_wa_start/end`.

Control flow, state, and persistence: Control flow runs before normal kernel C context: resume code re-enables coherency or SCU state, returns through ARM CPU resume machinery, and the boot workaround reads a PMSU boot address register then jumps to it.

Dependencies and integration points: Symbols include `armada_38x_scu_power_up`, `armada_370_xp_cpu_resume`, `armada_38x_cpu_resume`, and `mvebu_boot_wa_start/end`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include ARM assembler macros, CPU resume conventions, PMSU boot-address register layout, and coherency helpers. Risks are instruction-size/layout assumptions, endianness, and copied-code patching of the last word with a register address. Test suspend/resume on Armada 370/XP/38x and verify SRAM workaround code length/patched address.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 71 lines, 1853 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pmsu_ll.S -->
