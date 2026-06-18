
# sources/distributed-fs/ceph-client/drivers/power/supply/power_supply_core.c

## Purpose
`power_supply_core.c` implements the universal Linux power_supply class. It handles class registration, power_supply device registration/unregistration, property get/set dispatch, supplier relationships, battery-info parsing, notifications, extension registration, hwmon/sysfs/LED/thermal integration, and helper lookup/interpolation routines.

## Important APIs, Types, and Functions
Major exported APIs include `power_supply_register()`, `devm_power_supply_register()`, `power_supply_unregister()`, `power_supply_changed()`, `power_supply_get_property()`, `power_supply_set_property()`, direct get/set variants, supplier lookup helpers, `power_supply_get_battery_info()`, `power_supply_put_battery_info()`, OCV/resistance interpolation helpers, extension register/unregister, notifier register/unregister, and `power_supply_get_drvdata()`. Internal state is class-level `power_supply_class`, `power_supply_notifier`, and `power_supply_dev_type`.

## Control Flow
Class init initializes sysfs attributes and registers the `power_supply` class. Registration allocates `struct power_supply`, binds device metadata and config, checks supplies, optionally parses battery info for battery devices, initializes locks/work, adds the device, initializes wakeup/thermal/LED/hwmon integration, increments use count, marks initialized, and queues a delayed change event after parent probe has settled. `power_supply_changed()` marks a changed flag under spinlock, holds a wake reference, and schedules work. The worker updates sysfs groups if needed, propagates external-power changes to supplied devices, updates LEDs, calls notifiers, and emits uevents.

## State and Persistence
Persistent kernel state is per-device: descriptor pointer, driver data, supplier arrays, extension list, battery info, changed flags, wakeup source, thermal zone, hwmon resources, and LED triggers. Battery info is parsed from firmware nodes or static Samsung tables and managed with devm allocations. No disk persistence exists.

## Dependencies and Integration Points
The core integrates with the device model class API, fwnode/OF references, notifiers, PM wakeup, sysfs, thermal, hwmon, LED triggers, and optional Samsung SDI battery tables. Drivers in this subset call `devm_power_supply_register()`, `power_supply_changed()`, `power_supply_get_battery_info()`, `power_supply_am_i_supplied()`, and property dispatch helpers.

## Risks and Test Signals
Risk areas include lifecycle races around `use_cnt`, deferred registration, extension semaphore ordering, supplier probe deferral, dynamic sysfs/hwmon refresh, battery-info parsing error cleanup, and OCV/resistance interpolation assumptions about sorted tables. Tests should cover registration failure unwinds, sysfs/hwmon/LED optional configs, extension conflicts, supplier phandle deferral, absent monitored-battery nodes, uevent behavior during removal, and KUnit-style interpolation/property helper cases.
