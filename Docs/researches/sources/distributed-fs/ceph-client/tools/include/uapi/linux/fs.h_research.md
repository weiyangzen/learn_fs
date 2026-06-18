# sources/distributed-fs/ceph-client/tools/include/uapi/linux/fs.h

Purpose: central filesystem UAPI header for generic file, inode, block-device, cloning, dedupe, trimming, flags, async I/O, pagemap scanning, and `/proc` map query interfaces. It is a broad ABI surface consumed by libc, filesystem tools, storage tools, and io_uring.

Important APIs/types: structures include `file_clone_range`, `fstrim_range`, `fsuuid2`, `fs_sysfs_path`, `file_dedupe_range_info`, `file_dedupe_range`, `files_stat_struct`, `inodes_stat_t`, `fsxattr`, `page_region`, `pm_scan_arg`, and `procmap_query`. It defines seek modes, rename flags, integrity flags, block ioctls (`BLK*`), filesystem ioctls (`FICLONE`, `FIDEDUPERANGE`, `FS_IOC_*`), inode flags (`FS_*_FL`), xflags (`FS_XFLAG_*`), `__kernel_rwf_t` and `RWF_*` per-I/O flags, `PAGEMAP_SCAN`, and `PROCMAP_QUERY`.

Control flow, state, and persistence: flow is syscall/ioctl driven. Userspace issues file/block/procfs ioctls with these structures; kernel filesystem, block, or mm code reads input fields, performs operations, and fills output fields. Persistent effects include inode flags, labels, encryption/verity indicators, clone/dedupe extents, block-device state, and write-protection changes from pagemap scanning.

Dependencies and integration points: includes limits, ioctl, types, fscrypt for userspace, and mount flags. It integrates VFS, block layer, filesystems such as ext4/xfs/btrfs, procfs memory inspection, and io_uring read/write flags.

Risks and test signals: risks include ioctl number compatibility, 32/64-bit structure size issues, reserved fields not zeroed, dangerous persistent flags such as immutable/append/DAX, and partial clone/dedupe results. Tests should cover ioctl ABI sizes, compat ioctls, clone/dedupe/trim, fs labels/UUIDs, RWF flag validation, pagemap scans, and proc map queries with short buffers.
