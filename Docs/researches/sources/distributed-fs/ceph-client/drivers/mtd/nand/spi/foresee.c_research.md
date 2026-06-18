<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/foresee.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/foresee.c

Purpose: FORESEE SPI NAND support for F35SQA001G, F35SQA002G, and F35SQB002G.

Important APIs/types/functions: Defines manufacturer ID `0xcd`, common operation variants, `f35sqa002g_ooblayout`, `f35sqa002g_ecc_get_status()`, `f35sqb002g_ecc_get_status()`, chip table, and `foresee_spinand_manufacturer`.

Control flow: Core matches opcode-dummy two-byte IDs, enables quad-capable variants, installs a layout with hidden ECC/no ECC region and free OOB bytes after two BBM bytes, and maps ECC status. SQA devices use generic two-bit `STATUS_ECC_MASK` semantics but return full ECC strength on any corrected status. SQB maps a wider range where status values 2 through 6 mean 4-8 corrected bitflips.

State and persistence: No private state. Geometry entries cover 1G/2G devices with 64- or 128-byte OOB and ECC requirements of 1 or 8 bits per 512 bytes.

Dependencies/integration: Descriptor-only SPI NAND integration with MTD OOB and ECC callbacks.

Risks: `f35sqa002g_ecc_get_status()` treats any non-no-bitflips/non-corrected state as `-EBADMSG`, so reserved status values become failures. Hidden ECC layout means raw/OOB users must not expect visible ECC bytes.

Test signals: Verify ID matching for duplicate-byte IDs, `mtd->oobavail`, corrected/failed ECC status values for SQA and SQB, and quad read/write fallback on controllers without quad support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/foresee.c -->
