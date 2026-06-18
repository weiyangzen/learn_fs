# File Research: sources/block-storage/devicemapper-rs/src/shared_macros.rs

## Purpose
Provides small implementation macros shared by DM device wrapper structs.

## Key Macros
`device!`, `name!`, `uuid!`, `devnode!`, `to_raw_table_unique!`, `table!`, and `status!`.

## Behavior
Macros delegate common methods to `dev_info` and `table`, build `/dev/dm-<minor>` paths, convert single-line target tables to raw tuples, and implement status retrieval via `DM::table_status` plus parser conversion.

## Notes
`name!` panics if `DeviceInfo` has no name, so wrapper structs assume named DM devices.
