# sources/distributed-fs/ceph-client/drivers/iio/proximity/vl53l1x-i2c.c

Purpose: I2C regmap IIO driver for ST VL53L1X time-of-flight distance sensors. It loads ST default configuration, calibrates and starts continuous autonomous ranging, exposes raw distance and scale, and optionally provides IRQ-triggered buffered samples.

Important APIs/types/functions: `struct vl53l1x_data` holds regmap, completion, optional XSHUT reset, current distance mode, GPIO polarity, and IRQ number. Helpers read/write big-endian 16/32-bit registers, clear/start/stop ranging, initialize firmware, set short/long distance mode, set timing budget, compute inter-measurement period from oscillator calibration, and read proximity.

Control flow: probe enables VDD, deasserts optional reset, waits for boot, runs `vl53l1x_chip_init()` including firmware-status poll, model ID read, config blob write, initial VHV calibration cycle, and VHV register changes. It then configures long mode, 50 ms timing budget and period, starts ranging for the device lifetime, registers a stop action, and optionally installs trigger/IRQ/buffer support. Direct reads wait for the next ready sample by IRQ or GPIO-status polling, validate range status, read distance, and clear IRQ.

State and persistence: continuous ranging is persistent runtime state after probe. `distance_mode` influences timing-budget programming. `gpio_polarity` determines ready detection. No user-visible mutable config is exposed. Ranging is stopped only by devm cleanup.

Dependencies/integration: uses 16-bit-address regmap with volatile/readable tables, regulators, reset controls, IIO triggers/buffers, IRQ, bitfield helpers, and the ST Ultra Lite Driver configuration values embedded as a static blob.

Risks and test signals: because hardware runs continuously, failed IRQ clears can affect later reads. Test boot timeout, model-ID mismatch tolerance, IRQ and polling ready paths, invalid range status returning `-EIO`, trigger buffer with invalid samples, cleanup stop action, reset-control absence fallback, and timing-budget/inter-measurement writes.
