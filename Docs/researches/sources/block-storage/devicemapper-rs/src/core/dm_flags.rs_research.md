# File Research: sources/block-storage/devicemapper-rs/src/core/dm_flags.rs

## Purpose
Defines Rust `bitflags` wrappers for kernel device-mapper flags and udev-cookie flags.

## Key Types
`DmFlags` wraps ioctl flags such as read-only, suspend, persistent dev, status table, buffer full, noflush, query inactive table, uevent generated, uuid rename, secure data, data out, deferred remove, and internal suspend. `DmUdevFlags` wraps libdevmapper udev-rule flags.

## Behavior
Flags map directly to constants from `devicemapper_sys`. `DmOptions` filters user-provided flags by each ioctl’s valid set before calling the kernel.

## Notes
`DmUdevFlags` comments mirror libdevmapper semantics, including rule disabling and primary-source behavior.
