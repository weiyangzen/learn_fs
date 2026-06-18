# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-keba.c

Purpose: implements an auxiliary-bus I2C adapter for the KEBA FPGA I2C controller IP core. It supports a hardware `IN_USE` semaphore for sharing with non-Linux processors, direct SCL/SDA bus recovery when available, bytewise fallback recovery, and registration of known board devices supplied by the parent KEBA auxiliary device.

Important APIs, types, and functions: `struct ki2c` stores the KEBA auxiliary device wrapper, mapped register base, adapter, and client list. `ki2c_xfer()` is the algorithm hook. Important helpers handle hardware semaphore lock/unlock, wait for transfer complete/ACK cycles, direct-control capability, bitwise and bytewise bus reset, address/start/repeated-start/stop, byte read/write, and child-device registration.

Control flow: probe allocates state and client array, maps the auxiliary IO resource, initializes the adapter, enables the controller, resets the bus, registers the adapter, then scans/registers known devices from `keba_i2c_auxdev->info`. A transfer locks the hardware semaphore, sends START for the first message or repeated START for later read messages, performs byte-wise read or write, sends STOP, then unlocks the semaphore.

State and persistence: persistent software state includes the registered adapter and array of scanned `i2c_client` pointers for cleanup. Hardware persistence includes controller enable, direct-control line state, and the hardware semaphore. The driver explicitly disables the controller on probe failure and remove.

Dependencies and integration points: integrates with KEBA MFD/auxiliary bus types from `linux/misc/keba.h`, MMIO register access, devm resource mapping, `i2c_new_scanned_device`, HWMON class devices, and the I2C core.

Risks: repeated-start write is explicitly unsupported and returns `-EINVAL`, so combined write-write sequences cannot work. The bytewise recovery fallback may write an extra `0xff` to EEPROM-like devices; the comment recommends bitwise recovery where direct control exists. The hardware semaphore may block for up to ten seconds. ACK status maps to `-EIO` rather than `-ENXIO`, which affects clients expecting address-specific errors.

Test signals: auxiliary probe/remove, bus reset with and without direct-control capability, SCL stuck-low and SDA stuck-low recovery failures, hardware semaphore contention, read zero-length and one-byte paths, read final-byte NACK timing, write ACK failure, repeated-start read success, repeated-start write rejection, child device scanning/unregistering, and controller disable on failures.
