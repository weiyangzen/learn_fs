<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/afs.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/parsers/afs.c

Purpose: ARM Firmware Suite MTD partition parser. It scans erase blocks for AFS v1/v2 footers and creates MTD partitions for discovered firmware images.

Important APIs/types/functions: Defines v1 footer/image-info structures, `word_sum()` and `word_sum_v2()` checksums, `afs_is_v1()`, `afs_is_v2()`, `afs_parse_v1_partition()`, `afs_parse_v2_partition()`, `parse_afs_partitions()`, OF match `"arm,arm-firmware-suite"`, and `afs_parser`.

Control flow: The parser first scans every erase block and counts blocks with v1 or v2 footer magic. It allocates a partition array, scans again, and parses each matching block. V1 reads the footer at the end of the erase block, checks checksum, skips SIB type 2, masks image pointers to flash size, reads image info, validates a NUL-terminated name, and creates a partition rounded to eraseblock size. V2 reads a 12-word footer and 36-word image info, validates checksum with 32-bit or 64-bit padding, then creates partitions for described regions.

State and persistence: Runtime allocation is the partition array and duplicated partition names returned through `pparts`. Persistent state is only the AFS footer/image metadata in flash; the parser does not modify media.

Dependencies/integration: Uses MTD read APIs and `struct mtd_part_parser`, registers with `module_mtd_part_parser()`, and can be selected by OF-compatible flash nodes.

Risks: V2 parsing loops over `region_count` but writes repeatedly into the single `part` slot passed by caller, so multiple-region images may not produce multiple array entries as intended. V1 name validation checks `if (i > sizeof(iis.name))`, which does not reject the no-NUL case when `i == sizeof(iis.name)`. Address masking assumes power-of-two MTD size behavior. Parser trusts several v2 indexes after checksum.

Test signals: Images with valid/invalid v1 and v2 footer magic, checksum failures, SIB hiding, missing NUL terminator, multiple v2 regions, partial MTD reads, non-power-of-two sizes, OF parser selection, and cleanup of duplicated names on parse failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/afs.c -->
