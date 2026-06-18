# File Research: sources/block-storage/devicemapper-rs/src/core/sysvsem.rs

## Purpose
Thin re-export module for SysV semaphore types/constants missing or awkward in `libc`.

## Exports
`seminfo`, `semun`, `GETVAL`, `SEM_INFO`, and `SETVAL` from `devicemapper_sys`.

## Usage
Consumed by `dm_udev_sync.rs` for `semctl` operations and SysV semaphore capability probing.
