# sources/distributed-fs/ceph-client/arch/arm/mach-meson/Makefile

Purpose: Build glue for Meson ARM platform support.

Important APIs/types/functions: Always links `meson.o`; links `platsmp.o` for SMP builds.

Control flow: No runtime flow.

State and persistence: No runtime state.

Dependencies and integration points: Depends on Meson Kconfig and `CONFIG_SMP`.

Risks: Missing object entries would omit platform hooks.

Test signals: Compile Meson with SMP on/off.
