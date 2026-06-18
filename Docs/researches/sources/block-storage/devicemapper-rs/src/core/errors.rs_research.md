# File Research: sources/block-storage/devicemapper-rs/src/core/errors.rs

## Purpose
Defines low-level core error variants for device-mapper operations.

## Key Variants
`ContextInit`, `InvalidArgument`, `Ioctl`, `IoctlResultTooLarge`, `MetadataIo`, `GeneralIo`, and `UdevSync`.

## Behavior
`Ioctl` carries ioctl number, optional input/output `DeviceInfo`, and underlying `nix::Error`. `Display` messages include operational context, including path metadata failures and maximum buffer size for oversized ioctl responses.

## Notes
`source()` exposes the underlying nix error only for ioctl failures.
