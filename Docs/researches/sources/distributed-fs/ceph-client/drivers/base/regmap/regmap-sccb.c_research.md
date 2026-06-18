<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-sccb.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-sccb.c

Purpose: Implements regmap support for SCCB-style camera sensor register access using compatible I2C/SMBus operations.

Important APIs/types/functions: `sccb_is_available()` checks required adapter functionality. `regmap_sccb_read()` performs SCCB read sequencing. `regmap_sccb_write()` uses SMBus byte-data writes. `regmap_get_sccb_bus()`, `__regmap_init_sccb()`, and `__devm_regmap_init_sccb()` provide selection and initialization.

Control flow: The bus is available only for 8-bit register and 8-bit value configs with SMBus byte and write-byte-data functionality. Reads lock the I2C segment, perform a write-byte phase to set the register, then perform a byte read phase, store the returned byte, and unlock. Writes call `i2c_smbus_write_byte_data()` directly.

State and persistence behavior: The adapter owns no heap or persistent state. It uses the I2C adapter bus lock only during each read transaction.

Dependencies and integration points: Depends on I2C/SMBus internals, adapter functionality flags, and regmap core. It integrates with sensor drivers that expose SCCB as a variant of I2C rather than a native kernel SCCB bus.

Risks: It uses `__i2c_smbus_xfer()` while holding a segment lock to express SCCB’s two-phase read sequence. Only 8/8 formats are supported. Future native SCCB adapter support would need a new algorithm callback. Incorrect adapter functionality reporting results in `-ENOTSUPP`.

Test signals: Validate bus selection, read lock/unlock around both phases, propagation of either phase failure, and write-byte-data use for writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-sccb.c -->
