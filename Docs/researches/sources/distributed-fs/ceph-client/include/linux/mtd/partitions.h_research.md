# sources/distributed-fs/ceph-client/include/linux/mtd/partitions.h

## Purpose

Defines MTD partition descriptors, parser interfaces, parser registration, and parser data used to split master MTD devices into child partitions.

## Important APIs, Types, and Functions

Key types are `struct mtd_partition`, `struct mtd_part_parser_data`, and `struct mtd_part_parser`; functions include parser register/unregister helpers, parser lookup/put, and partition parse/delete helpers.

Source-visible symbols include structs: `struct mtd_partition`, `struct device_node *of_node;`, `struct mtd_info;`, `struct device_node;`, `struct mtd_part_parser_data`, `struct mtd_part_parser`, `struct list_head list;`, `struct module *owner;`, `struct mtd_part_parser_data *);`, `struct mtd_partitions`, `struct module *owner);`; enums: none visible in this header; typedefs: none visible in this header; prototypes: `extern void deregister_mtd_parser(struct mtd_part_parser *parser);`, `int mtd_del_partition(struct mtd_info *master, int partno);`, `uint64_t mtd_get_device_size(const struct mtd_info *mtd);`; representative macros: `MTD_PARTITIONS_H`, `MTDPART_OFS_RETAIN`, `MTDPART_OFS_NXTBLK`, `MTDPART_OFS_APPEND`, `MTDPART_SIZ_FULL`, `register_mtd_parser`, `module_mtd_part_parser`.

## Control Flow

MTD registration can pass fixed partitions and parser names. Parser modules inspect device contents or DT/platform data, return `mtd_partition` arrays, and the core creates child `mtd_info` partitions with offsets, sizes, masks, and parser metadata.

## State and Persistence Behavior

Partition definitions are static or parser-generated metadata. Runtime partition state lives in child `mtd_info.part` fields and parser reference counts.

## Dependencies and Integration Points

It depends on MTD core, module/device tree support, and parser implementations such as cmdline, fixed-partitions, RedBoot, or platform-specific parsers.

Direct includes observed in the source are: `#include <linux/types.h>`.

## Risks and Edge Cases

Incorrect offsets/sizes can expose overlapping partitions or hide data. Parser lifetime and dynamically allocated partition arrays must be managed consistently.

## Test Signals

Fixed partition registration, parser priority/order, overlap/bounds rejection, DT label propagation, and parser module refcount cleanup.

Source read signal: 115 lines, 3946 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
