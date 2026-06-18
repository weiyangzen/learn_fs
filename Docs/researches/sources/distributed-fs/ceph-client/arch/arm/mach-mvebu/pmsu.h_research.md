<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pmsu.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pmsu.h

Purpose: Internal header for MVEBU PMSU and low-level resume helpers. It exposes the small set of routines needed by SMP, cpuidle, and PM code without exporting PMSU register details.

Important APIs/types/functions: Declarations include `armada_xp_boot_cpu`, `mvebu_setup_boot_addr_wa`, `mvebu_v7_pmsu_idle_exit`, `armada_370_xp_cpu_resume`, `armada_370_xp_pmsu_idle_enter`, and `armada_38x_do_cpu_suspend`.

Control flow, state, and persistence: There is no state in the header; it binds C code to assembly symbols and PMSU implementation functions.

Dependencies and integration points: Declarations include `armada_xp_boot_cpu`, `mvebu_setup_boot_addr_wa`, `mvebu_v7_pmsu_idle_exit`, `armada_370_xp_cpu_resume`, `armada_370_xp_pmsu_idle_enter`, and `armada_38x_do_cpu_suspend`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are signature drift across C/assembly boundaries and missing declarations when low-level resume paths change. Test all MVEBU PM/SMP objects in one build with hotplug and suspend enabled.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 21 lines, 688 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pmsu.h -->
