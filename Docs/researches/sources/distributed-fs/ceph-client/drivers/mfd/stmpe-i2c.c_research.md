# sources/distributed-fs/ceph-client/drivers/mfd/stmpe-i2c.c

## Purpose
`stmpe-i2c.c` is the I2C transport wrapper for the STMPE MFD core. It supplies byte/block SMBus accessors, maps OF/I2C IDs to STMPE part numbers, and delegates common setup and teardown to `stmpe_probe()` and `stmpe_remove()`.

## Important APIs, Types, and Functions
Transport callbacks are `i2c_reg_read()`, `i2c_reg_write()`, `i2c_block_read()`, and `i2c_block_write()`. `stmpe_i2c_probe()` prepares `stmpe_client_info` and selects the part number from OF match data or I2C ID. `stmpe_i2c_remove()` calls core removal. OF and I2C tables cover STMPE610, 801, 811, 1600, 1601, 1801, 2401, and 2403.

## Control Flow
The I2C driver probes, fills the static `i2c_ci` with current client, IRQ, and device pointers, resolves the part number, and calls the common STMPE core. Remove fetches core state from device data and tears it down through `stmpe_remove()`.

## State and Persistence
This wrapper has static callback data updated at probe time and no separate persisted state. Device state is allocated by `stmpe.c`.

## Dependencies and Integration Points
It depends on SMBus byte and I2C block operations and the internal `stmpe.h` core interface. The PM ops are exported by the common STMPE core.

## Risks and Edge Cases
The static `i2c_ci` is shared by all devices, so concurrent multi-device probe would rewrite the transport context before the common core copies/uses it. OF-less matching falls back to I2C ID and logs that compatible strings are preferred.

## Test Signals
Probe all supported compatibles, exercise byte and block register access, verify fallback ID matching, check PM callback wiring, and remove/reprobe without stale core state.
