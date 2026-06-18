# sources/distributed-fs/ceph-client/drivers/power/supply/ltc4162-l-charger.c

## Purpose
This I2C/regmap driver supports LTC4162-L, LTC4162-F, LTC4162-S, and LTC4015 charger controllers. It exposes charger status, charge type, health, input telemetry, charge current/voltage limits, input current limit, die temperature, and termination current, plus sysfs controls for raw telemetry, forced telemetry, and ship mode.

## Important APIs, Types, and Functions
`struct ltc4162l_chip_info` provides per-chip names, voltage conversion callbacks, die-temperature callback, current/voltage resolutions, and telemetry-mask bits. `struct ltc4162l_info` stores client, regmap, charger supply, chip info, RSNSB/RSNSI resistor values, and cached cell count. State decoders map charger-state and charge-status registers to power-supply status, charge type, and health. Conversion helpers read VBAT/VCHARGE differently for LTC4162 lithium/LiFePO4/lead-acid, LTC4015 lead-acid encodings, IBAT/IIN through resistor values, input voltage, die temperature, input-current DAC, and termination threshold. Setters program max charge current, max charge voltage, input current target, and C-over-X termination current.

## Control Flow
Probe verifies SMBus word-data support, allocates state, selects chip info from I2C/OF match, initializes a 16-bit little-endian cached regmap, requires nonzero `lltc,rsnsb-micro-ohms` and `lltc,rsnsi-micro-ohms`, optionally seeds cell count from `lltc,cell-count`, duplicates the descriptor to set the chip-specific name, registers the mains supply with sysfs groups, disables limit alerts, enables charger-state and charge-status alerts, and clears pending alerts. SMBus alert callbacks clear alerts and notify the power supply.

## State and Persistence
Cell count is cached after the first successful hardware read or from firmware. Writable properties persist in controller registers. Regmap caches nonvolatile writable registers and treats status registers as volatile. Sysfs writes can force telemetry and arm ship mode; those are direct hardware state changes.

## Dependencies and Integration Points
It depends on I2C SMBus word transactions, regmap with 16-bit little-endian values and maple cache, OF/device properties for sense resistors, SMBus alert support, power-supply writable properties, and per-chip compatible data.

## Risks
The generic `ltc4162l_set_property()` always calls `ltc4162l_set_vcharge()` rather than the chip-info `set_vcharge` callback, so LTC4015 writable charge-voltage behavior may not match its getter/conversion table. Several conversions require a nonzero detected cell count and return `-EBUSY` or invalid values while the chip has not determined cells. Sysfs `arm_ship_mode` is a powerful persistent control. Unit conversions depend directly on correct resistor properties.

## Test Signals
Test all four chip-info paths, chemistry and cell-count conversions, writable current/voltage/input-limit/termination properties, zero and invalid resistor DT values, SMBus alert notification, forced telemetry and ship-mode sysfs behavior, regmap cache/volatile behavior, and the LTC4015 charge-voltage setter path.
