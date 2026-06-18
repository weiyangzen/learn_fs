<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/dosilicon.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/dosilicon.c

Purpose: Dosilicon SPI NAND table for DS35Q1GA and DS35M1GA.

Important APIs/types/functions: Defines manufacturer ID `0xe5`, common cache op variants, `ds35xx_ooblayout_ecc()`, `ds35xx_ooblayout_free()`, `ds35xx_ooblayout`, two `spinand_info` entries, and `dosilicon_spinand_manufacturer`.

Control flow: Core READID opcode-dummy matches IDs `0x71` and `0x21`, selects supported cache ops, enables quad when needed, and uses generic SPI NAND ECC status interpretation with the Dosilicon OOB layout.

State and persistence: No private state. Both entries describe 2 KiB page, 64-byte OOB, 64 pages per block, 1024 blocks, and ECC requirement 4 bits per 512 bytes.

Dependencies/integration: Descriptor-only integration with SPI NAND core. OOB layout exposes four sections, each with 8 ECC bytes at offset `8 + section * 16`; free bytes reserve two BBM bytes in section 0 and use 8 bytes in later sections.

Risks: No custom ECC status callback means the generic status mask must match the chips. Section count and fixed OOB layout assume 64-byte OOB geometry.

Test signals: ID match for both parts, OOB layout section enumeration, quad path negotiation, ECC stats under corrected/uncorrectable reads, and compile coverage when manufacturer arrays change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/dosilicon.c -->
