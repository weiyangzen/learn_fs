# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-dln2.c

## Purpose
I2C interface driver for the Diolan DLN-2 MFD USB device. It exposes each DLN2 I2C port as a Linux adapter and delegates actual transport to the parent DLN2 command layer.

## Important APIs, Types, And Functions
`struct dln2_i2c` stores platform device, adapter, port number, and a shared transfer buffer. Commands are built with `DLN2_I2C_CMD()`. Core helpers are `dln2_i2c_enable()`, `dln2_i2c_write()`, `dln2_i2c_read()`, `dln2_i2c_xfer()`, and `dln2_i2c_func()`. Probe/remove are `dln2_i2c_probe()` and `dln2_i2c_remove()`.

## Control Flow
Probe allocates state and a transfer buffer, reads the port from platform data, initializes adapter fields and ACPI/OF linkage, enables the DLN2 I2C port via parent command, and registers the adapter. Transfers iterate messages independently; read messages issue `DLN2_I2C_READ` and validate returned lengths, while writes issue `DLN2_I2C_WRITE` and require the full length to be accepted.

## State And Persistence
Per-adapter state is small and device-managed. The shared buffer is safe because I2C core serializes adapter transfers. The hardware port is enabled on probe and disabled on remove.

## Dependencies And Integration Points
Depends on the DLN2 MFD API (`dln2_transfer()` and `dln2_transfer_tx()`), platform data, ACPI companion propagation, and Linux I2C quirks for maximum transfer size.

## Risks
The driver does not combine messages into one firmware transaction, so repeated-start semantics depend on DLN2 command capabilities and may be limited. Buffer size is capped at 256 bytes. Strict protocol length checks can surface firmware inconsistencies as `-EPROTO`.

## Test Signals
Test enable/disable commands, read/write at boundary sizes, protocol length mismatch, adapter quirk enforcement, multiple port naming, ACPI companion linkage, and cleanup when `i2c_add_adapter()` fails.
