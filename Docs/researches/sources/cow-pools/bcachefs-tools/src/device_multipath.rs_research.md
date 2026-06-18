# File Research: sources/cow-pools/bcachefs-tools/src/device_multipath.rs

Provides helpers for identifying device-mapper multipath holder devices from a block device path.

Core behavior:
- Converts a block device `st_rdev` to `/sys/dev/block/<major>:<minor>`.
- Walks `holders/` entries, considering only `dm-*`.
- Reads `/sys/block/dm-*/dm/uuid` and treats `mpath-*`, `partN-mpath-*`, and nested `partN-partM-mpath-*` UUIDs as multipath.
- Resolves the preferred path as `/dev/mapper/<dm name>` if it exists, else `/dev/dm-N`.
- Recurses upward to find the topmost multipath holder with a maximum depth of 8.
- Exposes `warn_multipath_component` for user-facing warnings.

Tests cover:
- Sysfs attribute trimming and missing attributes.
- Missing/non-block input paths.
- Accepted and rejected multipath UUID forms.

Potential concerns:
- Tests do not mock full holder traversal because that depends on real block-device metadata/sysfs.
- The implementation picks the first matching holder returned by `read_dir`; if multiple holders exist, ordering is filesystem-dependent.
