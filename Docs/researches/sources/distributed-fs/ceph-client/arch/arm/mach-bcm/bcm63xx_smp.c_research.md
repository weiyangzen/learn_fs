# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm63xx_smp.c

Purpose: provides BCM63138 Cortex-A9 SMP startup.

Important APIs/types/functions: `scu_a9_enable()` maps/enables SCU, adjusts possible CPU mask, and disables VFP when secondary CPU lacks VFP; `bcm63138_smp_boot_secondary()` writes BootLUT reset vector and calls `bcm63xx_pmb_power_on_cpu()`; `bcm63138_smp_ops` registers the method.

Control flow: prepare enables the SCU and sets possible CPUs. Boot maps the `brcm,bcm63138-bootlut`, writes `secondary_startup` to `BOOTLUT_RESET_VECT`, locates the CPU node, powers it via PMB, and unmaps.

State and persistence: possible CPU mask and VFP capability are global CPU-feature state; BootLUT and PMB hardware retain reset vector/power state.

Dependencies and integration: depends on Cortex-A9 SCU helpers, VFP feature control, BootLUT DT node, PMB helper, and `CPU_METHOD_OF_DECLARE("brcm,bcm63138")`.

Risks: kernel-mode NEON forces UP restriction because CPU1 lacks VFP. Missing BootLUT or CPU node prevents secondary boot; mismatched reset phandles fail in PMB.

Test signals: boot logs showing VFP policy, `/proc/cpuinfo` CPU count, CPU1 online, and failure paths for absent BootLUT nodes.
