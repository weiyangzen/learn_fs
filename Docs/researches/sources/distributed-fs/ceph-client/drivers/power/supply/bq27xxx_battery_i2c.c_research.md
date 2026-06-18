# sources/distributed-fs/ceph-client/drivers/power/supply/bq27xxx_battery_i2c.c

Purpose: adapts the shared BQ27xxx battery core to I2C fuel-gauge devices. It provides byte/word and block read/write callbacks, maps many I2C IDs and OF compatibles to BQ27xxx chip IDs, handles optional IRQ-driven updates, and manages unique battery names.

Important APIs/types/functions: `bq27xxx_battery_i2c_read()` performs register-address write plus one- or two-byte read with limited `-EBUSY` retry and little-endian conversion. `bq27xxx_battery_i2c_write()`, `bq27xxx_battery_i2c_bulk_read()`, and `bq27xxx_battery_i2c_bulk_write()` implement the core bus callbacks. `bq27xxx_battery_i2c_probe()` allocates an IDA number, creates a name like `<id>-<num>`, fills `bq27xxx_device_info`, calls `bq27xxx_battery_setup()`, schedules initial polling, and requests an optional threaded IRQ. `bq27xxx_battery_i2c_remove()` frees the IRQ and tears down the core.

Control flow: module registration binds the I2C driver. Probe sets up the bus abstraction before invoking the shared core; after setup it schedules a delayed update about one minute later and installs the IRQ handler if `client->irq` is present. IRQ handling simply calls `bq27xxx_battery_update()`. Remove reverses IRQ registration and shared core setup. PM operations are provided by the shared core through the driver's `.pm` pointer.

State and persistence: local state is the global IDA for names and the per-client `bq27xxx_device_info`. I2C write and bulk-write support lets the shared core update gauge data memory on chips that advertise data-memory tables. Workqueue/cache state is in the shared core.

Dependencies and integration: depends on I2C transfers, SMBus block reads, unaligned little-endian helpers, interrupts, module device tables, and `linux/power/bq27xxx_battery.h`. The OF table is compatible-only; chip selection for OF-probed devices depends on I2C ID matching behavior.

Risks and test signals: `bq27xxx_battery_i2c_read()` does not verify that `i2c_transfer()` returned exactly two messages, so short positive transfers could be misinterpreted. Bulk writes use a 33-byte stack buffer and assume the core's 32-byte data-memory blocks. The IRQ is requested with non-devm `request_threaded_irq()`, so remove and probe-error teardown must remain correct. Test all ID mappings, busy-retry behavior, short-transfer failure behavior, block read/write lengths, optional IRQ update path, shared PM suspend/resume, and probe failure after `bq27xxx_battery_setup()`.
