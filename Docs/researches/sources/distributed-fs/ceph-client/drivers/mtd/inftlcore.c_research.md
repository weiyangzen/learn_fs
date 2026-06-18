<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/inftlcore.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/inftlcore.c

Purpose: implements the block-translation runtime for INFTL, exposing M-Systems DiskOnChip NAND as a 512-byte-sector `mtd_blktrans` device. It accepts only NAND MTDs named `DiskOnChip`, mounts INFTL metadata, computes disk geometry, and services sector reads/writes through virtual-unit chains stored in NAND OOB.

Important APIs, types, and functions: `inftl_tr` wires `.readsect`, `.writesect`, `.getgeo`, `.add_mtd`, and `.remove_dev`. `struct INFTLrecord` owns `PUtable`, `VUtable`, geometry, erase size, free counts, and the backing `mtd_info`. Core helpers include `inftl_read_oob()`, `inftl_write_oob()`, `INFTL_findfreeblock()`, `INFTL_findwriteunit()`, `INFTL_foldchain()`, `INFTL_makefreeblock()`, `INFTL_deleteblock()`, `inftl_readblock()`, and `inftl_writeblock()`.

Control flow: `inftl_add_mtd()` filters devices, allocates `INFTLrecord`, calls `INFTL_mount()`, derives CHS geometry, and registers the block translator. Reads walk the VU chain until a sector OOB state is `SECTOR_USED`, return zeroes for absent/deleted sectors, and tolerate corrected bitflips. Writes skip all-zero data by deleting the logical sector; non-zero writes find a free sector in the existing chain or allocate/fold chains before writing data plus `SECTOR_USED` OOB. Folding copies live sectors into the newest target unit, then erases older units oldest-first.

State and persistence: persistent truth is on-flash OOB metadata: unit headers, previous-unit pointers, ANAC/NAC counters, erase marks, and per-sector status bytes. In-memory `PUtable` and `VUtable` are reconstructed by mount and updated after allocation, fold, erase, and delete. Free space tracking is volatile and recomputed at mount.

Dependencies and integration points: depends on NAND MTD, OOB operations, `linux/mtd/inftl.h`, `linux/mtd/nftl.h`, raw NAND bad-block support, and the MTD block translation layer via `module_mtd_blktrans()`.

Risks: no modern wear-leveling is implemented; chain folding is a minimal free-space recovery path. Power loss during fold/delete relies on mount recovery and oldest-first erase ordering. Chain walking has loop guards but corruption still risks data loss or reserved blocks. Write errors are not always checked deeply after `inftl_write()`. Test signals are mount success, correct VU/PU chain dumps under debug, sector read/write/delete behavior, free-block accounting under low space, bad-block handling, and recovery after interrupted folds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/inftlcore.c -->
