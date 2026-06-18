<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-smp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-smp.c

## Purpose
`omap-smp.c` implements OMAP4/OMAP5/DRA7 SMP bring-up, secondary CPU initialization, CPU1 release, SCU setup, kexec/reset safety checks, and erratum/security hardening for secondary cores.

## Important APIs, Types, and Functions
The exported SMP operations object is `omap4_smp_ops`. Public helper `omap4_get_scu_base()` returns the mapped SCU base. Important internals include `struct omap_smp_config`, SoC-specific config records, `omap5_erratum_workaround_801819()`, `omap5_secondary_harden_predictor()`, `omap4_secondary_init()`, `omap4_boot_secondary()`, `omap4_smp_init_cpus()`, `omap4_smp_cpu1_startup_valid()`, `omap4_smp_maybe_reset_cpu1()`, and `omap4_smp_prepare_cpus()`.

## Control Flow
Early CPU init uses CPUID to discover A9/A15 core count and sets possible CPUs. Prepare selects SoC-specific reset/startup configuration, maps CPU1 reset control, enables SCU, optionally resets CPU1 if it appears parked in the current kernel address range, and writes the secondary startup physical address through secure AuxCoreBoot APIs or wakeupgen MMIO. Booting CPU1 writes release bits, handles OMAP4 SGI wake limitations by forcing CPU1 clockdomain wake after first boot, applies GIC erratum handling, and sends a wakeup IPI. Secondary init applies secure SMP ACTLR setup and OMAP5/DRA7 ACR hardening.

## State and Persistence Behavior
State includes static `cfg`, cached CPU1 clockdomain/powerdomain pointers, and a `booted` flag. Hardware state includes AuxCoreBoot registers, SCU enable, CPU1 reset control, powerdomain next state, and ACR/ACTLR secure settings. No filesystem persistence exists.

## Dependencies and Integration Points
It depends on ARM SMP core, SCU, GIC helpers, secure APIs, wakeupgen base, clockdomain/powerdomain, virtualization boot mode, CPUID, OMAP SoC detection, and assembly startup symbols. It integrates with `omap-headsmp.S`, `omap-mpuss-lowpower.c`, `omap-hotplug.c`, and `omap4-common.c`.

## Risks
CPU1 boot is timing and firmware sensitive. Wrong AuxCoreBoot values, stale kexec startup addresses, missing reset, or incorrect secure API selection can hang secondary bring-up. Erratum/hardening SMCs affect CPU security and performance. GIC distributor workaround must be coordinated with assembly reenable path.

## Test Signals
Boot SMP on OMAP443x/446x/OMAP5/DRA7, verify both CPUs online, run CPU hotplug loops, kexec reboot, suspend/resume, and branch-predictor hardening checks. Confirm no "CPU1 not parked" surprises except expected cases and no lost local-timer warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-smp.c -->
