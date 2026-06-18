<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams-i2c.c

Purpose: This file implements the I2C backend for Apple Motion Sensor devices, using SMBus byte access to reset/start the accelerometer, read axes, configure thresholds, and enable/clear interrupts.

Important APIs and state: `ams_i2c_driver` matches `"MAC,accelerometer_1"`. Backend callbacks are `ams_i2c_get_xyz()`, `ams_i2c_get_vendor()`, `ams_i2c_clear_irq()`, and exit `ams_i2c_exit()`. Helper functions read/write registers and issue commands through `ams_i2c_cmd()`.

Control flow: `ams_i2c_init()` fills `ams_info` with OF node, callbacks, bus type `BUS_I2C`, and registers the I2C driver. Probe rejects a second device, stores the client, resets and starts the chip, reads and validates device and firmware versions, disables interrupts, calls `ams_sensor_attach()`, writes default sensitivity/control registers, clears pending interrupts, marks device present, enables interrupts, and logs success. Remove detaches, disables and clears interrupts, and clears presence state.

State and persistence: The I2C client pointer and presence flag live in `ams_info`. Hardware register defaults are programmed on probe and are not persisted by the driver. Axis reads are synchronous SMBus operations under the core mutex.

Dependencies and integration: It depends on I2C/SMBus, delays/timeouts, the AMS core's singleton state and function-pointer contract, and OF discovery from core.

Risks and test signals: `ams_i2c_cmd()` treats command register zero or bit 7 as success; timeouts return `-1` rather than a standard errno. SMBus read errors are truncated into `u8` in several paths. Test reset/start failures, version mismatch, interrupt enable/disable register bits, remove after partial attach failure, and axis read error behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams-i2c.c -->
