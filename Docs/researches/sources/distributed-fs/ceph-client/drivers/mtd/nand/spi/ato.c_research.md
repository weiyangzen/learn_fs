<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/ato.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/ato.c

Purpose: ATO SPI NAND manufacturer support for `ATO25D1GA`.

Important APIs/types/functions: Defines manufacturer ID `0x9b`, common read/write/update op variants, `ato25d1ga_ooblayout_ecc()`, `ato25d1ga_ooblayout_free()`, one `spinand_info`, and exported `ato_spinand_manufacturer`.

Control flow: The core matches READID method opcode-address ID `0x12`, sets 2 KiB page/64-byte OOB geometry and 1-bit per 512-byte ECC requirement, and installs the ATO OOB layout. There is no custom ECC status function, so common SPI NAND status bits are interpreted by `spinand_check_ecc_status()`.

State and persistence: No private state. OOB layout divides the 64-byte spare area into four 16-byte sections, with 8 ECC bytes per section and free bytes before ECC; section 0 reserves byte 0 for the bad-block marker.

Dependencies/integration: Integrated through `spinand_manufacturer` descriptor in `core.c`; uses `SPINAND_HAS_QE_BIT` for quad variants.

Risks: The first free OOB region reserves only one BBM byte, unlike drivers that reserve two. Any device variant with a different BBM convention or ECC status encoding would need a new descriptor/callback.

Test signals: Confirm ID match, OOB region enumeration for sections 0 through 3, MTD read/write with on-die ECC, raw OOB behavior, and quad-enable negotiation on controllers with/without 4-bit data support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/ato.c -->
