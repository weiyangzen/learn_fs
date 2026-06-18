# sources/distributed-fs/ceph-client/drivers/mtd/mtdpart.c

Purpose: MTD partitioning layer. It allocates partition `mtd_info` children, applies offset/size directives, enforces alignment-derived writeability, registers/unregisters partition devices recursively, and runs partition parsers from explicit lists, command line, or device tree.

Important APIs/types/functions: `allocate_partition()`, `mtd_add_partition()`, `mtd_del_partition()`, `add_mtd_partitions()`, `del_mtd_partitions()`, `parse_mtd_partitions()`, parser registry functions, `mtd_part_of_parse()`, `mtd_part_do_parse()`, and `mtd_get_device_size()`. It depends on `mtdcore.h`, parent/master MTD geometry, OF partition nodes, parser modules, `mtd_virt_concat_add()`, sysfs partition offset attribute, and bad/reserved block helpers.

Control flow: allocation copies parent properties, applies `MTDPART_OFS_APPEND`, `NXTBLK`, `RETAIN`, and `SIZ_FULL`, clamps out-of-range partitions, computes child erasesize from parent erase regions, forces misaligned writable partitions read-only, copies ECC settings, and counts bad/reserved blocks. Static or dynamic partition add links the child under the parent lock, registers it, adds sysfs offset, and parses subpartitions. Deletion recursively removes child partitions and devices. Parser flow tries requested parsers, with special OF handling that matches compatible parsers, populates child platform devices, and falls back to fixed partitions.

State and persistence: partition state is an MTD hierarchy with child offsets/sizes, flags, sysfs attributes, and parser-owned partition arrays. Persistent data is shared with parent storage; partitioning only changes the exposed address ranges.

Risks and test signals: alignment math controls write protection and must use master offsets correctly for nested partitions. Error unwinding can recursively delete already-added partitions. Tests should cover append/next-block/retain/full directives, truncation/out-of-range disabled partitions, variable erase regions, nested partitions, parser module loading, OF fixed-partition fallback, virtual concat withholding, and BLKPG add/delete paths.
