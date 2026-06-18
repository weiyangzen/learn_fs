# sources/distributed-fs/ceph-client/include/linux/i2c.h

## Purpose
Defines the Linux I2C bus core interface: clients, drivers, adapters, algorithms, board info, transfers, SMBus helpers, slave mode, recovery, quirks, firmware discovery, and registration helpers.

## APIs, Control Flow, and State
Important types are `struct i2c_driver`, `struct i2c_client`, `struct i2c_board_info`, `struct i2c_algorithm`, `struct i2c_lock_operations`, `struct i2c_timings`, `struct i2c_bus_recovery_info`, `struct i2c_adapter_quirks`, and `struct i2c_adapter`. Transfer flow starts at `i2c_master_send/recv()` or `i2c_transfer()`, then dispatches through adapter `algo` callbacks; SMBus helpers dispatch through `i2c_smbus_xfer()` or emulation. Adapter state includes locks, timeout/retries, device object, suspend flags, userspace client list, recovery info, quirks, host-notify IRQ domain, regulator, debugfs, and address-instantiation bitmap. Registration APIs add/del adapters and drivers, create static/scanned/dummy/ancillary clients, parse firmware timings, and find clients/adapters by fwnode/OF/ACPI. Disabled I2C/OF/ACPI paths provide stubs.

## Dependencies, Integration, Risks, and Tests
Depends on device model, ACPI, OF, regulator, rtmutex, IRQ domains, uapi I2C messages, and optional slave/mux support. It integrates with almost every I2C controller and device driver, userspace i2c-dev, firmware enumeration, runtime/system suspend, bus recovery, and SMBus alert/host notify. Risks include missing adapter functionality checks, violating adapter quirks, transfer while suspended, incorrect root-vs-segment locking, DMA-unsafe buffers, client lifetime leaks from find helpers, and broken firmware enumeration fallback. Test signals include I2C selftests, adapter registration/removal, SMBus protocol vectors, bus recovery, mux locking, suspend transfer rejection, ACPI/OF enumeration, and config-matrix builds.
