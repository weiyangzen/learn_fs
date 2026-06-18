# sources/distributed-fs/ceph-client/drivers/iio/proximity/vl53l0x-i2c.c

Purpose: I2C IIO distance driver for ST VL53L0X FlightSense time-of-flight sensors. It supports direct single-shot range reads, scale reporting in meters from millimeters, optional IRQ completion, optional triggered-buffer continuous mode, regulator/reset control, and model-ID probing.

Important APIs/types/functions: `struct vl53l0x_data` stores client, completion, VDD regulator, reset GPIO, and trigger. `vl53l0x_read_proximity()` starts a single measurement and waits by IRQ completion or polling. `vl53l0x_trigger_handler()` reads the 12-byte result block and pushes range plus timestamp. Buffer postenable/postdisable switch continuous/single mode.

Control flow: probe validates SMBus capabilities, reads model ID, enables power and reset, registers cleanup action, configures IIO channel metadata, and if IRQ exists, allocates trigger, configures GPIO interrupt mode, and sets up a triggered buffer. Direct raw read writes `SYSRANGE_START`, waits up to 100 ms, clears IRQ if needed, reads result bytes, and returns the big-endian millimeter value.

State and persistence: power state is managed for device lifetime by devm action. The sensor mode changes between single and continuous when the buffer is toggled. Completion is only initialized when IRQ is present. The driver does not cache range values or configuration beyond trigger/power handles.

Dependencies/integration: depends on I2C SMBus byte/block transfers, regulators, optional reset GPIO, IRQ trigger type, IIO direct mode, IIO triggers, and triggered buffers.

Risks and test signals: direct raw reads do not call `iio_device_claim_direct()`, so test interaction with enabled buffer mode. Validate IRQ and polling paths, partial block-read handling, clear-IRQ failures, buffer disable wait for final sample, model-ID mismatch logging, regulator/reset sequencing, and systems with no IRQ.
