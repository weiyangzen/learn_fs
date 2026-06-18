# sources/distributed-fs/ceph-client/drivers/mtd/parsers/sharpslpart.c

Purpose: Sharp SL NAND partition parser for devices whose partition table is stored behind the Sharp FTL logical-address mapping.

Important APIs/types/functions: `sharpsl_parse_mtd_partitions()` is the parser entry. `struct sharpsl_ftl` holds `logmax` and a logical-to-physical table. `sharpsl_nand_check_ooblayout()`, `sharpsl_nand_get_logical_num()`, `sharpsl_nand_init_ftl()`, and `sharpsl_nand_read_laddr()` reconstruct enough FTL mapping to read the partition info sectors. `struct sharpsl_nand_partinfo` stores start/end/magic.

Control flow: it verifies OOB bytes 8-15 are free for FTL metadata, scans the first 7 MiB worth of physical blocks, skips bad blocks, reads OOB, decodes logical block numbers from three redundant copies with parity, and builds `log2phy`. It tries partition info at logical addresses 0x60000 and 0x64000, validates BOOT/FSRO/FSRW magics and monotonically increasing boundaries, fixes the final end to the actual MTD size, then creates `smf`, `root`, and `home` partitions.

State and persistence: persistent state is NAND OOB FTL metadata and partition info records. Runtime mapping is temporary and freed before returning. No flash writes occur, but bad block/OOB behavior directly affects discoverability.

Dependencies and integration: depends on MTD OOB layout APIs, raw OOB reads, bad-block checks, bit operations, and historical Sharp SL media layout constants. Risks include fixed 7 MiB FTL area, ignoring duplicate logical mappings after first hit, inability to read across logical block boundaries, strict OOB layout requirements, and hardcoded three-part output. Test signals include OOB layout coverage, redundant logical-number corruption, bad blocks, invalid first table with valid second table, boundary sanity failures, and older 64 MiB fixup behavior.
