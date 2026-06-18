# sources/distributed-fs/ceph-client/include/linux/mtd/onenand.h

## Purpose

Defines the OneNAND chip model, platform data, scan/release APIs, BufferRAM bookkeeping, option flags, and helper macros for Samsung/Numonyx OneNAND devices.

## Important APIs, Types, and Functions

Important APIs are `onenand_scan()`, `onenand_release()`, `onenand_bbt_read_oob()`, address conversion helpers, `flexonenand_region()`, `struct onenand_chip`, `struct onenand_platform_data`, and option/manufacturer macros.

Source-visible symbols include structs: `struct onenand_bufferram`, `struct onenand_chip`, `struct onenand_bufferram	bufferram[MAX_BUFFERRAM];`, `struct completion	complete;`, `struct onenand_manufacturers`, `struct mtd_oob_ops *ops);`, `struct mtd_partition;`, `struct onenand_platform_data`, `struct mtd_partition *parts;`; enums: none visible in this header; typedefs: none visible in this header; prototypes: `extern int onenand_scan(struct mtd_info *mtd, int max_chips);`, `extern void onenand_release(struct mtd_info *mtd);`, `unsigned short (*read_word)(void __iomem *addr);`, `unsigned onenand_block(struct onenand_chip *this, loff_t addr);`, `loff_t onenand_addr(struct onenand_chip *this, int block);`, `int flexonenand_region(struct mtd_info *mtd, loff_t addr);`; representative macros: `__LINUX_MTD_ONENAND_H`, `MAX_DIES`, `MAX_BUFFERRAM`, `ONENAND_PAGES_PER_BLOCK`, `ONENAND_CURRENT_BUFFERRAM`, `ONENAND_NEXT_BUFFERRAM`, `ONENAND_SET_NEXT_BUFFERRAM`, `ONENAND_SET_PREV_BUFFERRAM`, `ONENAND_SET_BUFFERRAM0`, `ONENAND_SET_BUFFERRAM1`, `FLEXONENAND`, `ONENAND_GET_SYS_CFG1`, `ONENAND_SET_SYS_CFG1`, `ONENAND_IS_DDP`, `ONENAND_IS_MLC`, `ONENAND_IS_2PLANE`.

## Control Flow

OneNAND drivers issue commands through replaceable `command`, `wait`, `bbt_wait`, BufferRAM read/write, word access, chip-probe, block-markbad, and scan-BBT hooks. BufferRAM macros toggle between the two internal buffers; option macros adapt behavior for Flex-OneNAND, DDP, MLC, 2-plane, cache program, and 4K pages.

## State and Persistence Behavior

Runtime state includes MMIO base, die boundaries and sizes, chip/device/version/technology IDs, geometry shifts, current BufferRAM index, completion/IRQ, spinlock/waitqueue, `flstate_t` state, page/OOB/verify buffers, bad-block management pointer, private data, and an `ongoing` multi-command flag.

## Dependencies and Integration Points

It depends on `flashchip.h`, OneNAND register definitions, bad-block management, completions/spinlocks, and MTD core.

Direct includes observed in the source are: `#include <linux/spinlock.h>`, `#include <linux/completion.h>`, `#include <linux/mtd/flashchip.h>`, `#include <linux/mtd/onenand_regs.h>`, `#include <linux/mtd/bbm.h>`.

## Risks and Edge Cases

BufferRAM index mistakes, Flex-OneNAND die boundary calculations, and command sequence status handling can corrupt data. Locking must coordinate interrupt completion with synchronous waiters.

## Test Signals

Scan/release lifecycle, BufferRAM switching, read/program/erase, cache-program sequences, Flex-OneNAND region mapping, bad-block marking, and IRQ/timeout wait paths.

Source read signal: 240 lines, 7974 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
