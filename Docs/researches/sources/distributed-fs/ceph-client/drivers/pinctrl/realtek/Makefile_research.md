# sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/Makefile

## Purpose
This Makefile maps Realtek DHC pinctrl Kconfig symbols to the object files compiled by kbuild. It builds the shared core and each supported SoC-specific data driver.

## Important APIs, Types, and Functions
This file has no runtime APIs. Its object mappings are:
- `CONFIG_PINCTRL_RTD` -> `pinctrl-rtd.o`
- `CONFIG_PINCTRL_RTD1619B` -> `pinctrl-rtd1619b.o`
- `CONFIG_PINCTRL_RTD1319D` -> `pinctrl-rtd1319d.o`
- `CONFIG_PINCTRL_RTD1315E` -> `pinctrl-rtd1315e.o`
- `CONFIG_PINCTRL_RTD1625` -> `pinctrl-rtd1625.o`

## Control Flow
During kbuild, each `obj-$(CONFIG_...)` line expands to either built-in, module, or nothing depending on Kconfig state. The core object provides `rtd_pinctrl_probe()` and `realtek_pinctrl_pm_ops`; SoC objects provide static descriptors and platform drivers that depend on the core symbol.

## State and Persistence
No runtime state exists. The persistent effect is the build artifact set selected by `.config`.

## Dependencies and Integration Points
The Makefile integrates directly with `drivers/pinctrl/realtek/Kconfig`. It assumes the SoC-specific source files exist beside `pinctrl-rtd.c` and use the shared header/core interfaces.

## Risks and Edge Cases
- If a SoC-specific symbol is enabled as built-in while the core is modular, kbuild dependency handling must keep link ordering coherent through the Kconfig dependency.
- Missing source files for any enabled symbol would produce build failures.
- There is no composite module aggregation; each object is controlled independently.

## Test Signals
Build `ARCH_REALTEK` configurations with each symbol as built-in and module where legal. Verify `modules.order`/built-in linkage contains the expected Realtek pinctrl objects and that SoC drivers resolve exported symbols from `pinctrl-rtd.o`.
