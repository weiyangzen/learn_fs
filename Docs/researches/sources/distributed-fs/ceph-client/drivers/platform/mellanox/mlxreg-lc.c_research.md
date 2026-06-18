# sources/distributed-fs/ceph-client/drivers/platform/mellanox/mlxreg-lc.c

## Purpose
Nvidia line-card platform driver for SN4800 C16 class hardware. It creates the line-card I2C hierarchy, registers mux, LED, and `mlxreg-io` children, attaches auxiliary and main-power devices, and reacts to hotplug notifications for synchronization, power, ready, and thermal events.

## Important APIs, Types, And Functions
`struct mlxreg_lc` stores parent regmap, child devices, mux/platform data, static device tables, and state bits. Register access is controlled by `mlxreg_lc_regmap_conf`. Static tables describe mux channels, EEPROM and power-monitor devices, LEDs, and IO attributes. Lifecycle helpers include `mlxreg_lc_power_on_off()`, `mlxreg_lc_enable_disable()`, `mlxreg_lc_event_handler()`, `mlxreg_lc_completion_notify()`, `mlxreg_lc_config_init()`, probe, and remove.

## Control Flow
Probe installs a notifier callback into hotplug platform data, creates the line-card I2C client, initializes regmap/defaults, obtains parent regmap from the parent hotplug data, validates the line-card type, registers the CPLD mux, then registers `mlxreg-io` and LED children. The mux completion callback maps logical static devices to created adapters, creates auxiliary devices immediately, conditionally creates main-power devices, checks sync state, powers the card if needed, and marks initialized.

## State, Dependencies, Integration, Risks, Tests
State is tracked in `MLXREG_LC_INITIALIZED`, `POWERED`, and `SYNCED` bits under a mutex, plus child device/client handles and adapter references. Dependencies include parent hotplug data, I2C, `i2c-mux-mlxcpld`, regmap, `mlxreg-io`, `leds-mlxreg`, and `mlxreg-hotplug` notifier callbacks. Risks include type-read duplication at `CONFIG_OFFSET`, event callbacks arriving before initialization, adapter index assumptions from mux channels, partial cleanup after mux completion failures, power/enable register bit mapping by slot, and notifier handle clearing on failed probe. Test signals include line-card insertion/removal, mux completion, auxiliary and main device creation, sync/power/ready/thermal event handling, child platform registration failures, and remove after failed probe.
