# File Research: sources/block-storage/devicemapper-rs/src/core/dm_options.rs

## Purpose
Encapsulates per-call device-mapper flags and udev behavior.

## Key APIs
`DmOptions::set_flags`, `set_udev_flags`, `flags`, `udev_flags`, and `private`.

## Behavior
Methods consume and return `DmOptions` for builder-style chaining. `private()` disables subsystem, disk, and other udev rules while leaving core DM rules enabled.

## Notes
`core/dm.rs` encodes `udev_flags` in the upper bits of `event_nr` when relevant.
