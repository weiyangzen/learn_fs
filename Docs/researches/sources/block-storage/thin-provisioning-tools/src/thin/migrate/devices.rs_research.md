# File Research: sources/block-storage/thin-provisioning-tools/src/thin/migrate/devices.rs

This file provides Linux device-mapper and udev helpers for thin migration.

Key elements:
- `split_device_number()` splits `rdev` into major/minor using an 8-bit minor mask.
- `DeviceNr` represents a block device major/minor pair and can be created from `rdev` or devicemapper `Device`.
- `DmIndex` builds a map from `DeviceNr` to DM names using `DM::list_devices()`.
- `PoolTable` captures thin-pool metadata device, data device, and data block size.
- `ThinTable` captures pool device and thin ID.
- `parse_dev()`, `parse_thin_table()`, and `parse_pool_table()` parse DM table argument strings with `nom`.
- `DmInfo` converts from devicemapper `DeviceInfo` and exposes name, uuid, dev number, open count, event number, and flags.
- `DmScanner` owns a `DM` handle and index, and provides:
  - `get_table()`
  - `get_info()`
  - `dev_to_name()`
  - `file_to_name()`
  - `dev_to_path()` via udev enumeration
- Public helpers return parsed thin table, pool table, and device info.

Interactions:
- Used by migration base code.
- Depends on `devicemapper`, `udev`, Unix file metadata, and `nom`.

Risks and notes:
- `split_device_number()` uses a simple 8-bit minor mask, which may not match Linux’s full modern `dev_t` major/minor encoding for all devices.
- `DmIndex` is built once and can go stale if DM devices change.
- `get_table()` requires exactly one target row.
