# File Research: sources/cow-pools/bcachefs-tools/src/commands/format_util.rs

This file is the Rust implementation of bcachefs formatting internals, replacing C `bch2_format` and `bch2_format_for_device_add`.

Core type:
- `DevOpts` owns a device fd, path, label, size/offset metadata, per-device options, and closes the fd on drop.

Main functions:
- `format()` creates and writes a new filesystem superblock across one or more devices.
- `format_for_device_add()` formats a single device for adding to an existing filesystem.
- `format_opts_default()` chooses default metadata version from kernel/current support.
- `pick_block_size()` chooses 512 bytes for small filesystems and at least 4 KiB/physical block size for larger ones.
- `pick_bucket_size()` chooses a filesystem-wide bucket size based on block size, btree node size, encoded extent size, total filesystem size, and fsck memory constraints.
- `check_bucket_size()` validates per-device bucket constraints.

Format logic:
- Determines missing device sizes.
- Selects block size, bucket sizes, btree node size, UUIDs, labels, member fields, feature bits, and time base.
- Sets all superblock options from filesystem and device `bch_opts`.
- Builds members_v2 and v1 compatibility copies.
- Resolves foreground/background/promote/metadata targets from device paths or disk groups.
- Initializes encryption field when requested.
- Writes superblock layouts and zeroes the start of disks when using the default superblock sector.
- Triggers `udevadm trigger --settle` for formatted devices.

Important safety behavior:
- Device opening uses exclusive read/write buffered mode and blkid checks unless explicitly bypassed by special helpers.
- Fatal validation failures call wrapper `die()`, matching older C behavior.
