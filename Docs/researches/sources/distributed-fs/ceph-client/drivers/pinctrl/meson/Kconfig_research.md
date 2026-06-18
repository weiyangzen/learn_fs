# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/Kconfig

## Purpose
This Kconfig file defines build-time configuration for Amlogic Meson and newer Amlogic pinctrl drivers. `PINCTRL_MESON` is the menuconfig gate and selects common pinctrl, pinmux, pinconf, gpiolib, generic pinconf, and `REGMAP_MMIO` support.

## Important Symbols
`PINCTRL_MESON` is a tristate defaulting to `ARCH_MESON` and requiring OF plus either `ARCH_MESON` or `COMPILE_TEST`. Sub-options cover older Meson8/Meson8b/GXBB/GXL drivers using `PINCTRL_MESON8_PMX`, AXG/G12A/A1/S4/C3/T7 drivers using `PINCTRL_MESON_AXG_PMX`, and `PINCTRL_AMLOGIC_A4`, a bool driver for the newer generic Amlogic pinctrl style. `PINCTRL_AMLOGIC_C3` and `PINCTRL_AMLOGIC_T7` remain per-SoC tristate drivers.

## Control Flow And Integration
Kconfig has no runtime control flow, but it controls which objects the Makefile builds. Hidden symbols `PINCTRL_MESON8_PMX` and `PINCTRL_MESON_AXG_PMX` are selected by SoC entries to include shared mux backends. The A4 option does not select `PINCTRL_MESON_AXG_PMX`; it builds its own `pinctrl-amlogic-a4.o` implementation.

## State And Persistence
Configuration state persists in kernel `.config`. It affects compiled objects and module availability but has no runtime state.

## Dependencies
All entries depend on the top-level menu. Most newer SoC drivers depend on ARM64 or `COMPILE_TEST`. Older Meson8 entries depend on ARM or `COMPILE_TEST`. The menu selects generic dependencies required by the common Meson and Amlogic code paths.

## Risks
`PINCTRL_AMLOGIC_A4` is `bool` rather than `tristate`, so it cannot be built as a module even though nearby drivers can. Help text says new Amlogic SoCs only need DTS additions; that is true only for SoCs whose register layout matches the generic A4/S6/S7 parser and quirks. Missing selects here would manifest as link failures in the Makefile objects.

## Test Signals
Run Kconfig builds for `ARCH_MESON`, ARM64 `COMPILE_TEST`, and module combinations. Verify hidden PMX backends are selected for older drivers and that `CONFIG_PINCTRL_AMLOGIC_A4=y` builds `pinctrl-amlogic-a4.o`.
