# File Research: sources/block-storage/stratisd/src/engine/strat_engine/device.rs

This file provides small Linux block-device ioctl helpers.

Key responsibilities:
- Defines ioctl bindings for `BLKGETSIZE64`, `BLKSSZGET`, and `BLKPBSZGET`.
- Exposes:
  - `blkdev_size()` for device byte size.
  - `blkdev_logical_sector_size()` for logical sector size.
  - `blkdev_physical_sector_size()` for physical sector size.

Important behavior:
- Uses `linux_raw_sys` constants and `nix`-style ioctl macros.
- Converts ioctl out-parameters into `devicemapper::Bytes`.
- Wraps syscall failures in `StratisError::Msg`.
- Uses checked integer conversions for sector-size results.

Tests:
- No local tests in this file.
