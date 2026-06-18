<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nftlcore.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nftlcore.c

Purpose: NAND Flash Translation Layer block translation driver for M-Systems DiskOnChip NFTL media. It exposes an MTD NAND device as a 512-byte sector block device and implements read plus optional write/fold logic.

Important APIs/types/functions: `nftl_add_mtd()` detects DiskOnChip NAND and mounts NFTL metadata. `nftl_remove_dev()` unregisters and frees tables. `nftl_read_oob()` and `nftl_write_oob()` wrap MTD OOB access. Under `CONFIG_NFTL_RW`, `NFTL_findfreeblock()`, `NFTL_foldchain()`, `NFTL_makefreeblock()`, `NFTL_findwriteunit()`, and `nftl_writeblock()` implement allocation/folding/writes. `nftl_readblock()` resolves the latest sector copy. `nftl_tr` registers `mtd_blktrans_ops`.

Control flow: When a DiskOnChip MTD appears, the driver allocates `NFTLrecord`, calls `NFTL_mount()` from `nftlmount.c`, calculates CHS geometry, and registers a blktrans device. Reads map a logical sector to its virtual unit chain, scan replacement units using OOB sector status, remember the last `SECTOR_USED`, stop at `SECTOR_FREE`, then read that 512-byte sector or return zeroes when absent. Writes find or allocate a writable erase unit, possibly fold a long chain to reclaim blocks, then write data plus OOB sector status.

State and persistence: Runtime state includes `EUNtable`, `ReplUnitTable`, free-block counts, last free unit, CHS geometry, and MTD blktrans registration. Persistent state is NFTL OOB metadata: virtual unit numbers, replacement unit links, sector status bytes, fold marks, erase marks, and wear info. Folding rewrites chains and formats old units.

Dependencies/integration: Depends on MTD core, raw NAND type checks, DiskOnChip naming convention, blktrans, and NFTL structures in `linux/mtd/nftl.h`. Module registration is via `module_mtd_blktrans(nftl_tr)`.

Risks: The driver only accepts MTD names beginning with `"DiskOnChip"`, which is fragile but intentional legacy behavior. Write support is gated by `CONFIG_NFTL_RW` and has comments acknowledging limited wear leveling and power-loss assessment. Chain traversal uses loop guards but corrupted OOB can still lead to data loss, reserved blocks, or formatting. Geometry emulation is legacy CHS and may not match all sizes cleanly.

Test signals: Attach DiskOnChip NFTL images, verify mount and blktrans device creation, read known virtual chains, test absent sectors returning zeroes, run optional write/fold/power-fail recovery tests under `CONFIG_NFTL_RW`, validate bad/corrupt OOB handling, and check module add/remove frees both tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nftlcore.c -->
