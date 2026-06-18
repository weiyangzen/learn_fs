<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/i2c.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/i2c.c

## Purpose
Implements the I2C physical transport for ST33ZP24 TPM 1.2 devices and delegates TPM protocol handling to the shared ST33ZP24 core.

## Important APIs, Types, And Functions
Defines `struct st33zp24_i2c_phy`, low-level helpers `write8_reg()` and `read8_reg()`, transport callbacks `st33zp24_i2c_send()` and `st33zp24_i2c_recv()`, and driver callbacks `st33zp24_i2c_probe()` and `st33zp24_i2c_remove()`. It registers I2C IDs, OF compatible `st,st33zp24-i2c`, ACPI ID `SMO3324`, and PM ops using `st33zp24_pm_suspend()`/`resume()`.

## Control Flow
Probe verifies adapter I2C capability, allocates a per-device physical context, stores the `i2c_client`, and calls `st33zp24_probe()` with the I2C send/receive callbacks and IRQ. Writes prepend the TPM register byte; reads first write a dummy byte to select the register and then receive the requested payload.

## State And Persistence
The per-device I2C context persists as devm memory and includes a scratch buffer sized for the ST33ZP24 FIFO plus address byte. The actual TPM chip state is owned by the shared core.

## Dependencies And Integration Points
Integrates Linux I2C, OF, ACPI, TPM core, and `st33zp24.h`. `i2c_set_clientdata()` is indirectly handled through `tpmm_chip_alloc()` setting driver data on the parent device.

## Risks And Edge Cases
The read path expects `write8_reg()` to return exactly two bytes for the register-select transaction before receiving data. Buffer sizing assumes `tpm_size <= ST33ZP24_BUFSIZE`. Transport errors propagate to the core timing and locality logic.

## Test Signals
Probe with capable and incapable I2C adapters, read/write TPM registers under fault injection, interrupt and polling modes through the shared core, ACPI/OF matching, suspend/resume, and oversized transaction rejection by upper layers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/i2c.c -->
