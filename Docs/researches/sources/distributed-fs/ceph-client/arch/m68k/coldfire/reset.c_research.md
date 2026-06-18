# sources/distributed-fs/ceph-client/arch/m68k/coldfire/reset.c

Purpose: common ColdFire software reset setup for parts that can reset through `MCFSIM_SYPCR` or `MCF_RCR`.

Important APIs and functions: compile-time-selected `mcf_cpu_reset()` and `mcf_setup_reset()` as an `arch_initcall()`.

Control flow and state: reset disables local interrupts, then either programs SYPCR for watchdog soft reset and spins forever, or writes `MCF_RCR_SWRESET` to the reset-control register. Init assigns `mach_reset = mcf_cpu_reset`.

Dependencies and integration: Linux machine reset hook, ColdFire SIM/reset-control registers, and SoC-specific files that do not override reset. M5272 and 54xx have their own reset implementations and do not rely on this path.

Risks and test signals: the comments mention exceptions for 5272 and 547x; build selection must avoid duplicate `mcf_cpu_reset()` definitions and wrong reset method. Test reboot command on each supported SoC, verify interrupts disabled before reset, and confirm no return after reset register write.
