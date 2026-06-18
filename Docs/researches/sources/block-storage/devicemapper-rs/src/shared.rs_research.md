# File Research: sources/block-storage/devicemapper-rs/src/shared.rs

## Purpose
Defines common abstractions and helpers for all high-level DM target wrappers.

## Key Types/Traits
`TargetType`/`TargetTypeBuf`, `TargetParams`, `TargetLine<T>`, `TargetTable`, and `DmDevice<T>`.

## Shared Device Behavior
`DmDevice` supplies kernel-table reads, default resume/suspend, table loading, and required device/name/size/table/teardown/uuid hooks. `device_create` creates, loads table, resumes, and removes the device if table load fails. `device_match` compares kernel table and uuid against local expectations. `device_exists` searches `list_devices`.

## Parsing Helpers
`parse_device` accepts block-device path or `major:minor`. `parse_value` wraps `FromStr`. `get_status_line_fields`, `get_status`, and `make_unexpected_value_error` centralize status parsing errors.

## Notes
`device_match` has a typo in its error string (“uuuid”). `device_create` uses default options for create/table-load and caller-provided options only for resume.
