# sources/distributed-fs/ceph-client/drivers/clk/aspeed/Kconfig

Purpose: this Kconfig fragment exposes Aspeed BMC clock controller support.

Important symbols: `COMMON_CLK_ASPEED` covers older Aspeed G4/G5 SoCs such as AST2400/AST2500, depends on `ARCH_ASPEED || COMPILE_TEST`, defaults to `ARCH_ASPEED`, and selects `MFD_SYSCON` plus `RESET_CONTROLLER`. `COMMON_CLK_AST2700` enables AST2700 clock support and depends on the same architecture/compile-test condition. AST2600 is controlled by `CONFIG_MACH_ASPEED_G6` in the Makefile rather than a symbol here.

Control flow/state: Kconfig selects which platform drivers are compiled. Runtime matching is by SCU compatible strings.

Dependencies and risks: older drivers use syscon/regmap and register reset controllers from the clock driver, so missing selects would break builds. AST2700 uses auxiliary reset device creation rather than selecting reset here, likely relying on broader platform dependencies. Test signals include Aspeed defconfigs, compile-test, and DT compatible coverage for AST2400/2500/2600/2700.
