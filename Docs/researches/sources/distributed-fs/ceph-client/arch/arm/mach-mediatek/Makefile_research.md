# sources/distributed-fs/ceph-client/arch/arm/mach-mediatek/Makefile

Purpose: Build glue for MediaTek ARM platform support.

Important APIs/types/functions: Always links `mediatek.o`; links `platsmp.o` when `CONFIG_SMP=y`.

Control flow: No runtime flow beyond Kbuild object selection.

State and persistence: No runtime state.

Dependencies and integration points: Depends on MediaTek Kconfig and SMP configuration.

Risks: SMP boot support is absent from UP builds by construction; future SoC-specific files need explicit entries.

Test signals: Compile MediaTek kernels with SMP on/off and verify object inclusion.
