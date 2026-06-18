# sources/distributed-fs/ceph-client/drivers/mfd/ene-kb3930.c

## Purpose
`ene-kb3930.c` is an I2C MFD driver for the ENE KB3930 embedded controller used by the Dell Wyse Ariel platform. It exposes EC RAM through regmap, validates the board model, registers child devices, and optionally provides board power-off/restart signaling through GPIOs.

## Important APIs, Types, and Functions
`struct kb3930` stores the I2C client, EC RAM regmap, and optional off GPIO array. `kb3930_ec_ram_reg_read()` and `kb3930_ec_ram_reg_write()` implement custom regmap access through EC RAM multiplexing registers. `kb3930_off()` drives the off-mode GPIO and generates a 10 Hz shutdown/reset wave forever. `kb3930_restart()` and `kb3930_pm_power_off()` hook into restart and power-off infrastructure. `kb3930_probe()` and `kb3930_remove()` manage lifecycle.

## Control Flow
Probe allocates state, initializes the custom EC RAM regmap, reads `EC_MODEL`, rejects non-`'J'` boards, registers Ariel LED and power child cells, and if the node is a system power controller, obtains two `off-gpios` and installs restart and optional `pm_power_off` handlers. Restart or poweroff calls enter `kb3930_off()` and intentionally never return while toggling the EC wave GPIO.

## State and Persistence
The global `kb3930_power_off` points at the active device for global callbacks. EC RAM is volatile device state exposed by regmap. Power-off mode GPIO state and wave toggling are external board-control signals. No persistent storage is used.

## Dependencies and Integration Points
The driver depends on I2C SMBus word accesses, regmap custom bus callbacks, GPIO descriptors, MFD core, OF system-power-controller detection, Linux restart handlers, and the global `pm_power_off` hook.

## Risks and Edge Cases
Only model `J` is supported. `kb3930_power_off` is a singleton, so multiple EC instances would conflict. If `off-gpios` has fewer than two descriptors, probe fails. Power-off/restart loops forever by design; wrong GPIO wiring can hang without reset or shutdown.

## Test Signals
Validate EC RAM reads for model/version registers, rejection of unknown models, child device creation, off-gpio count validation, restart handler registration/removal, `pm_power_off` ownership behavior, and actual EC shutdown/reset signaling on hardware.
