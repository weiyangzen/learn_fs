<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/macronix.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/macronix.c

Purpose: Macronix SPI NAND support for MX31/MX35 LF/UF families, including custom ECC status reads, continuous-read toggling, read-retry modes, and manufacturer initialization.

Important APIs/types/functions: Defines manufacturer ID `0xc2`, `struct macronix_priv`, `macronix_get_eccsr()`, `macronix_ecc_get_status()`, `macronix_set_cont_read()`, `macronix_set_read_retry()`, `macronix_spinand_init()`, cleanup, one OOB layout, and a large `macronix_spinand_table`.

Control flow: Core matches device IDs, selects cache op variants, and installs per-chip ECC/OOB callbacks plus optional `SPINAND_CONT_READ` and `SPINAND_READ_RETRY`. Macronix status handling reads ECCSR when threshold status is reported, extracting last-page and accumulated-page bitflip counts. Init allocates private data and may set bitflip threshold configuration for selected devices; cleanup frees it.

State and persistence: Private state records read-retry/continuous-read related data. Persistent chip state includes continuous-read config bit, read-retry feature register `0x70`, and bitflip threshold register `REG_CFG_BFT`.

Dependencies/integration: Uses SPI NAND exported register helpers and SPI-MEM ops, integrates with core continuous-read and read-retry loops, and uses MTD OOB layout callbacks.

Risks: Read-retry and ECCSR interpretation directly affect data-retention recovery and ECC stats; incorrect mode reset after retry could leave the chip in a non-default read mode. Continuous-read has the same CS/dirmap risks as GigaDevice. Threshold programming in init must be compatible with every table entry that receives it.

Test signals: Validate all IDs, ECCSR reads on threshold statuses, read-retry loop recovery and reset to mode 0, continuous-read enable/disable around MTD reads, bitflip threshold register programming, OOB availability, and suspend/resume returning to usable config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/macronix.c -->
