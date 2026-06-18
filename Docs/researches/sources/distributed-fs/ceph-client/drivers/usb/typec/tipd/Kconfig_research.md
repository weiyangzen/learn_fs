# sources/distributed-fs/ceph-client/drivers/usb/typec/tipd/Kconfig

## Purpose

This Kconfig fragment declares the build-time option for the TI TPS6598x USB Power Delivery controller driver under the Type-C TIPD directory. It lets kernel configuration select the TPS65982/TPS65983 controller support either built-in or as a module.

## Important APIs, Types, and Functions

The single symbol is `TYPEC_TPS6598X`, a `tristate` option with prompt `TI TPS6598x USB Power Delivery controller driver`. It depends on `I2C`, selects `POWER_SUPPLY`, `REGMAP_I2C`, and `USB_ROLE_SWITCH`, and documents that the module name is `tps6598x.ko`.

## Control Flow

There is no runtime control flow in this file. During Kconfig resolution, `TYPEC_TPS6598X=y` builds the driver into the kernel, `TYPEC_TPS6598X=m` builds it as a module, and disabled leaves the TIPD driver objects out. The `depends on I2C` gate prevents enabling the driver without I2C support. The selected symbols ensure the driver's power-supply, regmap-over-I2C, and USB role-switch dependencies are available when the option is enabled.

## State and Persistence Behavior

The only persistent state is the kernel configuration value stored in the build configuration. It affects which objects the Makefile compiles, but it does not manage runtime state.

## Dependencies and Integration Points

This option integrates with `drivers/usb/typec/tipd/Makefile`, where `obj-$(CONFIG_TYPEC_TPS6598X)` includes `tps6598x.o`. It also integrates with the broader kernel Kconfig dependency graph by requiring I2C and selecting `POWER_SUPPLY`, `REGMAP_I2C`, and `USB_ROLE_SWITCH`.

## Risks

Because `select` bypasses dependency prompts for selected symbols, this Kconfig entry assumes the selected subsystems are safe to force on whenever I2C is available. If the TPS6598x driver later depends on additional optional features, this file must be kept in sync. The help text names only TPS65982/TPS65983, so newer compatible chips may require updated wording if supported by the code.

## Test Signals

Configuration tests should verify that `CONFIG_TYPEC_TPS6598X=y` and `=m` select the required symbols and that `=m` produces `tps6598x.ko`. Negative tests should verify the option is unavailable or not buildable when `I2C` is disabled.
