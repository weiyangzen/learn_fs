<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/abp2030pa_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/abp2030pa_spi.c

Purpose: SPI transport adapter for the Honeywell ABP2 common IIO core.

Important APIs, types, and functions: `abp2_spi_xfer()` bounds `nbytes`, puts the command in `tx_buf[0]`, and performs a full-duplex `spi_sync_transfer()` using the core RX/TX buffers. `abp2_spi_probe()` delegates to `abp2_common_probe()`. The OF and SPI ID tables both expose `honeywell,abp2030pa`/`abp2030pa`.

Control flow: all common measurement sequencing is owned by `abp2030pa.c`; this file supplies identical `read` and `write` callbacks because SPI command and response handling are full-duplex transfers.

State and persistence: no transport-private runtime state is stored. The SPI device is recovered from `data->dev`; buffers live in the common state.

Dependencies and integration points: depends on SPI core, OF/SPI ID matching, and ABP2 common-probe namespace import. It relies on board-level SPI mode/chip-select configuration.

Risks: `tx_buf` bytes after the command are not cleared in this function, so transfer padding can contain previous contents. There is no explicit SPI mode, bits-per-word, or max-speed validation. Full-duplex write semantics may differ from I2C command framing and should be checked against the datasheet for each command length.

Test signals: probe on SPI devices, transfer-size overflow, full-duplex command capture, bad status handling through the core, and module namespace/modpost validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/abp2030pa_spi.c -->
