# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/everspin.c

## Purpose

`everspin.c` adds Everspin MRAM/FRAM-like SPI parts to the SPI NOR framework. These devices are non-erase memories, so the table and fixup adapt the NOR core to operate without erase and without fast-read support.

## Important APIs, types, and functions

`everspin_nor_parts[]` lists `mr25h128`, `mr25h256`, `mr25h10`, and `mr25h40` with sizes, sector sizes, two-byte addressing for the smaller parts, and `SPI_NOR_NO_ERASE`. `everspin_nor_default_init()` clears `SNOR_HWCAPS_READ_FAST`, and `everspin_nor_fixups` wires that hook into the exported `spi_nor_everspin` manufacturer.

## Control flow

These parts are typically matched by modalias/name rather than JEDEC ID. During parameter initialization, the manufacturer default fixup removes fast read before capability selection. Later, `spi_nor_set_mtd_info()` sees `SPI_NOR_NO_ERASE`, sets `MTD_NO_ERASE`, and does not install `_erase`.

## State and persistence behavior

No local mutable state exists. The file changes runtime behavior so writes are treated like direct programming of non-erase memory and no erase persistence model is exposed.

## Dependencies and integration points

It depends on the core's name matching, default fixup hook, MTD `MTD_NO_ERASE` handling, and static SPI device IDs in `core.c` for Everspin names.

## Risks

Treating MRAM as NOR-compatible is intentionally special. If an Everspin part actually requires different write semantics, the generic page-program path may be wrong. Removing fast read is important because the devices do not support the opcode; missing this would break reads after setup.

## Test signals

Bind by each supported name, confirm MTD has `MTD_NO_ERASE`, perform read/write without erase, verify two-byte addressing on 16K/32K parts, and confirm selected read opcode is normal read rather than fast read.
