# File Research: sources/cow-pools/bcachefs-tools/src/device_scan.rs

Implements bcachefs member-device discovery for mounting/opening, with udev first and whole-block scan fallback.

Core functions:
- `read_super_silent` reads a superblock with `noexcl`, `nochanges`, and `no_version_check`.
- `should_skip_multipath_component` filters multipath component devices via udev property or sysfs holder detection.
- `get_devices_by_uuid_udev` queries initialized block devices tagged `ID_FS_TYPE=bcachefs` and matching `ID_FS_UUID`.
- `get_all_block_devnodes` uses udev and falls back to `/proc/partitions` when udev is missing or empty.
- `read_sbs_matching_uuid` probes candidate devices and returns matching superblock handles.
- `scan_sbs` handles colon-separated explicit devices, UUID strings, and normal device paths.
- `open_scan` expands a single member path into all discovered members before `Fs::open`.
- `bch2_scan_devices` is a C ABI bridge returning a colon-joined device string.

Multipath behavior:
- Discovery filters component paths, but explicit user-provided paths are honored with warnings.
- The udev rule in this group sets the same multipath skip policy for enumeration.

Fallback strategy:
- If udev finds fewer devices than the first found superblock says are expected, it falls back to scanning all block devices.
- Without udev, `/proc/partitions` gives basic device enumeration.

Potential concerns:
- `/proc/partitions` fallback only includes `/dev/<name>` paths that already exist; systems with unusual device node layouts may be missed.
- When udev returns some devices but no readable superblock, expected count is zero and fallback proceeds only because the code does not early return unless `sbs.len() >= expected`; with zero expected and zero sbs this condition is true if reached inside non-empty udev path? In the current code, `expected` becomes 0 and `sbs.len() >= expected` returns true, so an unreadable udev result set could return empty instead of falling back.
