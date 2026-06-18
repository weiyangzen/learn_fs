
# sources/distributed-fs/ceph-client/drivers/power/supply/power_supply_hwmon.c

## Purpose
This file bridges power_supply properties into the hwmon subsystem. It creates a hwmon device for supplies that expose voltage, current, power, or temperature properties and performs unit conversion between power_supply and hwmon conventions.

## Important APIs, Types, and Functions
`struct power_supply_hwmon` stores the backing power_supply and a bitmap of supported power_supply properties. Mapping helpers convert hwmon attrs to power_supply properties for voltage, current, power, and two temperature channels. Main callbacks are `power_supply_hwmon_is_visible()`, `power_supply_hwmon_read()`, `power_supply_hwmon_write()`, `power_supply_hwmon_read_string()`, `power_supply_add_hwmon_sysfs()`, and `power_supply_remove_hwmon_sysfs()`.

## Control Flow
When the core adds hwmon, this file opens a devres group, allocates state and a bitmap, populates supported properties via `power_supply_has_property()`, sanitizes the hwmon name by replacing dashes with underscores, and calls `devm_hwmon_device_register_with_info()`. Visibility maps hwmon attributes to power_supply properties and marks attributes writable only when both the power_supply property is writable and hwmon allows writes. Reads call `power_supply_get_property()` then convert uV/uA to mV/mA and tenths-C to milli-C. Writes reverse those conversions and call `power_supply_set_property()`.

## State and Persistence
State is devm-managed under a devres group keyed by `power_supply_add_hwmon_sysfs()`, allowing removal/recreation when extensions change property availability. No persistent state is stored.

## Dependencies and Integration Points
It depends on `linux/hwmon.h`, power_supply property helpers, bitmap allocation, overflow helpers, and the private header. The core invokes add/remove during registration and extension updates.

## Risks and Test Signals
Risks include property enum bitmap sizing, unit conversion overflow, mismatch between visible/writeable attributes and driver capabilities, and missing labels when no temp input exists. Tests should verify hwmon files for supplies with each property class, write conversions for voltage/current/temp limits, name sanitization, extension-triggered rebuild, and overflow error paths.
