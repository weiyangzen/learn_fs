# sources/distributed-fs/ceph-client/drivers/acpi/battery.c

## Purpose
Implements the generic ACPI battery platform driver for PNP0C0A-compatible batteries and selected Microsoft Surface battery IDs. It translates ACPI control methods into the Linux `power_supply` class, reports battery presence, charge/energy/current/voltage/status properties, handles battery alarms, emits ACPI/netlink/power_supply notifications, and exposes a small hook API for platform-specific battery extensions.

## Important APIs, Types, And Functions
`struct acpi_battery` is the persistent per-battery state: ACPI device pointer, `power_supply_desc`, registered `power_supply`, update mutex, PM notifier, cached AML values, string fields, alarm, unit, and quirk flags. The ACPI ID table matches `PNP0C0A` and `MSHW0146`.

The main AML readers are `acpi_battery_get_status()` for `_STA`, `acpi_battery_get_info()` for `_BIX` or fallback `_BIF`, `acpi_battery_get_state()` for `_BST`, and `acpi_battery_set_alarm()` for `_BTP`. `extract_package()` maps integer/string package entries into `struct acpi_battery` using offset tables for `_BST`, `_BIF`, and `_BIX`.

`acpi_battery_get_property()` is the `power_supply` property callback. It exposes status, presence, technology, cycle count, voltage, current or power, full/design/current charge or energy, capacity percent, capacity level, model, manufacturer, and serial number. Separate property arrays are chosen for charge-mode versus energy-mode batteries and for broken full-capacity reporting.

Probe/remove entry points are `acpi_battery_probe()` and `acpi_battery_remove()` through the `acpi-battery` platform driver. Notifications are handled by `acpi_battery_notify()` installed via `acpi_dev_install_notify_handler()`. Sleep transitions use `acpi_battery_resume()` and a PM notifier `battery_notify()`.

The exported hook API is `battery_hook_register()`, `battery_hook_unregister()`, and `devm_battery_hook_register()`, backed by `acpi_battery_list`, `battery_hook_list`, and `hook_mutex`.

## Control Flow
Module init exits if ACPI is disabled or an AC/battery skip quirk applies, runs DMI quirks, then registers the platform driver. Probe obtains the ACPI companion, defers while dependencies are unmet, allocates state, detects `_BIX`, retries `acpi_battery_update()` up to five times, registers a PM notifier, enables wakeup, and installs the ACPI notify handler.

`acpi_battery_update()` first refreshes `_STA`. If the battery is absent, it unregisters the `power_supply` and clears the update cache. On first present update it reads `_BIX/_BIF`, initializes `_BTP`, reads `_BST`, applies firmware quirks, registers the `power_supply` if needed, and emits a PM wakeup event for critical or below-alarm capacity. Runtime property reads call `_BST` only when the battery is present and the `cache_time` jiffies window has expired.

ACPI notifications lock `update_lock`, optionally delay for broken firmware, refresh static info on info-change events, update runtime state, generate ACPI netlink and notifier-chain events, and call `power_supply_changed()` if the old and new `power_supply` objects are still present. Resume clears `update_time` and runs an update in resume mode so suspended-state changes are noticed without unnecessarily rebuilding sysfs.

## State And Persistence
State is in memory only. `update_time` caches `_BST` results for `cache_time` milliseconds. DMI callbacks set global quirk booleans for broken `_BIX`, notification delay, and AC-supply reporting. Per-battery quirk bits normalize percentage capacity, old ThinkPad mAh reporting, and degraded full-charge capacity. The `alarm` sysfs attribute stores the last requested threshold in `struct acpi_battery` and writes `_BTP` when the battery is present. Registered power supplies and hook-provided attributes persist until hot-remove, driver remove, or module exit.

## Dependencies And Integration Points
The driver depends on ACPICA evaluation helpers, ACPI platform-device enumeration, DMI, PM notifier/wakeup APIs, `power_supply`, sysfs attribute groups, and the ACPI bus notification wrappers in `bus.c`. It integrates with userspace through `/sys/class/power_supply/<BID>/` and an `alarm` attribute, with other kernel drivers through the exported battery hook API, and with suspend/resume through PM notifiers and wake events.

## Risks
Firmware package shape is a major risk: `_BIX/_BIF/_BST` type or length mismatches return errors or produce missing properties. Unit conversion quirks are model-specific and can regress capacity reporting if applied too broadly. `extract_package()` accepts integer values as short strings for string fields, which preserves legacy behavior but makes malformed firmware observable in user-visible strings. Notification timing is firmware-sensitive, hence the DMI delay quirk. The hook API must be used carefully because failed hook addition unregisters the hook from all batteries.

## Test Signals
Useful signals include successful probe logs, non-empty `power_supply` properties, correct `_BIX` fallback to `_BIF`, hotplug removal/readdition behavior, `power_supply_changed()` on ACPI battery events, low/critical wakeup events, suspend/resume state refresh, and DMI quirk coverage on affected hardware. Fault injection or AML emulation should cover malformed packages, absent batteries, broken full-capacity values, and `_BTP` failures.
