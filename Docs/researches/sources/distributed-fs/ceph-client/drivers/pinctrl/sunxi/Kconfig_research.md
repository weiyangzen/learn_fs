# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/Kconfig

## Purpose

This Kconfig fragment defines build-time configuration for Allwinner/sunxi pinctrl drivers. It gates the common sunxi pinctrl core under `ARCH_SUNXI` and provides per-SoC symbols for main PIO and R-PIO controllers from older ARM SoCs through newer ARM64 and RISC-V families.

## Important APIs, Types, And Functions

The central internal symbol is `PINCTRL_SUNXI`, a hidden bool selecting `PINMUX`, `GENERIC_PINCONF`, and `GPIOLIB`. Public SoC symbols include `PINCTRL_SUNIV_F1C100S`, `PINCTRL_SUN4I_A10`, `PINCTRL_SUN5I`, `PINCTRL_SUN6I_A31`, `PINCTRL_SUN6I_A31_R`, `PINCTRL_SUN8I_*`, `PINCTRL_SUN9I_*`, `PINCTRL_SUN20I_D1`, `PINCTRL_SUN50I_*`, and `PINCTRL_SUN55I_A523*`.

## Control Flow

There is no runtime flow. During kernel configuration, enabled architecture or machine symbols set defaults for matching pinctrl drivers. Selecting any SoC-specific symbol selects `PINCTRL_SUNXI`, which makes the common pinctrl, pinmux, generic pinconf, and GPIO dependencies available. The Makefile then uses the selected symbols to include the matching object files.

## State And Persistence

The only state is Kconfig configuration state saved in `.config` or generated defconfigs. That state controls compilation and built-in/module availability but does not persist runtime pin state.

## Dependencies And Integration Points

This file integrates with the architecture selection layer through `ARCH_SUNXI`, `MACH_SUNIV`, `MACH_SUN4I`, `MACH_SUN5I`, `MACH_SUN6I`, `MACH_SUN8I`, `MACH_SUN9I`, `ARM64`, and `RISCV`. It integrates with `drivers/pinctrl/sunxi/Makefile` through one-to-one `CONFIG_PINCTRL_*` object mappings.

## Risks

Incorrect defaults can omit required pinctrl support from platform defconfigs, leading to early boot failures when GPIO, UART, MMC, or regulator pins cannot be configured. Symbols are mostly bools, while A100 files use module registration macros; changing bool/tristate semantics must be coordinated with Makefile and init macro choices. A missing `select PINCTRL_SUNXI` on a new symbol would compile an SoC file without the common core.

## Test Signals

Useful validation includes `olddefconfig` for each supported architecture family, checking that expected `CONFIG_PINCTRL_*` symbols appear in generated configs, compile tests for all entries, and boot smoke tests confirming that device-tree-compatible pinctrl nodes bind on selected SoCs.
