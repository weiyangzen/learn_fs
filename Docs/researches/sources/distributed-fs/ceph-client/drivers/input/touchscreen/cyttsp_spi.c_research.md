# sources/distributed-fs/ceph-client/drivers/input/touchscreen/cyttsp_spi.c

Purpose: `cyttsp_spi.c` is the SPI transport shim for the older Cypress TTSP core. It formats full-duplex SPI command frames, validates synchronization acknowledgements, and delegates device lifecycle and input reporting to `cyttsp_core.c`.

Important APIs, types, and functions: `cyttsp_spi_xfer()` is the central transport helper. It builds a four-byte header (`0x00`, `0xff`, register, op), appends write data when needed, performs one or two `spi_transfer`s, and validates `0x62 0x9d` at `CY_SPI_SYNC_BYTE`. `cyttsp_spi_read_block_data()` and `cyttsp_spi_write_block_data()` wrap it for the core bus ops. `cyttsp_spi_probe()` forces 8 bits per word and SPI mode 0, runs `spi_setup()`, calls `cyttsp_probe()` with a double buffer sized for TX and RX, and stores driver data.

Control flow: matching SPI devices for `cypress,cy8ctma340` or `cypress,cy8ctst341` configure the SPI controller, instantiate the shared core, and use exported core PM callbacks. During reads, the first transfer clocks out the command header and the second reads payload bytes; writes combine header and payload in one full-duplex transfer.

State and persistence: no local persistent state exists. The transport uses the core-owned flexible transfer buffer split into write and read halves for each operation.

Dependencies and integration points: it depends on SPI core APIs, the TTSP core bus contract, OF matching, and the input bus type `BUS_SPI`. It provides `MODULE_ALIAS("spi:cyttsp")`.

Risks: only 8-bit, mode-0 SPI is supported. `cyttsp_spi_xfer()` logs but continues after `spi_sync()` errors to allow ACK validation, so callers see `-EIO` on bad ACK rather than the original error in many cases. Register arguments are only passed as one byte in the SPI header even though the core API uses `u16`. Transfers over 128 data bytes are rejected.

Test signals: validate SPI setup, read/write ACK checking, bad operation handling, overlength rejection, shared core probe success, and suspend/resume via `cyttsp_pm_ops`.
