# sources/distributed-fs/ceph-client/drivers/iio/dac/ti-dac7612.c

Purpose: SPI IIO direct-mode output driver for the dual 12-bit TI DAC7612. It supports two output channels and optional driver control of the `LOADDACS` GPIO.

Important APIs/types/functions: `struct dac7612` stores the SPI device, optional `ti,loaddacs` GPIO, two cached channel values, mutex, and DMA-aligned two-byte transfer buffer. `dac7612_cmd_single()` formats a start bit, channel address, and 12-bit value, writes it over SPI, then toggles `LOADDACS` if present. `dac7612_read_raw()` and `dac7612_write_raw()` expose raw and scale IIO attributes.

Control flow: probe allocates the IIO device, obtains optional `ti,loaddacs`, initializes channels and mutex, writes zero to both channels, and registers with `devm_iio_device_register()`. Raw writes reject non-raw masks, out-of-range values, nonzero `val2`, and no-op cached values, then call the SPI/GPIO sequence under lock.

State/persistence: per-channel cache is the source for raw readback. Cache is updated inside `dac7612_cmd_single()` before the SPI transaction; a failed SPI write can leave software cache ahead of hardware. There is no regulator handling or nonvolatile state.

Dependencies/integration: depends on SPI, GPIO descriptor API, and IIO direct mode. Scale is hard-coded as integer `1`, so userspace gets a raw-code scale rather than a Vref-derived voltage scale.

Risks: optional GPIO semantics rely on `gpiod_set_value()` with possible NULL descriptor behavior; this should be confirmed against GPIO helper guarantees in the target kernel. Cache-before-write can hide failed hardware updates. The driver lacks a remove callback because resources are managed. Test signals include dual-channel addressing, initial zero writes, optional vs absent `LOADDACS`, raw bounds, cache behavior on SPI error, and OF compatibles `ti,dac7612`, `ti,dac7612u`, and `ti,dac7612ub`.
