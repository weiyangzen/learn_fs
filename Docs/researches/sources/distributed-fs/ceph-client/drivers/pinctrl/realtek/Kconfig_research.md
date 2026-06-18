# sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/Kconfig

## Purpose
This Kconfig file defines build-time configuration symbols for the Realtek DHC pin controller family. It provides a core driver option and SoC-specific options for RTD1619B, RTD1319D, RTD1315E, and RTD1625.

## Important APIs, Types, and Functions
This file has no C APIs. Its important symbols are:
- `PINCTRL_RTD`: tristate core Realtek DHC pin controller driver, depending on `ARCH_REALTEK`, defaulting to `y`, and selecting `PINMUX`, `GENERIC_PINCONF`, and `REGMAP_MMIO`.
- `PINCTRL_RTD1619B`: SoC-specific RTD1619B driver depending on `PINCTRL_RTD`, default `y`.
- `PINCTRL_RTD1319D`: SoC-specific RTD1319D driver depending on `PINCTRL_RTD`, default `y`.
- `PINCTRL_RTD1315E`: SoC-specific RTD1315E driver depending on `PINCTRL_RTD`, default `y`.
- `PINCTRL_RTD1625`: SoC-specific RTD1625 driver depending on `PINCTRL_RTD`, default `y`, with help text describing muxing/GPIO enabling and generic pinconf electrical properties.

## Control Flow
Kconfig evaluation makes the core symbol available only on Realtek architectures. Selecting `PINCTRL_RTD` ensures the common pinmux, pinconf, and regmap-mmio infrastructure is built. Enabling each SoC-specific symbol causes Makefile entries in the same directory to compile the matching data driver, while those drivers call the exported core `rtd_pinctrl_probe()`.

## State and Persistence
The file defines build configuration only. It persists as kernel `.config` selections and has no runtime state.

## Dependencies and Integration Points
The file integrates with the kernel build system and the Realtek pinctrl Makefile. It ties the Realtek pinctrl family to architecture gating and required subsystems. The SoC symbols correspond to `pinctrl-rtd1619b.o`, `pinctrl-rtd1319d.o`, `pinctrl-rtd1315e.o`, and `pinctrl-rtd1625.o`.

## Risks and Edge Cases
- All symbols default to `y`, which can increase default build surface for `ARCH_REALTEK`.
- SoC-specific symbols depend only on `PINCTRL_RTD`; they do not independently gate on finer SoC/DT options.
- The RTD1625 help text lacks a final period/newline polish in this snapshot, but that is cosmetic.

## Test Signals
Build-system validation should check `all{yes,mod,no}config` behavior for `ARCH_REALTEK`, dependency selection of `PINMUX`, `GENERIC_PINCONF`, and `REGMAP_MMIO`, and that each symbol produces the expected object listed in the Makefile. Kconfig linting can catch formatting issues.
