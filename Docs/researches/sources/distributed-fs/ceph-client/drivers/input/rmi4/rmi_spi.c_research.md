# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_spi.c

## Purpose

`rmi_spi.c` implements the SPI transport adapter for RMI4 devices. It converts RMI read/write requests into SPI messages, handles page selection for RMI addressing, supports optional per-byte transfer delays, and registers an RMI transport device.

## Important APIs, Types, and Functions

`enum rmi_spi_op` and `struct rmi_spi_cmd` describe SPI command variants. `struct rmi_spi_xport` stores the transport, SPI device, page state, DMA-capable TX/RX buffers, and transfer arrays. `rmi_spi_manage_pools()` sizes buffers and transfer pools. `rmi_spi_xfer()` builds and submits SPI messages. `rmi_set_page()`, `rmi_spi_write_block()`, and `rmi_spi_read_block()` implement the RMI transport. Probe and PM hooks register and suspend/resume the transport.

## Control Flow

Probe rejects half-duplex controllers, allocates state, reads OF or platform SPI timing/mode data, applies bits-per-word/mode, calls `spi_setup()`, initializes transport ops, allocates default pools, sets page zero, and registers the transport with devm cleanup. Reads and writes lock the page mutex, change pages when needed, then call `rmi_spi_xfer()` with two-byte legacy read/write commands. `rmi_spi_xfer()` allocates larger pools as needed, prepares command bytes and data bytes, optionally splits transfers into one-byte entries with configured delays, calls `spi_sync()`, and copies received data out.

## State and Persistence Behavior

The transport persists current page, reusable DMA-capable buffers, transfer arrays, and platform timing/mode settings. The RMI transport registration persists until devm cleanup. No device configuration is persistent beyond page-select state and normal RMI register operations.

## Dependencies and Integration Points

The file depends on SPI core, OF matching/properties, RMI transport registration, RMI PM helpers, and platform `rmi_device_platform_data_spi`. It provides the backend used by all RMI function drivers over SPI.

## Risks and Edge Cases

`rmi_set_page()` updates `rmi_spi->page` when `ret` is nonzero, which appears inverted and can desynchronize page tracking after failed page writes. `RMI_SPI_PAGE(addr)` masks with `0x80`, not the full high byte, so only a limited page bit is tracked. Transfer length is capped at 255 bytes; higher layers must chunk larger accesses. V2 command opcodes are enumerated but not implemented for reads. Runtime suspend returns zero even when driver suspend fails.

## Test Signals

Tests should include page switching, failed page-select writes, max-length transfers and over-limit errors, per-byte read/write delay modes, OF and platform-data probe, half-duplex rejection, system/runtime PM, SPI short/error injection, and full RMI enumeration over SPI.
