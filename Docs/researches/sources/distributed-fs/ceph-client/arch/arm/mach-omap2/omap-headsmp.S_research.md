<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-headsmp.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-headsmp.S

## Purpose
`omap-headsmp.S` provides secondary CPU startup entry points for OMAP4 and OMAP5 SMP boot and hotplug resume. These routines run before normal C environment setup and release secondaries from ROM or hardware holding loops.

## Important APIs, Types, and Functions
Assembly entry points are `omap_secondary_startup`, `omap5_secondary_startup`, `omap5_secondary_hyp_startup`, `omap4_secondary_startup`, and `omap4460_secondary_startup`. Important constants are `AUX_CORE_BOOT0_PA`, `API_HYP_ENTRY`, and `OMAP44XX_GIC_DIST_BASE`.

## Control Flow
`omap_secondary_startup` branches to the ARM common `secondary_startup` when SMP is enabled, otherwise loops in WFI. OMAP5 startup polls AuxCoreBoot0 until the shifted release value matches the core ID, optionally enters HYP mode through an SMC ROM call, then jumps to common startup. OMAP4 startup reads AuxCoreBoot0 through SMC, waits for release, and jumps to common startup. OMAP4460 additionally reenables the GIC distributor as part of the ROM/GIC erratum workaround.

## State and Persistence Behavior
State is CPU register state and hardware release registers. No memory persistence is created. The routines depend on stack setup by the primary CPU and on AuxCoreBoot registers retaining release values.

## Dependencies and Integration Points
It depends on ARM assembly/linkage macros, `secondary_startup`, secure monitor calls, AuxCoreBoot registers, and OMAP SMP C code in `omap-smp.c` and `omap-mpuss-lowpower.c`.

## Risks
Any register clobbering, wrong release-bit shift, or wrong startup physical address can hang CPU1 before console output. HYP-mode startup depends on boot CPU mode and ROM SMC behavior. OMAP4460 GIC erratum handling must match the C-side distributor disable flow.

## Test Signals
Boot SMP OMAP4/OMAP5, online/offline CPU1 repeatedly, kexec, and suspend/resume from CPU-off states. Confirm secondary CPUs reach `smp_secondary_init`, HYP-mode boot works when primary is in HYP, and OMAP4460 does not lose interrupts after CPU1 wake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-headsmp.S -->
