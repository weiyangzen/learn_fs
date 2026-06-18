# sources/distributed-fs/ceph-client/drivers/power/supply/s2mu005-battery.c

## Purpose
Samsung S2MU005 PMIC fuel-gauge driver. It exposes voltage, average voltage, current, average current, capacity, and charging status for the PMIC battery gauge.

## Important APIs, Types, and Functions
`struct s2mu005_fg` holds device, 16-bit little-endian regmap, power supply, and `monout_mutex`. Conversion helpers read PMIC registers: `s2mu005_fg_get_voltage_now()`, `s2mu005_fg_get_voltage_avg()`, `s2mu005_fg_get_current_now()`, `s2mu005_fg_get_current_avg()`, `s2mu005_fg_get_capacity()`, and `s2mu005_fg_get_status()`.

## Control Flow
Probe initializes regmap, mutex, power supply, and a threaded IRQ. Direct properties read dedicated registers. Average voltage/current serialize access to `MONOUTSEL` and `MONOUT` because the monitor output register is multiplexed. IRQ sleeps briefly, then calls `power_supply_changed()`.

## State and Persistence
State is minimal and volatile. No persistent calibration or cached measurement is stored. The only mutable hardware selector is `MONOUTSEL`, protected by a mutex.

## Dependencies and Integration Points
Depends on I2C, regmap, IRQ, mutexes, firmware match data, and power_supply. Matched by `samsung,s2mu005-fuel-gauge`; descriptor is supplied through OF match data.

## Risks and Test Signals
Probe logs mutex and IRQ setup failures but does not return those errors, so a driver can bind without a requested IRQ or with a failed mutex init return path. Status inference depends on signed current conversion and treats `current_now == 0` as not charging regardless of average current. Test register endianness, negative current handling, MONOUT serialization, IRQ-less behavior, and capacity threshold for full status.
