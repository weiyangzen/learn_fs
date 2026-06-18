# sources/distributed-fs/ceph-client/drivers/clk/ralink/Kconfig

Purpose: This Kconfig file declares build switches for Ralink/MediaTek MIPS clock drivers in this directory.

Important APIs, types, and functions: It defines `CONFIG_CLK_MT7621` and `CONFIG_CLK_MTMIPS`. Both are `bool` symbols gated by `RALINK || COMPILE_TEST`, and both select `MFD_SYSCON` because the drivers obtain SoC system-controller registers through syscon/regmap.

Control flow: Kconfig selection determines whether the corresponding objects are compiled by the local Makefile. `CLK_MT7621` builds the MT7621-specific clock/reset provider, while `CLK_MTMIPS` builds the shared provider for RT2880/RT305x/RT3352/RT3883/RT5350/MT7620/MT76x8 class SoCs.

State and persistence: No runtime state. The file controls kernel configuration state and therefore object inclusion in built kernels.

Dependencies and integration: Integrates with top-level clock Kconfig inclusion and the local Makefile. The selected drivers also require reset-controller and clk-provider APIs in code, but this Kconfig only explicitly selects syscon support.

Risks: Because the symbols are bools rather than tristates, drivers are built in when selected. Missing dependency selections here can surface as link errors in unusual COMPILE_TEST configurations. Separating MT7621 from MTMIPS is important because their DT compatibles and clock topologies differ.

Test signals: Run `make ARCH=mips allmodconfig` or relevant Ralink defconfig, ensure both symbols select cleanly under COMPILE_TEST, and verify the Makefile emits exactly `clk-mt7621.o` or `clk-mtmips.o` for the matching symbol.
