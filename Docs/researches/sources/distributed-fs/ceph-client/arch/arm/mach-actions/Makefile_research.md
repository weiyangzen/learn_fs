# sources/distributed-fs/ceph-client/arch/arm/mach-actions/Makefile

Purpose: builds Actions platform SMP support. It adds `platsmp.o` when `CONFIG_SMP` is enabled.

Control flow is build-time only. There is no runtime state in the file. Dependencies are `ARCH_ACTIONS`, `CONFIG_SMP`, and the matching CPU method declared in `platsmp.c`. Risks are missing SMP object for SMP-capable DTs or compiling it without required selected drivers. Test signals are ARM Actions SMP builds and secondary CPU boot on S500.
