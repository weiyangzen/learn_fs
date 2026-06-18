# sources/distributed-fs/ceph-client/drivers/mtd/mtdchar.c

Purpose: MTD character-device frontend for `/dev/mtdX` and `/dev/mtdXro`. It implements open/read/write/lseek/ioctl/mmap hooks, exposes erase/OOB/OTP/raw/bad-block/partition operations to userspace, and serializes ioctl mutation through the master MTD chrdev lock.

Important APIs/types/functions: `struct mtd_file_info`, `mtdchar_open()`, `mtdchar_read()`, `mtdchar_write()`, `mtdchar_ioctl()`, `mtdchar_read_ioctl()`, `mtdchar_write_ioctl()`, `mtdchar_readoob()`, `mtdchar_writeoob()`, `mtdchar_blkpg_ioctl()`, `init_mtdchar()`, `cleanup_mtdchar()`. It depends on `get_mtd_device()`, `put_mtd_device()`, all public MTD operation wrappers, user-copy helpers, compat ioctl conversion, and `mtdcore.h`.

Control flow: open maps minor to MTD index, rejects write opens on ro minors or non-writable devices, gets an MTD ref, and stores mode state. Read/write clamp to device size, allocate a degraded-size bounce buffer via `mtd_kmalloc_up_to()`, then loop through normal, raw, or OTP operations. Ioctl first classifies commands into safe/dangerous and requires write mode for destructive commands, then handles info, erase, OOB, MEMREAD/MEMWRITE, lock/unlock, bad block, OTP, ECC layout/stats, raw/OTP file modes, and BLKPG partition add/delete. Close syncs write opens and drops refs.

State and persistence: per-open state holds the selected MTD and file mode. Persistent effects include writes, erases, bad-block marks, locks, OTP changes, and dynamic partitions.

Risks and test signals: ioctl surface is broad and must maintain ABI compatibility. OOB length adjustment and ECC error reporting are subtle. Tests should cover permission checks, ro minors, raw mode, OTP mode switching, ECC read returns, OOB-only operations, dynamic partition ioctls, compat OOB ioctls, size clamping, and mmap behavior on NOMMU.
