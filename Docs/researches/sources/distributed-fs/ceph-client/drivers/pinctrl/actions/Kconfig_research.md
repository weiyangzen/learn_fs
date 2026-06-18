# sources/distributed-fs/ceph-client/drivers/pinctrl/actions/Kconfig

## Purpose
Defines Actions Semi OWL pinctrl support and SoC-specific S500, S700, and S900 options.

## APIs, Flow, And State
`PINCTRL_OWL` is the common boolean option. It depends on `(ARCH_ACTIONS || COMPILE_TEST) && OF` and selects `PINMUX`, `PINCONF`, `GENERIC_PINCONF`, `GPIOLIB`, and `GPIOLIB_IRQCHIP`. `PINCTRL_S500`, `PINCTRL_S700`, and `PINCTRL_S900` depend on `PINCTRL_OWL` plus ARM/ARM64 or compile-test constraints. These symbols drive `drivers/pinctrl/actions/Makefile`; state is build-time `.config` only.

## Dependencies And Integration
Integrates with pinctrl, pinmux, pinconf, GPIO, IRQ-capable GPIO, OF probing, and the parent pinctrl Kconfig.

## Risks And Tests
All options are bool, so they are built-in only. No defaults means platform configs must select the relevant SoC. Test OWL alone, each variant, compile-test visibility, and that variants disappear when `PINCTRL_OWL` is disabled.
