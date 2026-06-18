# sources/distributed-fs/ceph-client/drivers/mtd/devices/mtd_dataflash.c

Purpose: SPI MTD driver for Atmel/Microchip AT45 DataFlash chips. It handles legacy status-bit identification and JEDEC ID probing, registers DataFlash as an MTD device, and optionally exposes one-time-programmable security regions.

Important APIs/types/functions: `struct dataflash` holds command scratch bytes, page geometry, mutex, SPI device, and embedded `mtd_info`. MTD callbacks are `dataflash_erase()`, `dataflash_read()`, and `dataflash_write()`. Probe helpers include `dataflash_status()`, `dataflash_waitready()`, `jedec_probe()`, `jedec_lookup()`, `add_dataflash_otp()`, and `dataflash_probe()`. OTP callbacks are compiled under `CONFIG_MTD_DATAFLASH_OTP`.

Control flow: probe first tries JEDEC `OP_READ_ID`; if unsupported, it falls back to status-byte density decoding. Registration sets page size, page offset, total pages, MTD type `MTD_DATAFLASH`, erase/write sizes, parent device, OF node, and optional platform partitions. Reads build an 8-byte continuous-read command and one RX transfer. Writes loop page by page, optionally transfer a partial page into buffer 1, program via buffer 1, wait ready, and optionally compare. Erase validates page alignment and uses block erase for aligned 8-page spans.

State and persistence: flash contents and OTP bytes are persistent. Runtime state is per-device geometry, a mutex serializing shared command buffer and SPI transactions, and optional OTP function pointers. There is no wear state or bad-block metadata in this driver.

Dependencies/integration: integrates with the SPI core (`spi_driver`, `spi_sync`, `spi_write_then_read`), platform data partitions, OF compatibles `atmel,at45`/`atmel,dataflash`, and MTD partition registration.

Risks: comments note incomplete write error handling and no erase retry/fail-address handling. `dataflash_write()` increments `*retlen` without clearing it, depending on MTD core convention. Partial-page writes modify internal SRAM buffer 1. OTP write support is revision-sensitive.

Test signals: probe logs device name/page size; JEDEC and legacy chips should both register; page-aligned erase, cross-page writes, optional write-verify failures, OTP read/write bounds, and remove/unregister paths are important coverage.
