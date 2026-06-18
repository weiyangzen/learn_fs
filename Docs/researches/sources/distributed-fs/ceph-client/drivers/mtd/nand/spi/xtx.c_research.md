<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/xtx.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/xtx.c

Purpose: XTX SPI NAND support for XT26G/Q A and D families.

Important APIs/types/functions: Defines manufacturer ID `0x0b`, A-family and D-family ECC masks, common op variants, `xt26g0xa_ooblayout`, `xt26g0xa_ecc_get_status()`, `xt26xxxd_ooblayout`, `xt26xxxd_ecc_get_status()`, large device table, and `xtx_spinand_manufacturer`.

Control flow: Core matches opcode-address IDs, installs A- or D-family OOB/ECC callbacks, and uses quad-enable only for A-family entries that set `SPINAND_HAS_QE_BIT`. A-family ECC status uses bits 2-5 and returns exact 1-7 values where possible; D-family combines `STATUS_ECC_MASK` with high ECC bits to return 4-7 or 8 corrected.

State and persistence: No private runtime state. Table entries cover 2 KiB and 4 KiB page geometries, 64/128/256-byte OOB, and 1G/2G/4G capacities.

Dependencies/integration: Uses `linux/bitfield.h`, SPI NAND descriptor macros, and MTD OOB layout callbacks.

Risks: ECC masks differ from common SPI NAND status positions, so using the wrong table callback would misreport failures. `xt26g0xa_ooblayout_free()` reserves only byte 0 for BBM, not two bytes. D-family OOB layout treats half the OOB as ECC and half as free after two BBM bytes.

Test signals: Probe A and D family IDs, verify corrected-bit counts and `-EBADMSG` status, OOB layout for all OOB sizes, quad-enable for A parts only, and large-page 4 KiB variants under MTD read/write/erase.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/xtx.c -->
