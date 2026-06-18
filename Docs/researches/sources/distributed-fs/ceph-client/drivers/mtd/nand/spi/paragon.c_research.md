<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/paragon.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/paragon.c

Purpose: Paragon SPI NAND support for PN26G01A and PN26G02A.

Important APIs/types/functions: Defines manufacturer ID `0xa1`, cache operation variants, `pn26g0xa_ooblayout_ecc()`, `pn26g0xa_ooblayout_free()`, `pn26g0xa_ecc_get_status()`, chip table, and `paragon_spinand_manufacturer`.

Control flow: Core matches opcode-dummy IDs `0xe1` and `0xe2`, installs a 128-byte OOB layout, and maps ECC status to no errors, 1-7 corrected, 8 corrected, or `-EBADMSG`. The free layout exposes small user bytes in sections 0-3 plus a large section 4 at offsets 64-127.

State and persistence: No private runtime state. Persistent geometry is 1G/2G with 2 KiB page, 128-byte OOB, and ECC requirement 8 bits per 512.

Dependencies/integration: Descriptor-based SPI NAND integration with MTD OOB callbacks.

Risks: Manufacturer ID overlaps FMSH. OOB section 4 exposes a large second half of OOB as free; users must ensure this is compatible with actual ECC placement on both listed chips.

Test signals: ID match despite ID overlap, OOB section enumeration through `mtd_ooblayout_*`, ECC status injection, full read/write/erase, and controller support for selected cache op variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/paragon.c -->
