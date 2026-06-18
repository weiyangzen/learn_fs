# sources/distributed-fs/ceph-client/drivers/iio/humidity/hdc100x.c

Purpose: I2C IIO driver for TI HDC1000/HDC1008/HDC1010/HDC1050/HDC1080 temperature and humidity sensors. It supports direct raw reads, integration-time configuration, heater control, and triggered dual-channel buffering.

Important APIs/types/functions: `struct hdc100x_data` stores client, lock, cached config, per-channel integration time, and aligned scan buffer. `hdc100x_update_config()` writes and caches configuration. `hdc100x_set_it_time()` maps requested integration time to resolution bits. `hdc100x_get_measurement()` starts one channel conversion and reads a big-endian word. `hdc100x_read_raw()` and `hdc100x_write_raw()` expose raw, scale, offset, integration time, and heater raw. Buffer hooks set/clear acquisition mode; `hdc100x_trigger_handler()` performs combined temp+humidity read and pushes timestamped data.

Control flow: probe checks I2C functionality, allocates IIO, initializes default integration times and config, sets channels and scan masks, installs triggered buffer callbacks, and registers the device. Direct reads claim direct mode, lock, start a measurement, wait integration time plus margin, and read the value. Buffered reads set acquisition mode and perform a dual read starting at the temperature register.

State and persistence: `data->config` mirrors `HDC100X_REG_CONFIG`; `adc_int_us[]` caches resolution-derived delays. Heater and acquisition mode persist in hardware until changed. No regulator or runtime PM state is managed.

Dependencies and integration points: Uses SMBus word/byte and raw I2C receive, IIO sysfs constants, triggered buffers, OF compatibles for the HDC100x family, and ACPI id `TXNW1010`.

Risks: Probe ignores return values from initial `hdc100x_set_it_time()` and config update, so hardware could start with unexpected defaults. Direct mode locking prevents conflict with buffers, but heater status reads do not require direct claim. Combined buffer read assumes both channels are active via scan mask. I2C short reads are not explicitly checked for exact byte count.

Test signals: Verify integration-time available/write/read, heater raw control, direct temp/humidity scaling/offset, buffer enable acquisition mode, triggered dual samples, ACPI/OF binding, and I2C failure injection.
