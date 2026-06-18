# sources/distributed-fs/ceph-client/drivers/mtd/mtdblock.c

Purpose: writable block-device emulation for MTD devices. It registers an `mtd_blktrans_ops` named `mtdblock` and implements sector reads/writes with an eraseblock-sized read-modify-write cache so partial 512-byte writes can be applied to erase-oriented flash.

Important APIs/types/functions: `struct mtdblk_dev`, `erase_write()`, `write_cached_data()`, `do_cached_write()`, `do_cached_read()`, `mtdblock_open()`, `mtdblock_release()`, `mtdblock_flush()`, `mtdblock_add_mtd()`, `mtdblock_tr`. It depends on the blktrans framework, `mtd_read()`, `mtd_write()`, `mtd_erase()`, `mtd_sync()`, `vmalloc()` for cache data, and MTD geometry/flags.

Control flow: the blktrans notifier creates one device per MTD index. Opening initializes cache state, warns for NAND, and sets cache size to erasesize unless `MTD_NO_ERASE`. Reads use cached dirty/clean data if the requested sector belongs to the cached eraseblock, otherwise read from MTD. Writes either erase/write a full sector-sized eraseblock directly or load an eraseblock into cache, patch bytes, and mark dirty. Flush/release write dirty cache and sync writable devices; last close frees cache.

State and persistence: runtime state tracks open count, cache mutex, cache buffer, cached eraseblock offset/size, and dirty state. Persistent flash is only updated on full-block writes or cache writeback, not immediately for every partial write.

Risks and test signals: power loss before cache flush can lose partial writes. Cache allocation happens lazily in write path and returns `-EINTR` on allocation failure. Tests should cover partial writes across eraseblock boundaries, full eraseblock writes bypassing cache, bitflip-tolerant reads, readonly MTDs, NAND warning, flush-on-release, and EIO cache invalidation.
