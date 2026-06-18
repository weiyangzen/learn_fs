<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/adxl34x-i2c.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/adxl34x-i2c.c

Purpose: I2C/SMBus transport wrapper for the ADXL345/ADXL346 accelerometer core.

Important APIs/types/functions: `adxl34x_smbus_read()`, `adxl34x_smbus_write()`, `adxl34x_smbus_read_block()`, and `adxl34x_i2c_read_block()` implement `struct adxl34x_bus_ops`. `adxl34x_i2c_probe()` checks byte-data support, chooses SMBus block read when available or raw I2C block read otherwise, then calls `adxl34x_probe()`.

Control flow and state: probe performs adapter capability validation, delegates all device initialization to the core, and stores the returned core pointer with `i2c_set_clientdata()`. The module registers an `i2c_driver` with I2C IDs and OF compatibles.

State and persistence behavior: this file owns no sensor state beyond client driver data. Register state, sysfs attributes, input events, and PM behavior are handled in `adxl34x.c`.

Dependencies and integration points: depends on I2C/SMBus APIs, OF matching for `adi,adxl345` and deprecated `adi,adxl34x`, the local `adxl34x.h` ABI, and core `adxl34x_groups`/`adxl34x_pm`.

Risks: the raw I2C block fallback only checks receive length, while the preceding address send may return a short positive count that is not rejected. Device tree lists only ADXL345 because ADXL346 is runtime-detected.

Test signals: test adapters with and without SMBus block support, missing IRQ, device-ID mismatch propagated from the core, OF autoloading, and sysfs group/PM attachment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/adxl34x-i2c.c -->
