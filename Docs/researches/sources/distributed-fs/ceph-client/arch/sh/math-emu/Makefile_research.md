# sources/distributed-fs/ceph-client/arch/sh/math-emu/Makefile

Purpose: builds the SH software floating-point emulator object.

Important variable: `obj-y := math.o`.

Control flow: Kbuild includes `math.o` when the containing configuration selects SH FPU emulation.

State and persistence: build-time object selection only.

Dependencies and integration: connects `arch/sh/math-emu/math.c` to the architecture build.

Risks: missing inclusion leaves reserved FPU instruction traps without emulator support.

Test signals: successful build with `CONFIG_SH_FPU_EMU` and execution of FPU instructions on no-FPU hardware.
