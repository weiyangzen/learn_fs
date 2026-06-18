# File Research: sources/block-storage/devicemapper-rs/src/core/dm.rs

## Purpose
Implements the low-level device-mapper control context and all ioctl-facing operations.

## Key APIs
`DM::new`, `version`, `remove_all`, `list_devices`, `device_create`, `device_remove`, `device_rename`, `device_suspend`, `device_info`, `device_wait`, `table_load`, `table_clear`, `table_deps`, `table_status`, optional `list_versions`, `target_msg`, and `arm_poll`.

## Core Mechanics
`DM` opens `/dev/mapper/control` on Linux or `/dev/device-mapper` on Android. `DmOptions::to_ioctl_hdr` builds ioctl headers with filtered flags and udev flags encoded into `event_nr`. `do_ioctl` sets minimum ioctl interface versions, clears `event_nr` for commands that do not accept input there, starts udev synchronization when needed, serializes header/input data into a growable buffer, retries on `DM_BUFFER_FULL`, and parses the output into `DeviceInfo` plus data bytes.

## Table Handling
`table_load` serializes `dm_target_spec` records plus NUL-padded parameter strings aligned to `u64`. `parse_table_status` reconstructs `(start, length, target_type, params)` tuples and trims via NUL parsing. `table_deps` converts dependency devices from kernel `kdev_t`.

## Error/Retry Behavior
Ioctl failures include both input and output headers when parseable. `device_remove` retries `EBUSY` up to five attempts with 200 ms delay. Oversized ioctl responses return `IoctlResultTooLarge`.

## Tests/Notes
Sudo-style tests cover version, list/create/remove/rename/status/table/deps semantics, duplicate names/UUIDs, UUID setting behavior, and a no-udev lifecycle using an error target.
