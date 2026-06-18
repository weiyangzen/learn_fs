# sources/distributed-fs/ceph-client/drivers/power/supply/lp8788-charger.c

## Purpose
This platform driver is the charger subdevice for the TI LP8788 MFD. It exposes charger input status and battery telemetry, applies optional platform-defined charger register settings, reads battery voltage/temperature through IIO channels, handles MFD IRQ resources, and provides charger diagnostic sysfs attributes.

## Important APIs, Types, and Functions
`struct lp8788_charger` stores the parent `struct lp8788`, charger and battery supplies, charger work, IIO channels, mapped IRQs, and platform data. Charger callbacks report online and input current. Battery callbacks decode `LP8788_CHG_STATUS` into status, health, presence, voltage, capacity, temperature, charge current, and termination voltage. `lp8788_update_charger_params()` writes validated charger-register parameters from platform data. `lp8788_irq_register()` maps named IRQ resources through the parent IRQ domain and installs a threaded handler. Sysfs attributes expose textual charger state, EOC time, and EOC level.

## Control Flow
Probe gets parent MFD data, stores charger platform data, applies charger params, sets up optional IIO channels named by platform data, registers the charger and battery supplies, and registers IRQs. IRQ threads notify both supplies for input/state/EOC/battery-low/no-battery events and optionally schedule `charger_work` to call a platform `charger_event()` callback when input state changes.

## State and Persistence
The driver caches IRQ mappings and IIO channel pointers, but most status is read live from LP8788 registers. Platform charger parameter writes persist in hardware registers. The work item has no periodic behavior; it is event driven.

## Dependencies and Integration Points
It depends on the LP8788 MFD register helpers, MFD IRQ domain and named resources, optional `lp8788_charger_platform_data`, IIO channels for VBATT and battery temperature, sysfs attribute groups, and the power-supply core.

## Risks
Some property helpers ignore `lp8788_read_byte()` return values, so failed reads can convert uninitialized data. Capacity is a simple VBATT/max-vbatt percentage unless maintenance state reports 100 percent, not a true fuel-gauge estimate. `lp8788_charger_event()` assumes platform data and callback are valid when scheduled. IRQ setup can partially map IRQs before failure and returns warning-only from probe, so systems may run without notifications.

## Test Signals
Test platform parameter validation/write ranges, charger online and current calculations, all charger-state mappings, no-battery/bad-battery health, IIO voltage/temp reads and missing-channel errors, capacity clamping, sysfs output strings, IRQ mapping/freeing, and platform charger-event callbacks.
