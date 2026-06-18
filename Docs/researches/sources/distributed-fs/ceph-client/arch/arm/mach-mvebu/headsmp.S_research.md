<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/headsmp.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/headsmp.S

Purpose: Armada XP secondary CPU assembly entry point. It switches to BE8 when needed, calls low-level coherency helpers, joins the SMP group, enables hardware coherency, and branches into the generic ARM `secondary_startup` path.

Important APIs/types/functions: `armada_xp_secondary_startup` is the only exported entry. It depends on `ll_add_cpu_to_smp_group`, `ll_enable_coherency`, `secondary_startup`, ARM assembler macros, and the coherency low-level implementation in the same platform.

Control flow, state, and persistence: The control path is intentionally short because it runs before normal C runtime setup on a secondary CPU. Persistent state is only the hardware coherency fabric registers touched by the helper calls.

Dependencies and integration points: `armada_xp_secondary_startup` is the only exported entry. It depends on `ll_add_cpu_to_smp_group`, `ll_enable_coherency`, `secondary_startup`, ARM assembler macros, and the coherency low-level implementation in the same platform. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: If the hard-coded early coherency assumptions drift from the SoC memory map, secondary CPUs can hang before console output is available. Test with SMP boot, CPU hotplug, kexec, and both endian configurations on Armada XP.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 37 lines, 1000 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/headsmp.S -->
