# sources/distributed-fs/ceph-client/drivers/iio/accel/stk8ba50.c

Purpose: I2C IIO driver for the Sensortek STK8BA50 three-axis 10-bit accelerometer.

Important APIs/types/functions: `struct stk8ba50_data` stores the I2C client, mutex, range table index, sample-rate index, optional trigger, trigger state, and aligned scan buffer. `stk8ba50_set_power()` toggles suspend/normal mode. `stk8ba50_read_raw()` and `stk8ba50_write_raw()` implement direct raw reads, scale selection, and sample-rate selection. `stk8ba50_trigger_handler()` handles buffered capture, while probe/remove and PM callbacks manage lifecycle.

Control flow: probe allocates and initializes the IIO device, resets the chip, initializes default +/-2 g and 1792 Hz cached settings, enables and maps data-ready interrupts, optionally registers an IRQ-backed trigger, sets up the triggered buffer, and registers the IIO device. Direct raw reads power the chip on, read a word from the axis register, shift/sign-extend the 10-bit sample, and suspend the chip. Buffer enable powers normal mode and buffer disable suspends it. Triggered capture bulk-reads six bytes for all axes or reads selected axis words.

State and persistence behavior: range and sample-rate caches mirror the latest successful register writes. The power bit is toggled for direct reads, buffers, suspend, resume, and cleanup. Trigger registration is manual rather than devm for `iio_trigger_register()`, so remove and error paths unregister it explicitly.

Dependencies and integration points: depends on I2C SMBus word/block access, IIO buffers/triggers, optional ACPI id `STK8BA50`, I2C modalias `stk8ba50`, and PM sleep callbacks.

Risks: the channel macro has a suspicious comma after `BIT(IIO_CHAN_INFO_SCALE)` before `BIT(IIO_CHAN_INFO_SAMP_FREQ)`, so sampling-frequency mask exposure should be checked carefully. Probe enables data-ready interrupts even when no IRQ is present. `stk8ba50_set_power()` uses a boolean-like argument with inverted naming (`STK8BA50_MODE_NORMAL` is zero and clears the power bit). Direct-read errors are collapsed to `-EINVAL`, losing original I2C error codes.

Test signals: compile with warnings enabled, inspect IIO channel masks for sampling-frequency visibility, probe over I2C and ACPI, validate reset and interrupt register writes, raw read sign extension, scale/rate writes, full and partial buffered scans, trigger enable/disable, and suspend/resume power-bit behavior.
