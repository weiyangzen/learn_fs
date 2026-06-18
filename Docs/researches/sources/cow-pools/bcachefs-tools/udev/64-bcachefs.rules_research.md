# File Research: sources/cow-pools/bcachefs-tools/udev/64-bcachefs.rules

Defines udev rules for bcachefs block devices.

Behavior:
- Applies only to non-remove block events where `ID_FS_TYPE=bcachefs` and `SYSTEMD_READY` is not `0`.
- Sets `UDISKS_AUTO=0` to discourage udisks from automatically mounting bcachefs filesystems.
- Skips multipath component devices when `DM_MULTIPATH_DEVICE_PATH=1`.
- Adds a per-member UUID symlink under `disk/by-uuid/` using `ID_FS_UUID_SUB_ENC` when available.

Security/operational intent:
- The udisks setting does not remove filesystem attack surface, but prevents unattended automount in locked-session scenarios.
- Multipath filtering aligns with Rust-side scanning behavior so enumeration prefers the dm-multipath map, not underlying paths.
