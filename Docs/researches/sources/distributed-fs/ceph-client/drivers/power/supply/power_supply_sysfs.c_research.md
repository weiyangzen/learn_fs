
# sources/distributed-fs/ceph-client/drivers/power/supply/power_supply_sysfs.c

## Purpose
This file implements sysfs and uevent formatting for the power_supply class. It maps enum properties to attribute names, text labels, writable modes, parsing, dynamic visibility, extension links, and `POWER_SUPPLY_*` uevent variables.

## Important APIs, Types, and Functions
`struct power_supply_attr` binds property names, lower-case sysfs attribute names, device attributes, and optional text tables. Important functions include `power_supply_init_attrs()`, `power_supply_format_property()`, `power_supply_show_property()`, `power_supply_store_property()`, `power_supply_attr_is_visible()`, `power_supply_uevent()`, enum helpers for charge behavior/types, and sysfs extension link add/remove helpers.

## Control Flow
Class init lowercases all property names and prepares the global attribute array. Attribute visibility checks whether the power_supply has the property through descriptor, battery info, or extensions, and adds owner-write mode when writeable. Reads call `power_supply_format_property()`, which fetches values, formats enums/text/string/int properties, and for USB type/charge modes shows available choices with the active value bracketed. Writes parse text labels or integers and call `power_supply_set_property()`. Uevent generation adds the supply name/type and then formats every property, tolerating absent-battery style errors.

## State and Persistence
The global attribute table is initialized once and marked `__ro_after_init`. Extension links are sysfs links under an `extensions` group. No persistent storage is used.

## Dependencies and Integration Points
It depends on the private power_supply header, string helpers, sysfs/device attributes, extension registration from the core, and the public enum value ordering in `linux/power_supply.h`. It provides `power_supply_attr_groups` and `power_supply_uevent` to `power_supply_core.c`.

## Risks and Test Signals
Risks include enum/text table drift, exposing driver-reported unavailable enum values, partial uevent omissions on transient errors, write parsing accepting raw integers for enums, and extension property conflicts. Tests should cover attribute visibility for descriptor/battery-info/extension properties, text formatting with spaces escaped, write parsing, uevents during removal, absent battery errors, and charge type/behavior available-value helpers.
