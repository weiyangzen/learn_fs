# sources/distributed-fs/ceph-client/arch/arm/mach-milbeaut/Makefile

Purpose: Build glue for Milbeaut platform support.

Important APIs/types/functions: Links `platsmp.o` when SMP is enabled.

Control flow: No runtime flow.

State and persistence: No runtime state.

Dependencies and integration points: Depends on `CONFIG_SMP` and Milbeaut Kconfig.

Risks: UP builds omit any Milbeaut SMP boot hooks.

Test signals: Compile Milbeaut SMP and non-SMP configurations.
