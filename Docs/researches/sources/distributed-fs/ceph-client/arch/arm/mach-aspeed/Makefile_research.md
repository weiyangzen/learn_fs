# sources/distributed-fs/ceph-client/arch/arm/mach-aspeed/Makefile

Purpose: builds Aspeed SMP support by adding `platsmp.o` when `CONFIG_SMP` is enabled.

Control flow is build-time only. Dependencies are AST2600 SMP DT using the declared CPU method. Risks are compiling SMP support without the expected secure boot memory node or missing SMP object in AST2600 SMP builds. Test signals are successful SMP build and AST2600 secondary CPU bring-up.
