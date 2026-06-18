# sources/distributed-fs/ceph-client/drivers/power/supply/lego_ev3_battery.c

## Purpose
This platform driver reports LEGO MINDSTORMS EV3 battery measurements using two IIO channels and a battery-type GPIO. It supports automatic Li-ion pack detection via a rechargeable switch and lets userspace mark an otherwise unknown AA pack as NiMH once during initialization.

## Important APIs, Types, and Functions
`struct lego_ev3_battery` stores voltage/current IIO channels, the rechargeable GPIO, registered supply, technology, and design voltage bounds. `lego_ev3_battery_get_property()` reports technology, voltage, design voltage min/max, current, and system scope. Voltage is calculated as voltage channel times two plus transistor Vce plus an estimated shunt drop from the current channel. Current is calculated from the current channel through the divider and shunt assumptions. `lego_ev3_battery_set_property()` permits only `POWER_SUPPLY_PROP_TECHNOLOGY` from unknown to NiMH and updates design limits. `property_is_writeable()` enforces that one-time policy.

## Control Flow
Probe gets the `voltage` and `current` IIO channels plus a required `rechargeable` GPIO. It samples the GPIO once because the pack cannot change without removal. A true GPIO selects Li-ion with fixed limits; false selects unknown/alkaline-style limits. It registers `lego-ev3-battery` with fwnode and driver data.

## State and Persistence
The chosen technology and design limits persist in memory until driver removal. The one writable path can change unknown to NiMH, but there is no way back to unknown. Measurements are read live from IIO and not cached.

## Dependencies and Integration Points
It depends on two processed IIO channels, a GPIO descriptor from DT, the power-supply core, and the `lego,ev3-battery` compatible. The driver is system-scope only and does not expose charger state.

## Risks
The Li-ion and alkaline/NiMH design voltage constants appear one decimal place larger than typical EV3 pack values if interpreted as microvolts, so downstream behavior depends on whether this source tree intentionally carries that scaling. Measurement formulas hard-code board resistor/transistor assumptions. The technology override is stateful and irreversible until reboot/remove.

## Test Signals
Validate IIO conversion math for voltage and current, GPIO true/false technology selection, one-time NiMH write behavior, rejection of Li-ion overrides, design voltage updates after NiMH selection, missing-channel probe errors, and fwnode registration.
