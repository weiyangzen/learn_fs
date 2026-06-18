<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr-i2c.c

Purpose: optional I2C bridge for the HD-PVR, primarily to expose the Zilog IR receiver/transmitter device through the Linux I2C and `ir-kbd-i2c` infrastructure.

Important APIs/types/functions: `hdpvr_register_i2c_adapter()` activates IR hardware and registers an `i2c_adapter`. `hdpvr_register_ir_i2c()` creates an `ir_z8f0811_hdpvr` client with Hauppauge RC map/protocol metadata. `hdpvr_transfer()` implements I2C master transfers over USB control messages. `hdpvr_i2c_read()` and `hdpvr_i2c_write()` wrap firmware read/write/status request types. `hdpvr_algo` and `hdpvr_quirks` define adapter behavior.

Control flow: probe calls `hdpvr_register_i2c_adapter()`, which sends activation writes to the device, copies the adapter template, sets parent/adapdata, and calls `i2c_add_adapter()`. The IR client is then registered. I2C users enter `hdpvr_transfer()`, which serializes operations with `i2c_mutex`, converts the 7-bit address to the device format, and supports single read/write or combined write-then-read transactions.

State and persistence: `dev->i2c_adapter`, `dev->i2c_mutex`, `dev->i2c_buf`, and `dev->ir_i2c_init_data` persist for the device lifetime. The IR activation writes persist in firmware/hardware until reset. No filesystem persistence exists.

Dependencies and integration: compiled only when `CONFIG_I2C` is enabled. Integrates with USB control transport, Linux I2C core, `ir-kbd-i2c`, remote-control protocol maps, and cleanup paths in core/video release.

Risks: the adapter supports only a narrow transaction set and marks zero-length reads unsupported; clients outside the intended IR path may fail. `hdpvr_activate_ir()` ignores read/write return values, so IR registration can proceed after activation failures. `hdpvr_i2c_write()` validates completion by checking `i2c_buf[1] == len - 1`, which is firmware-specific. Shared `i2c_buf` requires all transfer users to obey `i2c_mutex`.

Test signals: build with and without `CONFIG_I2C`; verify adapter registration and IR client creation; test remote key events; run I2C transfer fault injection for read/write/status failures; unbind while IR polling is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr-i2c.c -->
