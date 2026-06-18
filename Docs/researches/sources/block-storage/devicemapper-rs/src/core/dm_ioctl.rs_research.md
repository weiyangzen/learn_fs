# File Research: sources/block-storage/devicemapper-rs/src/core/dm_ioctl.rs

## Purpose
Re-exports bindgen-generated `devicemapper_sys` structs/constants and records supported ioctl command version requirements.

## Key APIs
Re-exports `dm_ioctl`, `dm_name_list`, `dm_target_deps`, `dm_target_msg`, `dm_target_spec`, `dm_target_versions`, and constants. Provides `ioctl_to_version`, `ioctl_uses_udev_cookie`, and `ioctl_uses_event_number`.

## Behavior
`IOCTL_VERSIONS` maps commands to minimum `(major, minor, patch)` interface versions, conditionally including newer commands behind cfg flags. Udev cookies are used for remove, rename, and suspend/resume; `DM_DEV_WAIT` uses `event_nr` as an event number but not for udev sync.

## Notes
`DM_DEV_ARM_POLL` is intentionally gated at 4.37 despite libdevmapper documenting 4.36, because the command appeared after 4.36.0.
