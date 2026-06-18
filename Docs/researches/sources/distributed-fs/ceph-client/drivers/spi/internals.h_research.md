# sources/distributed-fs/ceph-client/drivers/spi/internals.h

## Purpose

`internals.h` is a private header for SPI core implementation files, explicitly intended for `spi.c` and `spi-mem.c` rather than controller drivers. It exposes queue flushing and DMA buffer mapping helpers that are shared inside the SPI core.

## Important APIs, types, and functions

- `spi_flush_queue(struct spi_controller *ctrl)` is declared for flushing queued controller work.
- `spi_map_buf()` and `spi_unmap_buf()` map or unmap a linear buffer into a scatter-gather table when `CONFIG_HAS_DMA` is enabled.
- Without DMA support, `spi_map_buf()` returns `-EINVAL` and `spi_unmap_buf()` is an empty inline.
- `spi_xfer_is_dma_mapped()` checks whether a transfer should be considered DMA mapped by combining `ctlr->can_dma()`, the SPI device and transfer, and the transfer's `tx_sg_mapped`/`rx_sg_mapped` flags.

## Control flow

This header does not execute by itself. It shapes compile-time behavior: DMA helpers are real declarations when the architecture has DMA support and stubs otherwise. SPI core code can call the same helper names while preserving no-DMA build coverage.

## State and persistence behavior

There is no state in the header. State affected by these helpers lives in `struct sg_table`, `struct spi_transfer`, and controller/device DMA mappings owned by caller code.

## Dependencies and integration points

The header includes `linux/device.h`, `linux/dma-direction.h`, `linux/scatterlist.h`, and `linux/spi/spi.h`. It is a SPI core internal contract and should not become a public controller-driver API.

## Risks and edge cases

- External use by controller drivers would couple them to SPI core internals.
- `spi_xfer_is_dma_mapped()` requires `ctlr->can_dma` to be non-NULL and true; mapped scatterlists alone are not enough.
- No-DMA builds intentionally fail `spi_map_buf()` with `-EINVAL`, so callers must handle that path.

## Test signals

Compile coverage with and without `CONFIG_HAS_DMA` is the key signal. SPI core DMA and PIO transfer tests should verify that mapped transfer flags are honored and no-DMA configurations still build.
