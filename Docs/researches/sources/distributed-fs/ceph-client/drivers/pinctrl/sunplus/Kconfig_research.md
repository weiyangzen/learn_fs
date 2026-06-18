# sources/distributed-fs/ceph-client/drivers/pinctrl/sunplus/Kconfig

## Purpose
This Kconfig file exposes the Sunplus SP7021 pinmux/GPIO controller driver as `CONFIG_PINCTRL_SPPCTL`. It controls whether the SP7021 pinctrl implementation in this directory is built and declares the framework dependencies required by the driver.

## Important APIs, Types, And Symbols
- `config PINCTRL_SPPCTL`: tristate option labeled "Sunplus SP7021 PinMux and GPIO driver".
- `depends on SOC_SP7021`: restricts visibility/building to SP7021 SoC configurations.
- `depends on OF && HAS_IOMEM`: requires devicetree and MMIO access, both mandatory for `sppctl.c`.
- `select GENERIC_PINCTRL_GROUPS`, `GENERIC_PINMUX_FUNCTIONS`, `GENERIC_PINCONF`, `PINCONF`, `PINMUX`, and `GPIOLIB`: ensures pinctrl, pinmux, pinconf, and GPIO subsystems are present.
- Help text states the driver provides both pin control and GPIO and that the module name is `sppinctrl`.

## Control Flow
Kconfig resolution runs before build. If selected as built-in or module, the Makefile compiles `sppinctrl` from `sppctl.o` and `sppctl_sp7021.o`. If dependencies are unmet, the option is unavailable and no runtime driver registration occurs.

## State And Persistence
The file has no runtime state. It persists build-time policy in the kernel configuration. The selected tristate value controls whether the driver is absent, built into the kernel, or built as a module according to the Kconfig model, although the C file uses `builtin_platform_driver`, so modular expectations deserve review with the current tree.

## Dependencies And Integration Points
- Integrates with the top-level pinctrl Kconfig through inclusion by the parent driver menu.
- Directly coordinates with `drivers/pinctrl/sunplus/Makefile`.
- The selected generic pinctrl symbols are prerequisites for the operations structures used in `sppctl.c`.
- Devicetree binding `sunplus,sp7021-pctl` is meaningful only when this option is enabled.

## Risks
- The help text says `M` builds module `sppinctrl`, but `sppctl.c` uses `builtin_platform_driver`; if the broader kernel tree still permits `m`, module build semantics should be verified.
- `select` can force dependencies without exposing their own prompts; changes in generic pinctrl APIs may require revisiting selected symbols.
- Overly narrow `SOC_SP7021` dependency can prevent compile coverage on non-SP7021 test configs unless explicitly enabled by build infrastructure.

## Test Signals
- `make menuconfig`/`olddefconfig` should expose `PINCTRL_SPPCTL` only when dependencies are satisfied.
- Built-in and module build tests should confirm that the declared tristate behavior matches the C registration macro.
- Runtime boot on SP7021 with `sunplus,sp7021-pctl` should probe only when the option is enabled.
