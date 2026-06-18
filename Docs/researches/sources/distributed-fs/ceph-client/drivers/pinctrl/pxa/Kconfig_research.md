# sources/distributed-fs/ceph-client/drivers/pinctrl/pxa/Kconfig

## Purpose
Defines Kconfig symbols for Marvell PXA2xx pinctrl support and chip-specific PXA25x/PXA27x drivers.

## Important APIs, Types, And Functions
Symbols are `PINCTRL_PXA`, `PINCTRL_PXA25X`, and `PINCTRL_PXA27X`. The common symbol selects `PINMUX`, `PINCONF`, and `GENERIC_PINCONF`; chip symbols select the common symbol and default to `y` on matching platform symbols.

## Control Flow
The menu is visible only when `ARCH_PXA` or `COMPILE_TEST` is set. Selecting a chip driver pulls in common PXA pinctrl support and controls Makefile object inclusion.

## State And Persistence
State is build-time configuration persisted in `.config`; no runtime state is created by this file.

## Dependencies And Integration Points
Works with `drivers/pinctrl/pxa/Makefile` and the PXA platform Kconfig symbols `PXA25x` and `PXA27x`.

## Risks
Because `PINCTRL_PXA` is hidden and selected, common driver coverage depends on at least one chip symbol. Missing dependencies on OF or platform resources would surface at build/probe time rather than menu visibility.

## Test Signals
`olddefconfig` on PXA platforms, `COMPILE_TEST` builds, and verifying object inclusion for both chip symbols are the key signals.
