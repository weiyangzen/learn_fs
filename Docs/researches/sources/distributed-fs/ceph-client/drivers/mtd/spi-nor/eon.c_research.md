# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/eon.c

## Purpose

`eon.c` registers Eon SPI NOR parts with the core framework. It is a manufacturer table only: it lists JEDEC IDs, legacy names, sizes, and non-SFDP capability hints for EN25 devices.

## Important APIs, types, and functions

The file defines `eon_nor_parts[]` and exports `const struct spi_nor_manufacturer spi_nor_eon`. Entries use `SNOR_ID()` and `flash_info` fields such as `.name`, `.size`, and `.no_sfdp_flags`.

## Control flow

The core's `manufacturers[]` includes `spi_nor_eon`. During detection, `spi_nor_match_id()` compares read JEDEC bytes against `eon_nor_parts[]`. If matched, the selected entry feeds default and non-SFDP parameter initialization.

## State and persistence behavior

The file has no mutable state. It contributes static probe metadata. For legacy parts with `.size` set, the core may avoid mandatory SFDP parsing and use `.no_sfdp_flags` to initialize 4K erase and dual-read support.

## Dependencies and integration points

It depends on public `linux/mtd/spi-nor.h` constants and internal `core.h`. It integrates only through the `spi_nor_eon` manufacturer object.

## Risks

Incorrect ID or size entries cause wrong MTD size or wrong device binding. Missing `SECT_4K` or read-mode hints can reduce functionality on parts without usable SFDP; over-declaring dual-read can select operations unsupported by old devices.

## Test signals

Probe known EN25 parts, compare MTD size and erase size with datasheets, verify JEDEC matching for entries with IDs, and run read/erase/write tests on devices using `SECT_4K` or dual-read hints.
