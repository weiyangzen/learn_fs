<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/alliancememory.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/alliancememory.c

Purpose: AllianceMemory SPI NAND manufacturer table and per-device ECC/OOB interpretation.

Important APIs/types/functions: Defines manufacturer ID `0x52`, read/write/update op variants, `am_get_eccsize()`, `am_ooblayout_ecc()`, `am_ooblayout_free()`, `am_ecc_get_status()`, one `spinand_info` entry for `AS5F34G04SND`, and exported `alliancememory_spinand_manufacturer`.

Control flow: During ID match, `core.c` selects the fastest supported cache operations, installs `am_ooblayout`, and uses `am_ecc_get_status()` after page reads. ECC status maps no errors to 0, corrected states to 3/7 or 4/8 depending on OOB size, and errored state to `-EBADMSG`.

State and persistence: No private runtime allocation. Persistent media characteristics are encoded as `NAND_MEMORG(1, 2048, 128, 64, 4096, 80, 1, 1, 1)` and `NAND_ECCREQ(4, 512)`.

Dependencies/integration: Uses SPI NAND core descriptor macros and MTD OOB layout callbacks. `SPINAND_HAS_QE_BIT` lets the core enable quad I/O when selected operation variants need it.

Risks: `am_get_eccsize()` only accepts OOB sizes 64, 128, and 256; unsupported geometry returns `-EINVAL`. The free OOB region reserves two BBM bytes, but the source comments note uncertainty about exact bad-block marker usage and unprotected chunking.

Test signals: Probe `AS5F34G04SND`, verify quad read/write path if controller supports it, inspect `mtd->oobavail`, run raw and auto-OOB read/write tests, and inject status values to validate corrected/failed ECC accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/alliancememory.c -->
