<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/platsmp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/platsmp.c

Purpose: Armada XP and 98DX3236 SMP support. It validates BootROM mapping, prepares coherency, synchronizes CPU clocks, sets per-CPU boot vectors, deasserts reset, and provides CPU hotplug by deep-idle entry.

Important APIs/types/functions: Important routines include `armada_xp_boot_secondary`, `armada_xp_smp_init_cpus`, `armada_xp_smp_prepare_cpus`, `armada_xp_sync_secondary_clk`, 98DX resume/boot helpers, and the `armada_xp_smp_ops`/`mv98dx3236_smp_ops` CPU methods.

Control flow, state, and persistence: The primary control path flushes caches, marks the boot CPU coherent, checks the bootrom DT resource equals `0xfff00000/1MiB`, captures boot CPU clock rate, and later writes PMSU or resume-controller boot addresses before waking secondary CPUs.

Dependencies and integration points: Important routines include `armada_xp_boot_secondary`, `armada_xp_smp_init_cpus`, `armada_xp_smp_prepare_cpus`, `armada_xp_sync_secondary_clk`, 98DX resume/boot helpers, and the `armada_xp_smp_ops`/`mv98dx3236_smp_ops` CPU methods. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: State includes the cached boot CPU clock and hardware boot-address registers. Dependencies are DT, clock framework, PMSU, CPU reset, coherency fabric, and BootROM layout. Risks include panic on DT mapping mismatches, clock-reference leaks, and platform-specific CPU count limits. Test SMP boot, hotplug, clock rates, and 98DX single-secondary assumptions.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 255 lines, 6468 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/platsmp.c -->
