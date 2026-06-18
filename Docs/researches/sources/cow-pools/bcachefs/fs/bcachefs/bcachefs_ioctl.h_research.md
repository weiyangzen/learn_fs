# File Research: sources/cow-pools/bcachefs/fs/bcachefs/bcachefs_ioctl.h

This header defines the bcachefs user/kernel ioctl ABI. It is a stable interface surface for filesystem-wide operations, device management, fsck, accounting queries, subvolume/snapshot queries, and several file-specific recovery operations.

Key contents:
- Common force flags: `BCH_FORCE_IF_*`, plus device addressing flags `BCH_BY_INDEX` and `BCH_READ_DEV`.
- Filesystem ioctls under ioctl type `0xbc`, including disk add/remove/online/offline, state changes, resizing, journal resizing, data operations, superblock reads, subvolume operations, fsck, accounting/counters, subvolume listing/path resolution, and snapshot-tree queries.
- Versioned ABI structs such as `bch_ioctl_disk_v2`, `bch_ioctl_disk_set_state_v2`, `bch_ioctl_disk_resize_v2`, and `bch_ioctl_subvolume_v2` add `bch_ioctl_err_msg` for detailed userspace error reporting.
- Background data operations use `struct bch_ioctl_data`, `bch_ioctl_data_event`, and `bch_ioctl_data_progress` to expose progress for scrub/rereplicate/migrate/rewrite/drop-extra-replicas jobs through a returned file descriptor.
- Obsolete usage structs remain present for compatibility: `bch_ioctl_fs_usage`, `bch_ioctl_dev_usage`, and `bch_ioctl_dev_usage_v2`.
- Newer metadata query structures expose disk accounting (`bch_ioctl_query_accounting`), counters, subvolume directory entries, subvolume-to-path resolution, and full snapshot tree nodes with per-snapshot accounting.
- File-specific ioctls include raw direct reads with extended error reporting (`BCHFS_IOC_PREAD_RAW`) and unpoisoning poisoned file extents (`BCHFS_IOC_UNPOISON`).

Important details:
- Many structs use fixed-width integer types and explicit padding because they define ABI layout.
- Several flexible-array structs carry user buffers or variable entries; callers must respect input/output size semantics such as `-ERANGE`.
- `bch_ioctl_subvol_dirent_path_len()` computes a bounded path length using `reclen`, preserving safety around padded variable-length records.
