# sources/distributed-fs/ceph-client/drivers/input/touchscreen/cyttsp_i2c.c

Purpose: `cyttsp_i2c.c` is the I2C transport shim for the older Cypress TTSP core. It supplies `struct cyttsp_bus_ops` implementations that translate the core's 16-bit register accesses into the controller's I2C addressing convention.

Important APIs, types, and functions: `cyttsp_i2c_read_block_data()` builds a two-message I2C transfer: write low address byte, then read the requested length. `cyttsp_i2c_write_block_data()` prefixes the low address byte into the shared transfer buffer and writes the address plus payload. Both derive `client_addr` from the base I2C address ORed with bit 8 of the requested register. `cyttsp_i2c_probe()` checks `I2C_FUNC_I2C`, calls `cyttsp_probe()` with `CY_I2C_DATA_SIZE`, and stores the returned core pointer.

Control flow: module registration creates an I2C driver named `cyttsp-i2c`. Matching clients for `cypress,cy8ctma340` or `cypress,cy8ctst341` run the functionality check, instantiate the shared core, and inherit the core PM ops.

State and persistence: this file keeps no independent runtime or persistent state. The I2C client data points to the `struct cyttsp` allocated by the core.

Dependencies and integration points: it depends on the core header, Linux I2C and input bus constants, OF match data, and `pm_sleep_ptr(&cyttsp_pm_ops)`. The transfer buffer ownership remains in the core object.

Risks: the high register bit being encoded into the slave address is unusual and hardware-specific; adapters or board descriptions with incompatible address handling will fail transfers. Write length is limited by the 128-byte core buffer minus one address byte. Errors are detected by exact I2C message count.

Test signals: check probe on both compatible strings, read/write paths with registers below and above 0x100, transfer failure propagation, and PM callbacks through the shared core.
