# sources/distributed-fs/ceph-client/drivers/power/supply/max14577_charger.c

## Purpose
This platform driver controls the charger block in Maxim MAX14577 and MAX77836 MFD devices. It initializes safe charger defaults from device-tree data, reports charger/battery status through the power-supply core, and exposes a sysfs knob for the fast-charge timer.

## Important APIs, Types, and Functions
`struct max14577_charger` stores device, parent MFD, registered supply, and charger platform data. `maxim_get_charger_type()` normalizes MUIC charger-type register values across MAX14577 and MAX77836. `max14577_get_charger_state()`, `max14577_get_charge_type()`, `max14577_get_online()`, and `max14577_get_battery_health()` read MFD registers to report status, charge type, online, and health. Initialization helpers program fast-charge timer, constant voltage, EOC current, fast-charge current, charger detect mode, battery charger enable, auto-stop, and OVP threshold. `fast_charge_timer` sysfs show/store maps between hours and register bits.

## Control Flow
Probe allocates state, gets parent MFD data, parses required DT properties (`maxim,constant-uvolt`, `fast-charge-uamp`, `eoc-uamp`, `ovp-uvolt`), initializes charger registers, creates the sysfs file, registers the power supply, and validates compile-time current constants. Remove deletes the sysfs file.

## State and Persistence
The driver persists charger policy in hardware registers at probe and when sysfs changes the fast-charge timer. It does not cache runtime telemetry. Battery presence is always reported as true because the chip lacks a battery-present bit.

## Dependencies and Integration Points
It depends on the parent MAX14577/MAX77836 MFD regmap and register definitions, OF charger node properties, helper tables from `max14577.h`, sysfs, and the power-supply core. The descriptor is named `max14577-charger` and has type `BATTERY` despite reporting charger-like properties.

## Risks
Probe requires all charger DT properties and fails otherwise. Several initialization writes before later validation can leave partial hardware state if a later step fails. Online classification treats downstream ports as offline but several special chargers as online. TODOs note incomplete full, dead-battery, and charger timer handling. Sysfs allows disabling or changing the fast-charge timer after probe.

## Test Signals
Validate DT parsing failures, MAX14577 versus MAX77836 current/EOC mappings, constant voltage gap handling, OVP values, charger type decoding including reserved/dead-battery values, status/health reads, sysfs timer show/store, cleanup on power-supply registration failure, and parent regmap error propagation.
