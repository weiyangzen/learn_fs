# sources/distributed-fs/ceph-client/include/linux/mtd/mtd.h

## Purpose

Defines the Linux MTD core device contract: `struct mtd_info`, erase/OOB operations, partition/master relationships, callback wrappers, pairing schemes, registration, notifiers, and common geometry helpers.

## Important APIs, Types, and Functions

Key types include `struct erase_info`, `mtd_oob_ops`, `mtd_oob_region`, `mtd_ooblayout_ops`, `mtd_pairing_scheme`, `mtd_part`, `mtd_master`, and `mtd_info`. Public functions include `mtd_erase/read/write/read_oob/write_oob`, OTP accessors, lock/bad-block helpers, device registration/unregistration, `get_mtd_device*()`, notifiers, and mmap capability helpers.

Source-visible symbols include structs: `struct mtd_info;`, `struct erase_info`, `struct mtd_erase_region_info`, `struct mtd_req_stats`, `struct mtd_oob_ops`, `struct mtd_req_stats *stats;`, `struct mtd_oob_region`, `struct mtd_ooblayout_ops`, `struct mtd_oob_region *oobecc);`, `struct mtd_oob_region *oobfree);`, `struct mtd_pairing_info`, `struct mtd_pairing_scheme`; enums: none visible in this header; typedefs: none visible in this header; prototypes: `int mtd_ooblayout_count_freebytes(struct mtd_info *mtd);`, `int mtd_ooblayout_count_eccbytes(struct mtd_info *mtd);`, `return dev_of_node(&mtd->dev);`, `int mtd_pairing_groups(struct mtd_info *mtd);`, `int mtd_erase(struct mtd_info *mtd, struct erase_info *instr);`, `int mtd_unpoint(struct mtd_info *mtd, loff_t from, size_t len);`, `int mtd_read_oob(struct mtd_info *mtd, loff_t from, struct mtd_oob_ops *ops);`, `int mtd_write_oob(struct mtd_info *mtd, loff_t to, struct mtd_oob_ops *ops);`, `int mtd_lock_user_prot_reg(struct mtd_info *mtd, loff_t from, size_t len);`, `int mtd_erase_user_prot_reg(struct mtd_info *mtd, loff_t from, size_t len);`, `int mtd_lock(struct mtd_info *mtd, loff_t ofs, uint64_t len);`, `int mtd_unlock(struct mtd_info *mtd, loff_t ofs, uint64_t len);`, `int mtd_is_locked(struct mtd_info *mtd, loff_t ofs, uint64_t len);`, `int mtd_block_isreserved(struct mtd_info *mtd, loff_t ofs);`; representative macros: `__MTD_MTD_H__`, `MTD_FAIL_ADDR_UNKNOWN`, `mtd_device_register`.

## Control Flow

MTD users call `mtd_*()` wrappers rather than driver callbacks directly. The wrappers validate ranges, translate partition offsets through `mtd_get_master_ofs()`, dispatch to master callbacks, and maintain suspend state at the master. OOB helpers use `mtd_ooblayout_ops`; pairing helpers translate NAND write-unit ordering for MLC/TLC devices.

## State and Persistence Behavior

Each `mtd_info` stores public geometry, flags, OOB layout, ECC stats, bitflip threshold, optional erase regions, callback table, owner/refcount/device/nvmem handles, partition list, parent pointer, and master locks/suspend bit. Persistent flash state is accessed through callbacks; this header itself holds only kernel runtime state.

## Dependencies and Integration Points

It depends on Linux device, notifier, list, kref, NVMEM, device tree, ABI definitions, and low-level MTD drivers that fill the callback table.

Direct includes observed in the source are: `#include <linux/types.h>`, `#include <linux/uio.h>`, `#include <linux/list.h>`, `#include <linux/notifier.h>`, `#include <linux/device.h>`, `#include <linux/of.h>`, `#include <linux/nvmem-provider.h>`, `#include <mtd/mtd-abi.h>`.

## Risks and Edge Cases

Bypassing wrappers skips partition translation and validation. Wrong geometry or write/OOB sizes affects every filesystem and block translation user. Suspend state, refcounting, and partition list locks are shared integration points.

## Test Signals

Use MTD core tests for range validation, partition offset translation, OOB layout mapping, bad block handling, bitflip/ECC error return semantics, notifier delivery, suspend/resume, and registration cleanup.

Source read signal: 724 lines, 22834 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
