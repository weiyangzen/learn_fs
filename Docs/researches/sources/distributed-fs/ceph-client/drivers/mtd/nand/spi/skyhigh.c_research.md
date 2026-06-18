<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/skyhigh.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/skyhigh.c

Purpose: SkyHigh SPI NAND support for S35ML01G/02G/04G devices with hidden ECC and no raw access.

Important APIs/types/functions: Defines manufacturer ID `0x01`, SkyHigh ECC status values, `skyhigh_spinand_ooblayout`, `skyhigh_spinand_ecc_get_status()`, `skyhigh_spinand_init()`, table entries, and `skyhigh_spinand_manufacturer`.

Control flow: Core matches opcode-dummy IDs, installs hidden-ECC OOB layout, sets `SPINAND_NO_RAW_ACCESS`, and uses the custom ECC status mapper. Manufacturer init writes `SKYHIGH_CONFIG_PROTECT_EN` to `REG_BLOCK_LOCK` before the core unlocks all blocks.

State and persistence: Runtime state is descriptor-only. Persistent config includes block-lock/config-protect bits and hidden ECC metadata. The exposed OOB free area starts after two BBM bytes and runs to the end of visible OOB.

Dependencies/integration: Uses SPI NAND register helper in manufacturer init, and depends on core fallback from raw bad-block marker reads to place-OOB mode due to `SPINAND_NO_RAW_ACCESS`.

Risks: Raw access is explicitly unsupported, so tools/filesystems requiring raw OOB or ECC bytes may fail. Bad-block operations rely on the core fallback path. The ECC requirement uses 6 bits per 32 bytes, an unusual granularity that must be propagated correctly to MTD.

Test signals: Probe all capacities, verify manufacturer init writes block-lock protect enable, test raw-mode rejection and bad-block fallback, ECC status mapping for 1-2/3-6/uncorrectable, OOB free bytes, and standard MTD read/write/erase.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/skyhigh.c -->
