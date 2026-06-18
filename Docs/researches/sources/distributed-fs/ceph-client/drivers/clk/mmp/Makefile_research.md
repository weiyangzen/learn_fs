# sources/distributed-fs/ceph-client/drivers/clk/mmp/Makefile

Purpose: This Makefile defines the object composition for Marvell MMP clock support.

Important APIs, types, and functions: Core objects `clk-apbc.o`, `clk-apmu.o`, `clk-frac.o`, `clk-mix.o`, `clk-gate.o`, and `clk.o` are always built for the directory. Optional entries include `reset.o` for `CONFIG_RESET_CONTROLLER`, PXA168/PXA910 OF clock files for `CONFIG_MACH_MMP_DT`, MMP2 PLL/power/audio files for `CONFIG_COMMON_CLK_MMP2*`, PXA1908 APBC/APBCP/MPMU/APMU files for `CONFIG_COMMON_CLK_PXA1908`, and PXA1928 OF clocks for `CONFIG_ARCH_MMP`.

Control flow: Kbuild uses these assignments to compile and link platform-specific MMP clock providers. There is no runtime logic in this file.

State and persistence behavior: Build output composition is the only state.

Dependencies and integration points: The always-built helpers provide registration APIs used by multiple MMP SoC clock files. Optional SoC files layer device-tree providers and reset/power support on top.

Risks and edge cases: Always building helper objects assumes the parent Kbuild only enters this directory when MMP clock support is needed. Optional SoC objects depend on helper declarations in `clk.h`. Test signals include build coverage for reset-controller, legacy MMP DT, MMP2 audio, PXA1908, and ARCH_MMP configurations.
