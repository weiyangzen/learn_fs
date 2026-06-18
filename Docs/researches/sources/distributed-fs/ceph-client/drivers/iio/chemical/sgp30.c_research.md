# sources/distributed-fs/ceph-client/drivers/iio/chemical/sgp30.c

Purpose: I2C IIO driver for Sensirion SGP30 and SGPC3 gas sensors. It exposes processed IAQ values and raw gas-signal channels, verifies feature-set compatibility, and maintains a background IAQ measurement thread to satisfy the sensors' periodic-measurement requirements.

Important APIs, types, and functions: `struct sgp_data` holds client, mutex, IAQ kthread, feature set, command choices, measurement interval, and raw/IAQ buffers. `sgp_read_cmd()` sends a big-endian command, waits the specified duration, receives CRC-protected words, and calls `sgp_verify_buffer()`. `sgp_measure_iaq()` updates `iaq_buffer` and marks default versus valid IAQ readings after the initialization warm-up window. `sgp_iaq_threadfn()` issues IAQ init once, then repeatedly measures at the product interval. `sgp_read_raw()` exposes processed TVOC/eCO2 when the IAQ buffer is valid and raw ethanol/H2 signals. `sgp_check_compat()` decodes the feature-set product/generation/version fields and rejects engineering or unsupported devices. `sgp_probe()` reads feature set, initializes product-specific channels and commands, registers IIO, and starts the kthread.

Control flow: probe determines product data from OF/I2C match, reads feature set, validates it, registers the device, then starts the IAQ polling thread. Direct user reads use the most recent thread-produced IAQ buffer for processed values; raw SGP30 gas signals trigger immediate commands while SGPC3 ethanol reuses IAQ data.

State and persistence: IAQ buffer state is `EMPTY`, `DEFAULT_VALS`, or `VALID`; warm-up default readings return `-EBUSY`. No baseline or humidity compensation persistence is implemented, matching the file TODO.

Dependencies and integration: depends on I2C, CRC8, kthread, mutex, jiffies timing, and IIO direct mode. Compatibles are `sensirion,sgp30` and `sensirion,sgpc3`.

Risks and test signals: `kthread_run()` result is not checked with `IS_ERR`, so failed thread creation could leave no IAQ updates. Warm-up timing, command endian handling, and CRC validation are correctness-critical. Tests should cover feature-set rejection, default-value `-EBUSY`, thread shutdown in remove, CRC mismatch, raw-channel command selection, and product-specific channel layout.
