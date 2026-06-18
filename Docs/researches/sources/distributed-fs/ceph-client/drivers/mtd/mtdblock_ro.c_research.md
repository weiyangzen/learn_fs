# sources/distributed-fs/ceph-client/drivers/mtd/mtdblock_ro.c

Purpose: simple block-device emulation variant that marks disks read-only while still providing a `writesect` callback for RAM-backed or otherwise writable use through the common translation layer. It avoids the eraseblock writeback cache used by `mtdblock.c`.

Important APIs/types/functions: `mtdblock_readsect()`, `mtdblock_writesect()`, `mtdblock_add_mtd()`, `mtdblock_remove_dev()`, and `mtdblock_tr`. It depends on `mtd_read()`, `mtd_write()`, `mtd_is_bitflip()`, blktrans registration, and MTD index/size fields.

Control flow: the add callback allocates a generic `mtd_blktrans_dev`, sets devnum from `mtd->index`, size from `mtd->size >> 9`, marks it readonly, warns for NAND, and calls `add_mtd_blktrans_dev()`. Sector reads and writes perform one 512-byte MTD read/write at `block * 512`. Removal delegates to `del_mtd_blktrans_dev()`.

State and persistence: no cache or private state beyond the allocated blktrans device. Persistent behavior is immediate and entirely delegated to the underlying MTD.

Risks and test signals: write callback ignores short `retlen`; read callback treats ECC bitflips as success but also ignores short reads. Because the disk is readonly, normal block writes should be blocked by block-layer policy. Tests should cover readonly flag, RAM-write path if enabled, NAND warning, add/remove, short I/O handling, and bitflip read status.
