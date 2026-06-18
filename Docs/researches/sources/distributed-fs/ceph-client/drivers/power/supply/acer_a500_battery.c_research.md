# sources/distributed-fs/ceph-client/drivers/power/supply/acer_a500_battery.c

## Purpose
`acer_a500_battery.c` is a platform battery driver for the Acer Iconia Tab A500. It reads battery telemetry from the parent embedded-controller regmap named `KB930`, exposes it through the power-supply class, and polls capacity periodically to emit change notifications.

## Important APIs, Types, And Functions
- `struct a500_battery` stores delayed polling work, registered `power_supply`, parent EC `regmap`, and cached capacity.
- `ec_data[]` maps EC registers to `POWER_SUPPLY_PROP_CAPACITY`, `VOLTAGE_NOW`, `CURRENT_NOW`, `CHARGE_FULL_DESIGN`, and `TEMP`.
- `a500_battery_update_capacity()` reads and clamps capacity to 100%.
- `a500_battery_get_status()` derives charging/discharging/full from cached capacity and `power_supply_am_i_supplied()`.
- `a500_battery_unit_adjustment()` converts EC units to power-supply units: mV/mA/mAh-style values to micro units, Kelvin deci-units to Celsius deci-degrees, and presence to boolean.
- `a500_battery_get_property()` serves all exposed properties.
- `a500_battery_poll_work()` polls capacity every 30 seconds and calls `power_supply_changed()` only when capacity changes.

## Control Flow
Probe allocates state, gets the parent `KB930` regmap, registers the `ec-battery` power supply using the parent firmware node, initializes delayed polling, and schedules the first poll after one second. Property reads either return derived status/technology/capacity or read an EC register and apply unit conversion. Remove and suspend cancel the delayed work; resume restarts it.

## State And Persistence
The only driver-owned state is cached capacity and the delayed-work schedule. All persistent telemetry is owned by the EC. The driver does not write EC registers and does not persist capacity across reprobe. Presence is inferred from the design-capacity register being non-zero.

## Dependencies And Integration Points
The driver depends on a parent platform device exposing `dev_get_regmap(parent, "KB930")`, the power-supply framework, firmware-node propagation from the parent, and external supplies for `power_supply_am_i_supplied()`. It registers as platform driver alias `acer-a500-iconia-battery`.

## Risks
- If the EC returns transient register-read errors, property reads return `-ENODATA`; polling silently ignores failed capacity updates.
- Status is derived from cached capacity, so a stale cached value after read failures can affect full/charging/discharging reporting.
- Presence uses `CHARGE_FULL_DESIGN` as a proxy. A malformed EC value can make a disconnected battery appear present or hide a connected one.
- Unit conversion assumes specific EC units; a parent regmap variant with different units would report incorrect values.

## Test Signals
- Mock regmap reads for all EC registers, including failed reads, capacity over 100%, zero design capacity, and temperature conversion.
- Verify poll work emits `power_supply_changed()` only on capacity changes and is canceled/restarted across suspend/resume/remove.
- Exercise supplied/not-supplied status with capacity below 100 and full status at 100.
