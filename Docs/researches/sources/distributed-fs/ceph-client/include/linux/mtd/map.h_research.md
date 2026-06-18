# sources/distributed-fs/ceph-client/include/linux/mtd/map.h

## Purpose

Defines the central memory-map abstraction for parallel NOR/flash devices, including bank-width handling, `map_word` operations, inline MMIO accessors, and chip-driver registration.

## Important APIs, Types, and Functions

Important APIs include `struct map_info`, `struct mtd_chip_driver`, `map_word` helpers, `map_read()`, `map_write()`, `map_copy_from()`, `map_copy_to()`, `simple_map_init()`, `do_map_probe()`, `map_destroy()`, and chip-driver register/unregister calls.

Source-visible symbols include structs: `struct device_node;`, `struct module;`, `struct mtd_chip_driver;`, `struct map_info`, `struct device_node *device_node;`, `struct mtd_chip_driver *fldrv;`, `struct mtd_chip_driver`, `struct mtd_info *(*probe)(struct map_info *map);`, `struct module *module;`, `struct list_head list;`, `struct mtd_info *do_map_probe(const char *name, struct map_info *map);`; enums: none visible in this header; typedefs: `typedef union {`; prototypes: `void register_mtd_chip_driver(struct mtd_chip_driver *);`, `void unregister_mtd_chip_driver(struct mtd_chip_driver *);`, `void map_destroy(struct mtd_info *mtd);`, `extern void simple_map_init(struct map_info *);`; representative macros: `__LINUX_MTD_MAP_H__`, `map_bankwidth`, `map_bankwidth_is_1`, `map_bankwidth_is_large`, `map_words`, `MAX_MAP_BANKWIDTH`, `map_bankwidth_is_1`, `map_bankwidth_is_2`, `MAX_MAP_BANKWIDTH`, `map_bankwidth_is_2`, `map_bankwidth_is_4`, `MAX_MAP_BANKWIDTH`, `map_bankwidth_is_4`, `map_calc_words`, `map_bankwidth_is_8`, `MAX_MAP_BANKWIDTH`.

## Control Flow

Map drivers fill physical/virtual/cached address fields, bank width, optional complex accessors, cache invalidation, and VPP controls. Probe code calls `do_map_probe()`, which invokes a chip driver and returns an `mtd_info`; chip drivers then use `map_read/write/copy` and `map_word_*` helpers for bus-width-neutral command/data cycles.

## State and Persistence Behavior

Runtime state includes map identity, size, physical and virtual addresses, optional cached alias, byte-swap flag, bank width, PFOW base, private words, device tree node, and flash-driver private data. No flash metadata is persisted by this header.

## Dependencies and Integration Points

It depends on Linux I/O, unaligned access, memory barriers, and MTD chip drivers. It is the integration point for CFI, JEDEC, physmap, LPDDR/PFOW, HyperFlash, and other mapped flash drivers.

Direct includes observed in the source are: `#include <linux/bug.h>`, `#include <linux/io.h>`, `#include <linux/ioport.h>`, `#include <linux/string.h>`, `#include <linux/types.h>`, `#include <linux/unaligned.h>`, `#include <asm/barrier.h>`.

## Risks and Edge Cases

Bank-width configuration controls memory access size and stack layout for wide maps. Missing barriers, wrong cached alias invalidation, or unsupported bank widths can corrupt command sequences or stale reads.

## Test Signals

Compile every configured bank width, probe simple and complex mappings, test `map_word_load_partial()` on endian variants, verify VPP reference behavior, and exercise cached/uncached copy paths.

Source read signal: 466 lines, 13053 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
