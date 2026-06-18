# sources/distributed-fs/ceph-client/drivers/pinctrl/visconti/Kconfig

## Purpose

This Kconfig file defines build-time configuration for Toshiba Visconti pinctrl support. It separates a common Visconti pinctrl core symbol from the TMPV7700 SoC-specific driver symbol.

## Important APIs, Types, And Data

- `PINCTRL_VISCONTI` is a hidden boolean selected by concrete Visconti SoC drivers. It selects `PINMUX`, `GENERIC_PINCONF`, `GENERIC_PINCTRL_GROUPS`, and `GENERIC_PINMUX_FUNCTIONS`.
- `PINCTRL_TMPV7700` is a user-visible boolean for the Toshiba Visconti TMPV7700 series pinctrl driver. It depends on `OF` and on either `ARCH_VISCONTI` or `COMPILE_TEST`, selects `PINCTRL_VISCONTI`, and defaults to `ARCH_VISCONTI`.

## Control Flow

Kconfig resolution occurs at kernel configuration time. Enabling `PINCTRL_TMPV7700` selects the common `PINCTRL_VISCONTI` support, which in turn ensures generic pinctrl, pinmux, and pinconf helpers are available. The Makefile then uses the resolved config symbols to build the common and TMPV7700 objects.

## State And Persistence

The file has no runtime state. Its persistent effect is the generated kernel `.config` and the object inclusion decisions derived from it.

## Dependencies And Integration Points

It integrates with the kernel pinctrl Kconfig hierarchy, architecture selection through `ARCH_VISCONTI`, Open Firmware support through `OF`, and compile coverage through `COMPILE_TEST`.

## Risks And Edge Cases

- Because `PINCTRL_VISCONTI` is hidden, no common object is built unless a concrete SoC driver selects it.
- Missing generic helper selections would cause compile or runtime registration failures in `pinctrl-common.c`; this Kconfig correctly selects the needed generic pinctrl and pinmux/pinconf infrastructure.
- `PINCTRL_TMPV7700` being `bool` means this driver is built in, not modular, when enabled.

## Test Signals

Configuration tests should verify that `ARCH_VISCONTI=y` enables `PINCTRL_TMPV7700` by default and that `COMPILE_TEST=y` on other architectures can build the driver when dependencies are met. Build logs should include both `pinctrl-common.o` and `pinctrl-tmpv7700.o` when TMPV7700 support is enabled.
