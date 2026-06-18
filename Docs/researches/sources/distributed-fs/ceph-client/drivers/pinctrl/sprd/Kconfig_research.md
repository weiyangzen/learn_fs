<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sprd/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sprd/Kconfig

## Purpose
This Kconfig file defines the build switches for Spreadtrum pinctrl support. It provides a common hidden/base `PINCTRL_SPRD` symbol and a user-visible SC9860 SoC driver option.

## Important Symbols
- `PINCTRL_SPRD` is a tristate base symbol. It selects `PINMUX`, `PINCONF`, `GENERIC_PINCONF`, and `GENERIC_PINMUX_FUNCTIONS`.
- `PINCTRL_SPRD_SC9860` is the visible `Spreadtrum SC9860 pinctrl driver` option. It depends on `OF` and `ARCH_SPRD || COMPILE_TEST`, and selects `PINCTRL_SPRD`.

## Control Flow And Integration
Kconfig has build-time control flow only. Enabling SC9860 pulls in the common Spreadtrum pinctrl core and the SC9860 data driver through the sibling Makefile. The selected generic pinctrl helpers define which pinmux/pinconf APIs are available to the compiled driver.

## State And Persistence
The persistent state is the generated kernel `.config`. No runtime state is created by this file directly.

## Dependencies
It depends on the kernel pinctrl framework, OF support for SC9860, architecture symbol `ARCH_SPRD`, and `COMPILE_TEST` for non-native build coverage.

## Risks And Review Notes
- `PINCTRL_SPRD` is not user-prompted; SoC symbols must select it or the common object will not build.
- Missing generic helper selections would break core driver compilation or runtime feature availability.
- New Spreadtrum SoCs need coordinated Kconfig and Makefile entries.

## Test Signals
Run `make olddefconfig` with `ARCH_SPRD` and with `COMPILE_TEST` to ensure `PINCTRL_SPRD_SC9860` is visible and selects `PINCTRL_SPRD`. Build `drivers/pinctrl/sprd/` and inspect `.config` for `PINMUX`, `PINCONF`, and generic helper selections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sprd/Kconfig -->
