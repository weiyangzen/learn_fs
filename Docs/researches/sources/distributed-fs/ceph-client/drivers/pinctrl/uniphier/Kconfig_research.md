# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/Kconfig

## Purpose

This Kconfig fragment defines the UniPhier pinctrl driver family. It exposes a menu-level `PINCTRL_UNIPHIER` switch and individual boolean options for supported UniPhier SoCs, allowing architecture defaults to select the appropriate SoC-specific pinctrl table drivers.

## Important APIs, Types, and Functions

The menu symbol is `PINCTRL_UNIPHIER`, a bool depending on `ARCH_UNIPHIER || COMPILE_TEST` and `OF && MFD_SYSCON`, defaulting to `ARCH_UNIPHIER`. It selects `PINMUX` and `GENERIC_PINCONF`. Child symbols are `PINCTRL_UNIPHIER_LD4`, `PRO4`, `SLD8`, `PRO5`, `PXS2`, `LD6B`, `LD11`, `LD20`, `PXS3`, and `NX1`. ARM-generation SoCs default to `ARM`; later SoCs default to `ARM64`.

## Control Flow

Kconfig first determines whether the UniPhier menu is available. If enabled, child symbols can be selected and their defaults follow the target architecture. Kbuild then uses these symbols to include the common UniPhier core object and the selected SoC-specific objects from the Makefile.

## State and Persistence

The file persists only kernel configuration choices in `.config`. It does not own runtime state or hardware state.

## Dependencies and Integration Points

The dependency on OF and MFD_SYSCON reflects that UniPhier pinctrl drivers use Device Tree and syscon/regmap-backed SoC registers. `PINMUX` and `GENERIC_PINCONF` are selected for the shared core and SoC drivers. The child symbols integrate directly with `drivers/pinctrl/uniphier/Makefile`.

## Risks

Incorrect defaults can omit a needed SoC driver from common ARM/ARM64 UniPhier defconfigs. Missing `MFD_SYSCON` or generic pinconf dependencies would break builds or probing. Because all child symbols are bools under a bool menu, they are built-in when selected rather than separately modularized; that matches common pinctrl usage but affects footprint.

## Test Signals

Run configuration checks for UniPhier ARM and ARM64 defconfigs and compile-test builds. Verify menu visibility when `ARCH_UNIPHIER` is off but `COMPILE_TEST` is on. Build each child symbol and confirm the expected object file is selected by the Makefile together with `pinctrl-uniphier-core.o`.
