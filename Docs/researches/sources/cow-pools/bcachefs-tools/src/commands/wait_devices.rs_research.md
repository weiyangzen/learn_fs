# File Research: sources/cow-pools/bcachefs-tools/src/commands/wait_devices.rs

Implements `bcachefs wait-devices`, which blocks until every device in a multi-device filesystem has appeared and is initialized in udev.

Behavior:
- Accepts only `UUID=<uuid>` or `OLD_BLKID_UUID=<uuid>` device strings via `device_scan::parse_uuid_equals`.
- Builds a udev monitor for block events and an initial enumerator for initialized bcachefs block devices.
- Tracks expected `number_of_devices` and observed device indices in `WaitInitialized`.
- Reads superblocks silently from matching devices to validate UUID, device index, and member count.
- Processes add/change/remove events until the set of unique device indices equals `number_of_devices`.

Multipath handling:
- Uses `device_scan::should_skip_multipath_component` to ignore underlying multipath component devices.

Error handling:
- Invalid device strings and inconsistent superblock `number_of_devices` values are hard errors.
- Devices whose superblock disappears with `ENOENT` are ignored.
- Invalid `dev_idx >= number_of_devices` is warned and skipped.

Potential concerns:
- There is no timeout or degraded-mode exit; the command can wait indefinitely if a device never appears.
- The filtering expression only rejects devices with a different parsed UUID; a device with missing/unparseable `ID_FS_UUID` reaches superblock probing, which may be intentional for robustness.
