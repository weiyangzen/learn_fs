# File Research: sources/block-storage/devicemapper-rs/src/core/mod.rs

## Purpose
Defines the low-level core module tree and public re-exports.

## Exports
Exports `devnode_to_devno`, `Device`, `DeviceInfo`, `DM`, `DmFlags`, `DmUdevFlags`, `DmOptions`, `DevId`, `DmName`, `DmNameBuf`, `DmUuid`, and `DmUuidBuf`.

## Internal Modules
Includes device, deviceinfo, dm, flags, ioctl bindings, options, udev sync, errors, SysV semaphore bindings, typed IDs, and utilities.

## Notes
Only `errors` is public as a module; most implementation modules stay private behind selected re-exports.
