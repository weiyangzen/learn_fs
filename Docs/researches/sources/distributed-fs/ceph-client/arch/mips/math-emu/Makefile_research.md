<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/Makefile

Purpose: Builds the Linux/MIPS software FPU emulator and IEEE754 helper library objects.

Important APIs/types/functions: `obj-y` includes `cp1emu.o`, IEEE754 core, double/single arithmetic, conversion, compare, fused multiply-add, class/min/max, and delay-slot emulation. `lib-y` includes helpers used as library code such as sqrt and long conversions. `me-debugfs.o` is conditional on `CONFIG_DEBUG_FS`.

Control flow: Build rules ensure the emulator and arithmetic helpers are always available for MIPS math emulation.

State and persistence: Build metadata only.

Dependencies and integration: Links with MIPS exception handling and FPU emulator entry points.

Risks: Removing an arithmetic object can break instruction cases in `cp1emu.c`.

Test signals: Kernel builds with FPU emulation should link all `ieee754*` references and optional debugfs stats when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/Makefile -->
