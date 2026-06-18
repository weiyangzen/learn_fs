<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/platsmp-a9.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/platsmp-a9.c

Purpose: SMP support for MVEBU Cortex-A9 SoCs such as Armada 375/38x/39x. It writes the secondary startup address, wakes the target CPU, deasserts reset, and supplies Armada 38x hotplug hooks.

Important APIs/types/functions: Key routines are `mvebu_cortex_a9_boot_secondary`, `armada_38x_secondary_init`, `armada_38x_cpu_die`, and `armada_38x_cpu_kill`; CPU methods are declared for `marvell,armada-375-smp`, `-380-smp`, and `-390-smp`.

Control flow, state, and persistence: Boot flow maps Linux CPU to hardware CPU, stores the startup address in either system-controller or PMSU registers, issues a memory barrier, sends a wake IPI, then deasserts reset. Hotplug-offlined CPUs enter deep idle and exit through PMSU idle cleanup.

Dependencies and integration points: Key routines are `mvebu_cortex_a9_boot_secondary`, `armada_38x_secondary_init`, `armada_38x_cpu_die`, and `armada_38x_cpu_kill`; CPU methods are declared for `marvell,armada-375-smp`, `-380-smp`, and `-390-smp`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include DT compatible strings, `mvebu_cpu_reset_deassert`, PMSU, system-controller boot address registers, and generic ARM SMP. Risks are wrong boot-address backend per SoC and broken deep-idle hotplug. Test SMP boot, CPU online/offline, and kexec on Armada 375 versus 38x/39x.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 111 lines, 3245 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/platsmp-a9.c -->
