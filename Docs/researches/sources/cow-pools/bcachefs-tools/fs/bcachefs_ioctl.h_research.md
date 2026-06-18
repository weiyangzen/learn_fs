# File Research: sources/cow-pools/bcachefs-tools/fs/bcachefs_ioctl.h

## Purpose
Defines the bcachefs userspace/kernel ioctl ABI for filesystem-wide and file-specific operations. This is a public contract header: layout, ioctl numbers, packing, alignment, and pointer-width decisions matter for compatibility.

## Main Contents
- Common force flags:
  - `BCH_FORCE_IF_DATA_LOST`
  - `BCH_FORCE_IF_METADATA_LOST`
  - `BCH_FORCE_IF_DATA_DEGRADED`
  - `BCH_FORCE_IF_METADATA_DEGRADED`
  - aggregate `BCH_FORCE_IF_LOST` and `BCH_FORCE_IF_DEGRADED`
- Device-addressing flags:
  - `BCH_BY_INDEX`: interpret `dev` as filesystem device index instead of pathname pointer.
  - `BCH_READ_DEV`: read a specific device superblock.
- Filesystem ioctl command definitions for:
  - UUID query
  - disk add/remove/online/offline/state/resize/journal resize
  - data jobs
  - usage/accounting/counters
  - superblock read
  - subvolume create/destroy/list/path
  - snapshot tree query
  - offline/online fsck
- File-specific ioctl command definitions for:
  - reinheriting attrs
  - reflink option propagation controls
  - raw pread with extended errors
  - unpoisoning file ranges

## ABI Structures
- `struct bch_ioctl_err_msg` is a reusable user-buffer error-reporting descriptor used by v2 ioctls.
- Device operation structures exist in legacy and v2 forms, where v2 variants append `err`.
- `struct bch_ioctl_data` starts background data jobs such as scrub, rereplicate, migrate, rewrite old nodes, and drop extra replicas. It carries btree ranges and operation-specific parameters.
- `struct bch_ioctl_data_event` reports progress from the returned job fd, currently with progress events only.
- `struct bch_replicas_usage`, `bch_ioctl_fs_usage`, `bch_ioctl_dev_usage`, and `bch_ioctl_dev_usage_v2` support older usage-query interfaces.
- `struct bch_ioctl_query_accounting` returns `bkey_i_accounting` entries.
- `struct bch_ioctl_query_counters` returns variable-length counter data.
- Subvolume ABI:
  - `bch_ioctl_subvol_dirent`
  - `bch_ioctl_subvol_readdir`
  - `bch_ioctl_subvol_to_path`
  - `bch_ioctl_snapshot_node`
  - `bch_ioctl_snapshot_tree_query`
- Raw recovery ABI:
  - `bch_ioctl_pread_raw` reports checksum, IO, decompression, and erasure-code reconstruction errors.
  - `bch_ioctl_unpoison` clears poison state over a file range.

## Notable Details
- Many user pointers are represented as `__u64`, keeping the ABI explicit across user/kernel boundary.
- Several variable-length arrays appear at the end of ioctl structures: `replicas[]`, `d[]`, `devs[]`, `accounting[]`, `nodes[]`.
- Some structs are explicitly `__packed __aligned(8)` to preserve expected userspace layout.
- `bch_ioctl_subvol_dirent_path_len()` treats `reclen` as an 8-byte-aligned record length with a NUL-terminated path inside it.
- Legacy and replacement ioctls coexist; comments mark old usage interfaces obsolete.

## Risks / Review Notes
- Ioctl numbers are ABI-sensitive. `BCH_IOCTL_FS_USAGE` and `BCH_IOCTL_DEV_USAGE` both use command number `11` with different structs, and `BCH_IOCTL_QUERY_ACCOUNTING` and `BCH_IOCTL_QUERY_COUNTERS` both use command number `21`; callers must rely on the intended dispatch context or compatibility handling.
- Typo-level comments exist, e.g. “offline or offline” and “approprate”; no code effect.
- The `__counted_by()` comment in `bch_ioctl_fsck_offline` documents an intentional avoidance of a compiler bounds-check issue for userspace pointers.
