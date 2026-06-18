# File Research: sources/block-storage/devicemapper-rs/src/core/deviceinfo.rs

## Purpose
Converts raw `dm_ioctl` headers into safe `DeviceInfo` values.

## Key APIs
`DeviceInfo::new`, `TryFrom<Struct_dm_ioctl>`, and getters for version, open count, event number, device, name, uuid, and flags.

## Behavior
Parses null-terminated `name` and `uuid` C arrays, converts empty strings to `None`, validates non-empty identifiers through `DmNameBuf`/`DmUuidBuf`, stores flags via `DmFlags::from_bits_truncate`, and converts `ioctl.dev` from kernel `kdev_t`.

## Notes
Fails with `InvalidArgument` if kernel name/uuid buffers lack NUL termination. `data_size` and `data_start` are retained but not exposed.
