# sources/distributed-fs/ceph-client/arch/arm/mach-mstar/mstarv7.c

Purpose: MStar/SigmaStar ARMv7 DT machine support, including a SoC-specific memory barrier and simple CPU1 release.

Important APIs/types/functions: Defines `mstarv7_mb()`, optional `mstarv7_boot_secondary()`, `mstarv7_smp_ops`, `mstarv7_init()`, root-compatible table, and `DT_MACHINE_START(MSTARV7_DT, ...)`.

Control flow: Machine init maps the `mstar,l3bridge` node and installs `soc_mb = mstarv7_mb`; the barrier toggles the L3 bridge flush trigger and polls status done using relaxed MMIO so it does not recurse into itself. SMP boot currently supports only CPU1: it maps `mstar,smpctrl`, writes the low/high 16-bit physical `secondary_startup_arm` address, writes unlock magic `0xbabe`, sends a wakeup IPI, and unmaps the control block.

State and persistence: Global state is `l3bridge` and the global architecture memory-barrier hook `soc_mb`. Hardware state includes L3 bridge flush/status registers and CPU1 SMP control boot/unlock registers.

Dependencies and integration points: Depends on DT nodes `mstar,l3bridge` and `mstar,smpctrl`, ARM heavy memory-barrier hook support selected by Kconfig, GIC/arch timer setup, and root compatibles for Infinity/Mercury families.

Risks: If L3 bridge mapping fails the code warns that DMA will be broken, because devices can see stale CPU writes. The barrier has no lock and can be reentered from interrupts. SMP supports only CPU1 and does not `of_node_put()` the SMP control node on the success path.

Test signals: Boot with Ethernet or other DMA devices to validate the custom barrier, run SMP CPU1 online tests, and check behavior when L3 bridge DT node is missing.
