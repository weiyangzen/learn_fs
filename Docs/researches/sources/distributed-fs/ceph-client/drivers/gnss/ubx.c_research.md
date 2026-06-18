# sources/distributed-fs/ceph-client/drivers/gnss/ubx.c

## Purpose
`ubx.c` is the u-blox serial GNSS receiver driver. It uses the generic GNSS serial helper and adds regulator and GPIO setup for common u-blox modules.

## Important APIs, Types, and Functions
Private state is `struct ubx_data` containing the `vcc` regulator. Power callbacks are `ubx_set_active()`, `ubx_set_standby()`, and `ubx_set_power()`. Probe and remove are `ubx_probe()` and `ubx_remove()`.

## Control Flow
Probe allocates a serial GNSS wrapper, sets power ops and type `GNSS_TYPE_UBX`, gets mandatory `vcc`, optionally enables backup regulator `v-bckp`, deasserts optional `safeboot` and `reset` GPIOs by driving them low, and registers the serial GNSS device. The serial helper handles serdev open/close, data flow, and PM. Remove deregisters and frees the wrapper.

## State and Persistence
Runtime state is the serial wrapper, GNSS device, regulator handle, and devm-managed GPIO/regulator resources. There is no persistent state.

## Dependencies and Integration Points
The driver depends on serdev, GNSS serial helper, regulator and GPIO descriptor frameworks, and OF compatibles `u-blox,neo-6m`, `u-blox,neo-8`, and `u-blox,neo-m8`.

## Risks and Test Signals
Backup regulator is enabled by devm helper and not explicitly disabled in remove, relying on devm cleanup. Safeboot and reset GPIO polarity depends on board descriptions matching `GPIOD_OUT_LOW`. Tests should cover optional resource absence, mandatory `vcc` failure, GPIO acquisition failure, PM transitions, and GNSS read/write through serdev.
