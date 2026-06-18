<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/gigadevice.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/gigadevice.c

Purpose: GigaDevice SPI NAND manufacturer support across many GD5F families, with multiple OOB layouts, ECC status decoders, and continuous-read support for GM9 devices.

Important APIs/types/functions: Defines manufacturer ID `0xc8`, `struct gigadevice_priv`, multiple read-cache variant groups, `gd5fxgm9_get_eccsr()`, `gd5fxgm9_ecc_get_status()`, `gd5fxgm9_set_continuous_read()`, several OOB layout callbacks, status decoders for Q4XA/Q4UE/Q5XE/Q4UF families, the large `gigadevice_spinand_table`, and init/cleanup ops for private state.

Control flow: Core matches numerous opcode/address/dummy IDs, selects family-specific operation variants, installs the right ECC/OOB callbacks, and for GM9 allocates private state and provides a continuous-read config toggle. ECC status flow may use base status bits, secondary status register `0xf0`, or an ECC status register read command depending on family.

State and persistence: Private runtime state tracks continuous-read configuration for GM9. Persistent chip state includes normal-vs-continuous read config bits, status registers, OOB layout, and on-die ECC correction state.

Dependencies/integration: Uses SPI NAND core helpers, SPI-MEM direct ops for feature/ECCSR access, MTD OOB layout callbacks, and the core continuous-read path via `SPINAND_CONT_READ`.

Risks: Many families share similar names but have different status encodings and OOB layouts, so table misassignment can silently undercount bitflips or expose wrong OOB bytes. Continuous-read needs controller support for non-toggling CS and full-block dirmaps; core fallback handles `-EAGAIN` but performance and correctness should be tested on real controllers. ESMT also uses manufacturer ID `0xc8`, making match ordering important.

Test signals: Probe representative chips from each table cluster, validate each ECC decoder against datasheet statuses, test secondary/ECCSR register reads, run OOB layout enumeration for 64/128/256 OOB parts, exercise GM9 continuous read and fallback, and run multi-page MTD reads under UBI-like patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/gigadevice.c -->
