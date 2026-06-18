# sources/distributed-fs/ceph-client/drivers/clk/tegra/Makefile

Lists Tegra clock driver objects and maps SoC/config symbols to the appropriate implementation files.

Common clock primitives such as `clk.o`, audio sync, device, DFLL core, dividers, peripheral wrappers, PLLs, super clocks, fixed clocks, and utilities are always built into this directory. SoC-specific files are gated by `CONFIG_ARCH_TEGRA_*`, `CONFIG_TEGRA_CLK_DFLL`, `CONFIG_TEGRA124_CLK_EMC`, and `CONFIG_CLK_TEGRA_BPMP`.

There is no runtime state. The file determines object composition and therefore the available registration functions and platform drivers. It integrates Kbuild, Kconfig symbols, and source modules under `drivers/clk/tegra`. It ensures common helpers are present before SoC clock initialization code references them.

Missing object entries cause unresolved symbols or absent clocks; overbroad `obj-y` entries can build dead code for unsupported SoCs. Test signals are allmodconfig/SoC defconfig builds and link coverage for BPMP, DFLL, EMC, and legacy Tegra generations.
