# sources/distributed-fs/ceph-client/drivers/pinctrl/Kconfig

## Purpose
Main pinctrl subsystem Kconfig. It defines core pinctrl capabilities, generic helper symbols, debug support, many top-level pinctrl drivers, and includes vendor subdirectory Kconfigs.

## APIs, Flow, And State
Core symbols include `PINCTRL`, `PINMUX`, `PINCONF`, `GENERIC_PINCONF`, `GENERIC_PINCTRL_GROUPS`, `GENERIC_PINMUX_FUNCTIONS`, `GENERIC_PINCTRL`, and `DEBUG_PINCTRL`. Driver symbols select related infrastructure such as `GPIOLIB`, IRQ chips, regmap, MFD, firmware, OF, or ACPI. When `PINCTRL` is enabled, this file exposes options and sources vendor Kconfigs including `actions`, `qcom`, `ti`, `renesas`, `tegra`, and others. State is build-time `.config` only.

## Dependencies And Integration
Integrates pinctrl with GPIO, IRQ, device tree, firmware, architecture symbols, and `drivers/pinctrl/Makefile`.

## Risks And Tests
Dependency/select mistakes can create missing symbols or overly broad builds. Source ordering mistakes can hide vendor menus. Test `olddefconfig`, `allmodconfig`, `allyesconfig`, targeted symbols, architecture visibility, compile-test visibility, and Makefile symbol consistency.
