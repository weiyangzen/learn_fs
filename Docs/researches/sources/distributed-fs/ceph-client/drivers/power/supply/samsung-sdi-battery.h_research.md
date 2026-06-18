# sources/distributed-fs/ceph-client/drivers/power/supply/samsung-sdi-battery.h

## Purpose
Small public interface for the Samsung SDI battery profile provider. It lets consumers call `samsung_sdi_battery_get_info()` when `CONFIG_BATTERY_SAMSUNG_SDI` is enabled and receive a harmless `-ENODEV` stub otherwise.

## Important APIs, Types, and Functions
Declares or defines `samsung_sdi_battery_get_info(struct device *dev, const char *compatible, struct power_supply_battery_info **info)`.

## Control Flow
The preprocessor selects the external declaration when the provider is built in or as a module, otherwise compiles an inline stub returning `-ENODEV`.

## State and Persistence
No state. It only controls build-time linkage behavior.

## Dependencies and Integration Points
Requires `struct device` and `struct power_supply_battery_info` declarations from including contexts. It integrates consumers with the optional `CONFIG_BATTERY_SAMSUNG_SDI` provider.

## Risks and Test Signals
The header has no include guard beyond conditional compilation and assumes required type declarations are already available. Test all build combinations: provider enabled, module, and disabled consumer builds.
