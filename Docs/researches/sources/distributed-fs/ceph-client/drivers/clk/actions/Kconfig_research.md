# sources/distributed-fs/ceph-client/drivers/clk/actions/Kconfig

Purpose: this fragment exposes clock controller support for Actions Semi OWL SoCs. `CLK_ACTIONS` is the family-wide switch, and `CLK_OWL_S500`, `CLK_OWL_S700`, and `CLK_OWL_S900` enable individual SoC clock descriptors.

Important symbols: `CLK_ACTIONS` depends on `ARCH_ACTIONS || COMPILE_TEST`, selects `REGMAP_MMIO` and `RESET_CONTROLLER`, and defaults to `ARCH_ACTIONS`. The S500 option supports 32-bit Actions platforms, while S700 and S900 additionally depend on `ARM64 && ARCH_ACTIONS` unless `COMPILE_TEST` is used.

Control flow/state: Kconfig only controls compilation of the common `clk-owl` library and the SoC-specific drivers. Runtime binding is handled by each SoC driver's OF compatible string.

Dependencies and risks: the family option must select reset and MMIO regmap support because the SoC probes register reset controllers and use a regmap over CMU registers. SoC symbol dependencies protect against invalid platform builds while retaining compile coverage. Test signals are `COMPILE_TEST`, Actions defconfigs, and DT binding compatibility for `actions,s500-cmu`, `actions,s700-cmu`, and `actions,s900-cmu`.
