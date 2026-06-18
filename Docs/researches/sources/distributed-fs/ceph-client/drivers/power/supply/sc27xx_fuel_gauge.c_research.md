# sources/distributed-fs/ceph-client/drivers/power/supply/sc27xx_fuel_gauge.c

## Purpose
Spreadtrum SC27XX PMIC fuel-gauge driver. It exposes battery presence, voltage/current, OCV, boot voltage, capacity, charge counter, health, and calibration controls using PMIC FGU registers, NVMEM calibration, IIO channels, and battery-info OCV/resistance tables.

## Important APIs, Types, and Functions
`struct sc27xx_fgu_data` stores regmap, battery power supply, base, mutex, detect GPIO, IIO channels, calibration constants, battery tables, capacity state, boot voltage, and coulomb-counter state. Key functions are `sc27xx_fgu_hw_init()`, `sc27xx_fgu_get_boot_capacity()`, `sc27xx_fgu_get_capacity()`, `sc27xx_fgu_capacity_calibration()`, `sc27xx_fgu_interrupt()`, `sc27xx_fgu_bat_detection()`, suspend/resume callbacks, and property get/set callbacks.

## Control Flow
Probe acquires regmap/base/calibration resistance, IIO channels, battery-detect GPIO, registers the battery power supply, initializes hardware, installs disable cleanup, requests FGU and GPIO IRQs, and sets drvdata. Hardware init loads battery info, OCV table, resistance table, NVMEM calibration, enables FGU/RTC clock, clears interrupts, programs low-voltage and coulomb delta thresholds, computes boot capacity, and seeds the coulomb counter. Runtime capacity is initial capacity plus coulomb-counter delta with OCV-based calibration.

## State and Persistence
The PMIC user area stores boot mode and last capacity across non-first power-on. Driver state caches `init_cap`, `init_clbcnt`, `alarm_cap`, `min_volt`, `boot_volt`, tables, and calibration factors. Writable properties can save capacity, adjust calibration baseline, or change total capacity.

## Dependencies and Integration Points
Depends on PMIC regmap, NVMEM cell `fgu_calib`, IIO channels `bat-temp` and `charge-vol`, battery-detect GPIO, power_supply battery-info tables, and charger supplies named `sc2731_charger`, `sc2720_charger`, `sc2721_charger`, or `sc2723_charger`.

## Risks and Test Signals
Capacity correctness depends on calibration resistance, NVMEM data, OCV table ordering, and charger status lookup by fixed names. `sc27xx_fgu_get_status()` iterates all charger names and returns the last successful status, not the first. Test first and warm boot paths, user-area writes, NVMEM failures, low-voltage IRQ calibration, suspend interrupt enable/disable, GPIO presence IRQ, and writable property effects.
