# sources/distributed-fs/ceph-client/drivers/power/supply/lenovo_yoga_c630_battery.c

## Purpose
This auxiliary-bus driver exposes battery and USB-C adapter data from the Lenovo Yoga C630 embedded controller. It registers separate adapter and battery power supplies, caches expensive EC battery-status reads for ten seconds, and reacts to EC notifications for battery info, adapter, and status changes.

## Important APIs, Types, and Functions
`struct yoga_c630_psy` stores the EC handle, fwnode, notifier, mutex, supplies, cache timestamp, adapter state, capacity unit mode, static battery info, and dynamic telemetry. `yoga_c630_psy_update_bat_info()` reads presence, unit mode, design capacity/voltage, and full capacity, with 50 ms sleeps matching DSDT behavior. `yoga_c630_psy_maybe_update_bat_status()` refreshes status, remaining capacity, voltage, current, and power under cache control. `yoga_c630_psy_bat_get_property()` maps EC state to charge or energy properties depending on unit mode. `yoga_c630_ec_refresh_bat_info()` can unregister and re-register the battery supply if the EC changes units.

## Control Flow
Probe allocates state, registers the adapter supply first with `supplied_to` pointing at the battery name, reads battery info under the mutex, registers either the mA or mWh battery descriptor, then registers an EC notifier. Notifications call `power_supply_changed()` for relevant supplies and refresh battery info on `LENOVO_EC_EVENT_BAT_INFO`.

## State and Persistence
Static battery data and dynamic telemetry are cached in memory. `last_status_update` throttles EC reads. Unit mode controls which property list is registered; a unit change causes battery supply replacement. There is no persistent write path to the EC.

## Dependencies and Integration Points
It depends on the Yoga C630 EC platform data and read/notifier APIs, auxiliary bus matching through `YOGA_C630_MOD_NAME "." YOGA_C630_DEV_PSY`, mutex cleanup guards, the power-supply core, and fwnode inherited from the parent.

## Risks
`yoga_c630_psy_bat_get_property()` checks `bat_present` before refreshing status, so stale absence can hide a newly inserted battery until an info event. The error path calls `power_supply_unregister(ecbat->bat_psy)` even if registration did not happen, relying on the value being harmless. EC sleeps make property reads slow on cache misses. Power calculation multiplies current in mA by voltage in mV-like units and should be validated for expected power-supply units.

## Test Signals
Test adapter online/USB type, battery present and absent behavior, charge versus energy descriptor selection, cache expiry, EC notification handling, unit-mode re-registration, full/not-charging detection, signed current conversion, and failure paths for EC reads and notifier registration.
