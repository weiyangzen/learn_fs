# File Research: sources/block-storage/devicemapper-rs/src/core/device.rs

## Purpose
Defines `Device`, the major/minor representation used by device-mapper APIs, plus conversions to/from Linux device encodings and block-device node discovery.

## Key APIs
`Device { major, minor }`, `Display` as `major:minor`, `FromStr`, `From<dev_t>`, `From<Device> for dev_t`, `from_kdev_t`, `to_kdev_t`, and `devnode_to_devno`.

## Behavior
Handles glibc/libc `dev_t` via `major`, `minor`, and `makedev`, with Android conversion differences. `from_kdev_t`/`to_kdev_t` implement kernel “huge” `kdev_t` encoding and reject values too large for 12-bit major/20-bit minor representation. `devnode_to_devno` returns `Ok(None)` for missing or non-block paths.

## Tests/Notes
Tests verify round-trip `dev_t` and `kdev_t` conversions. Metadata failures are wrapped as core `MetadataIo`.
