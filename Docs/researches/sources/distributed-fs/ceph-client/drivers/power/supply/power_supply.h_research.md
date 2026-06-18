
# sources/distributed-fs/ceph-client/drivers/power/supply/power_supply.h

## Purpose
This private header declares internal interfaces shared by the power_supply core, sysfs, LED trigger, and hwmon implementation files. It centralizes optional feature stubs so core code can call sysfs/LED/hwmon helpers regardless of configuration.

## Important APIs, Types, and Functions
It forward-declares `struct power_supply`, exposes internal `power_supply_property_is_writeable()`, `power_supply_has_property()`, and `power_supply_ext_has_property()`, defines `struct power_supply_ext_registration`, and provides `power_supply_for_each_extension()` with a lockdep assertion on `extensions_sem`. It conditionally declares or stubs `power_supply_init_attrs()`, `power_supply_uevent()`, `power_supply_attr_groups`, sysfs extension links, LED trigger helpers, and hwmon helpers.

## Control Flow
There is no runtime control flow beyond inline stubs. Compile-time configuration selects real helper declarations for `CONFIG_SYSFS`, `CONFIG_LEDS_TRIGGERS`, and `CONFIG_POWER_SUPPLY_HWMON`, or no-op fallbacks that let `power_supply_core.c` build without feature-specific code.

## State and Persistence
The only state shape introduced here is `power_supply_ext_registration`, which links extension metadata, owning device, and extension data into a power_supply list. The header stores no state itself and has no persistence behavior.

## Dependencies and Integration Points
It depends on `linux/lockdep.h` and public power_supply types. The extension macro assumes callers hold `psy->extensions_sem`; misuse can trigger lockdep. This header is the internal contract among `power_supply_core.c`, `power_supply_sysfs.c`, `power_supply_leds.c`, and `power_supply_hwmon.c`.

## Risks and Test Signals
Risks include list iteration without the extension semaphore, stubs masking missing feature behavior, and declaration drift with the public power_supply API. Build coverage should include combinations of sysfs, LED triggers, and hwmon enabled/disabled; runtime lockdep should cover extension registration and property paths.
