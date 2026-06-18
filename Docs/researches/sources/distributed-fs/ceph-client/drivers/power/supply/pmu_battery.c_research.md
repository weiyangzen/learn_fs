
# sources/distributed-fs/ceph-client/drivers/power/supply/pmu_battery.c

## Purpose
This legacy Apple PMU battery driver exposes PMU AC status and one power_supply battery per PMU battery slot. It adapts global PMU battery structures into standard power_supply properties.

## Important APIs, Types, and Functions
`struct pmu_battery_dev` embeds a dynamic descriptor, pointer to `struct pmu_battery_info`, name buffer, and registered power supply. Main functions are `pmu_bat_init()`, `pmu_bat_exit()`, `pmu_get_ac_prop()`, `pmu_bat_get_model_name()`, and `pmu_bat_get_property()`.

## Control Flow
Module init creates a synthetic platform device, registers `pmu-ac`, then loops over `pmu_battery_count` to allocate per-battery descriptors named `PMU_battery_N` and register each battery power supply. Property reads directly inspect global `pmu_power_flags` and per-slot `pmu_batteries[]`. Exit unregisters all registered batteries, frees wrappers, unregisters AC, and removes the platform device.

## State and Persistence
The driver keeps per-registration wrapper objects in the `pbats` array. Battery values are live global PMU state maintained outside this file. No persistent storage or hardware programming is performed here.

## Dependencies and Integration Points
It depends on classic PowerMac PMU/ADB globals and constants from `linux/pmu.h`, platform device helpers, and the power_supply core. It uses non-devm registration because it is module-init based.

## Risks and Test Signals
Risk areas include partial registration cleanup when allocation stops early, assuming global PMU arrays are valid for module lifetime, and reporting AC online when no batteries exist. Tests should cover zero-battery systems, multiple battery registration, unit conversions mWh-to-uWh/mA-to-uA/mV-to-uV, model-name decoding, and cleanup after mid-loop registration failure.
