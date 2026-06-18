# File Research: sources/cow-pools/bcachefs-tools/src/wrappers/sysfs.rs

Provides sysfs and mount-table helper functions for mounted bcachefs filesystems.

Functions:
- `dev_name_from_sysfs` resolves `dev-N/block` symlink to a block device name, falling back to the sysfs directory name for offline devices.
- `sysfs_path_from_fd` resolves `/proc/self/fd/<fd>` for a sysfs fd.
- `read_sysfs_u64` parses a sysfs attribute as `u64`.
- `read_sysfs_fd_str` reads a small string attribute relative to a directory fd.
- `bcachefs_kernel_version` reads `/sys/module/bcachefs/parameters/version`, returning 0 if unavailable.
- `dev_mounted` parses `/proc/mounts`, handling colon-separated bcachefs device lists, and compares device identities.
- `sysfs_write_str` best-effort writes a string to an attribute relative to sysfs fd.
- `fs_get_devices` enumerates `dev-N` directories, reading device name, label, and durability.

Potential concerns:
- `read_sysfs_fd_str` reads at most 256 bytes and does not loop; adequate for current short attributes.
- `dev_mounted` splits mount device fields on `:`, which works for bcachefs device lists but could interact poorly with escaped mount fields or unusual path names.
- `sysfs_write_str` ignores all write errors.
