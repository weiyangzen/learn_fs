# Research: sources/distributed-fs/ceph-client/drivers/iio/imu/adis_buffer.c

Purpose: shared ADIS16xxx IIO buffer helper. It builds SPI transfer messages for either burst-mode or per-channel register reads, provides a generic trigger handler, and exposes `devm_adis_setup_buffer_and_trigger_with_attrs()` for ADIS drivers.

Important APIs, types, and functions: `adis_update_scan_mode()` is exported in namespace `IIO_ADISLIB` and rebuilds `adis->xfer`, `adis->buffer`, and `adis->msg` for the active scan mask. `adis_update_scan_mode_burst()` builds a two-transfer burst request/read sequence. `adis_paging_trigger_handler()` forces paged devices back to page 0 before capture. `adis_trigger_handler()` is the default poll function. `devm_adis_setup_buffer_and_trigger_with_attrs()` wraps IIO triggered-buffer setup, optional ADIS trigger probing, and devm cleanup.

Control flow: each scan-mode update frees old transfer state, allocates new transfer and buffer memory, then either prepares a burst read or constructs one delayed 16-bit SPI transfer per enabled scan element plus a pipeline transfer. For non-burst 32-bit channels, it emits high-register then low-register reads. Trigger handling performs paging fixup if needed, runs `spi_sync()`, pushes the raw ADIS buffer with timestamp, and notifies trigger completion.

State and persistence: dynamically owns `adis->xfer`, `adis->buffer`, and `adis->msg` until the next scan-mode update or devm cleanup. It also mutates `adis->current_page` for paged devices. No persistent hardware settings are configured here except SPI read sequencing.

Dependencies and integration: used by ADIS IMU drivers through `linux/iio/imu/adis.h`; depends on SPI, IIO triggered buffer, trigger consumer, and `devm_adis_probe_trigger()` from `adis_trigger.c`.

Risks: allocation failures must leave `adis->xfer` and `adis->buffer` consistent. Active scan ordering and storage width determine wire command order; misdeclared channel metadata corrupts buffers. Burst callers that mutate `burst_extra_len` must keep transfer lengths synchronized. Paged devices must not capture from a nonzero page.

Test signals: exercise burst and non-burst scan-mode rebuilds, 16-bit and 32-bit channels, allocation-failure unwinds, repeated scan-mask changes, paged-device capture, default handler errors, and cleanup after managed device removal.
