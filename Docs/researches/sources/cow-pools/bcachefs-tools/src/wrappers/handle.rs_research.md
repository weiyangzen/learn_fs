# File Research: sources/cow-pools/bcachefs-tools/src/wrappers/handle.rs

Defines `BcachefsHandle`, an RAII handle to a mounted bcachefs filesystem with ioctl and sysfs fds, plus high-level wrappers for subvolume, disk, superblock, and device-usage ioctls.

Opening paths:
- UUID string: opens `/sys/fs/bcachefs/<uuid>`, reads `minor`, then opens `/dev/bcachefs<minor>-ctl`.
- Mounted path: detects via `BCH_IOCTL_QUERY_UUID`, uses `FS_IOC_GETFSSYSFSPATH` or UUID fallback to open sysfs.
- Block device: reads `/sys/dev/block/<major>:<minor>/bcachefs` symlink to infer filesystem UUID and dev index.
- Fallback file/device path: reads the superblock to infer user UUID, then opens the mounted filesystem by name.

Ioctl compatibility:
- `v2_v1_ioctl!` tries newer v2 ioctls with an 8192-byte error buffer and falls back to v1 on `ENOTTY`.
- On v2 errors, prints the kernel-provided error message if present.

Supported operations:
- `create_subvolume`, `delete_subvolume`, and `snapshot_subvolume`.
- `disk_add`, `disk_remove`, `disk_online`, `disk_offline`, `disk_set_state`.
- `disk_resize` and `disk_resize_journal`.
- `read_super` via `BCH_IOCTL_READ_SUPER`, growing buffer on `ERANGE`.
- `sb_version`.
- `dev_usage`, with v2 flex-array parsing and v1 fallback.

Device usage helpers:
- `DevUsage` exposes capacity, hidden sectors, used sectors, used buckets, and typed data-type iteration.
- Caps iteration at known `BCH_DATA_NR` to avoid interpreting more kernel-returned types than userspace knows.

Potential concerns:
- `open_via_superblock` calls `bch2_free_super` on a handle obtained from Rust wrapper APIs; this depends on ownership expectations matching exactly.
- `read_super` starts at 4096 bytes and grows to under 1 MiB; unusually large superblocks beyond that fail.
- UUID parsing/formatting is implemented manually and accepts only canonical 32 hex digits with optional dashes.
