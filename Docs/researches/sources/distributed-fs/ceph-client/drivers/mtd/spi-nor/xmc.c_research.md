# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/xmc.c

## Purpose
Registers XMC (Wuhan Xinxin Semiconductor Manufacturing Corp.) SPI NOR parts with the generic SPI NOR core.

## Important APIs, Types, and Functions
The only exported object is `spi_nor_xmc`. It references `xmc_nor_parts[]`, which contains `XM25QH64A` and `XM25QH128A` entries with JEDEC IDs, sizes, 4 KiB sectors, dual-read, and quad-read no-SFDP capability flags.

## Control Flow
The SPI NOR core matches the manufacturer and JEDEC ID, then uses the static part metadata if SFDP data is missing or insufficient. There are no custom fixups, callbacks, or register operations.

## State and Persistence
No runtime or persistent state is changed by this file. All behavior is declarative through the flash table.

## Dependencies and Integration Points
It depends on `linux/mtd/spi-nor.h` and the local SPI NOR core definitions. Integration is via the manufacturer registry in the SPI NOR subsystem.

## Risks
The risk is stale or incomplete part metadata. If newer XMC variants share IDs or require fixups, this table alone cannot handle them.

## Test Signals
Probe both listed XMC parts and verify capacity, erase size, dual read, quad read, and fallback operation on systems without usable SFDP.
