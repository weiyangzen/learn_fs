# sources/distributed-fs/ceph-client/drivers/clk/meson/Kconfig

Purpose: this Kconfig menu defines build-time configuration for Amlogic Meson common clock helpers and SoC-specific clock controller drivers. It gates the Meson clock driver family behind `ARCH_MESON || COMPILE_TEST`.

Important symbols: helper symbols include `COMMON_CLK_MESON_REGMAP`, `DUALDIV`, `MPLL`, `PHASE`, `PLL`, `SCLK_DIV`, `VID_PLL_DIV`, `VCLK`, `CLKC_UTILS`, `AO_CLKC`, and `CPU_DYNDIV`. SoC/controller symbols include `COMMON_CLK_MESON8B`, `COMMON_CLK_GXBB`, `COMMON_CLK_AXG`, `COMMON_CLK_AXG_AUDIO`, `COMMON_CLK_A1_PLL`, `COMMON_CLK_A1_PERIPHERALS`, `COMMON_CLK_C3_PLL`, `COMMON_CLK_C3_PERIPHERALS`, `COMMON_CLK_G12A`, `COMMON_CLK_S4_PLL`, `COMMON_CLK_S4_PERIPHERALS`, `COMMON_CLK_T7_PLL`, and `COMMON_CLK_T7_PERIPHERALS`.

Control flow: Kconfig selection controls which objects the Makefile builds. Helper symbols are mostly tristate and selected by SoC drivers. SoC entries select the common helper implementations they need, such as regmap, PLL, MPLL, dualdiv, AO clock controller, CPU dynamic divider, video clock helpers, reset controller, and syscon support.

State and persistence: this file affects kernel configuration state, not runtime state. Selected options are persisted in `.config` and determine which modules or built-ins are compiled.

Dependencies and integration points: the menu integrates with the kernel build system, architecture symbols, reset-controller support, regmap/syscon, auxiliary bus support for AXG audio, and optional SCMI clock support through `imply` on newer platforms.

Risks: missing `select` entries cause link failures or runtime missing helpers; overly broad `select` entries build unnecessary code. Some SoC configs default to `ARCH_MESON`, so dependency drift can change default kernel size. `COMMON_CLK_AXG_AUDIO` implies but does not hard-select `RESET_MESON_AUX`, so reset functionality may depend on broader config resolution.

Test signals: run `make olddefconfig` and compile for `ARCH_MESON`, ARM64 `COMPILE_TEST`, and module builds. Verify selected object lists match expected helpers and that all SoC clock drivers link when enabled independently.
