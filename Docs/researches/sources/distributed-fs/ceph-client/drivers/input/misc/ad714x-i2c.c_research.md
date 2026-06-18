# sources/distributed-fs/ceph-client/drivers/input/misc/ad714x-i2c.c

## Purpose

This I2C transport driver connects Analog Devices AD714x capacitive touch controllers to the shared AD714x core. It supplies big-endian register read/write callbacks and registers chip instances for AD7142/AD7143/AD7147/AD7147A/AD7148 I2C IDs.

## Important APIs, Types, and Functions

`ad714x_i2c_write()` writes a 16-bit register address and 16-bit data word through `i2c_master_send()`. `ad714x_i2c_read()` writes the 16-bit register address, receives `len` 16-bit words, and converts from big-endian to CPU endian. `ad714x_i2c_probe()` calls the common `ad714x_probe()` with `BUS_I2C`, client IRQ, and transport callbacks, then stores chip data with `i2c_set_clientdata()`.

## Control Flow

When an I2C device ID matches, probe delegates most setup to the shared AD714x core. All later core register accesses call this file's transport callbacks. Reads first send the target register address and then perform a receive for the requested word count. Writes send address and data in one transfer.

## State and Persistence Behavior

The transport layer owns no independent state beyond the common chip pointer stored as I2C client data. It uses the shared chip transfer buffer for endian-converted command/data words.

## Dependencies and Integration Points

It depends on the I2C core, `ad714x.h` shared core, PM ops exported as `ad714x_pm`, and input bus identity `BUS_I2C`. The ID table controls module autoload for named I2C devices.

## Risks and Edge Cases

`i2c_master_send()` and `i2c_master_recv()` positive short transfers are treated as success; the code only checks `< 0`, so partial transfers can corrupt core register state. Shared `xfer_buf` length must be large enough for the maximum core read length. There is no OF/SPI-style device table here beyond I2C IDs.

## Test Signals

Test read/write endian correctness, partial transfer injection, negative I2C errors, all ID table names, IRQ propagation to core probe, PM suspend/resume through `ad714x_pm`, and concurrent core accesses if any locking is expected in the shared driver.
