# File Research: sources/block-storage/cryptsetup/lib/utils_device.c

## Purpose
Implements cryptsetup’s internal device abstraction for block devices, regular-file loop backing, direct I/O, topology, locking, sizing, and open-fd caching.

## Key Responsibilities
- Allocates and frees `struct device` instances.
- Detects whether paths are usable block devices or regular files requiring loop setup.
- Prefers direct I/O but falls back after a real read test when needed.
- Caches read-only/read-write fds and supports exclusive block-device opens.
- Tracks device block size, filesystem block size, physical block size, alignment, and loop block size.
- Attaches regular files to autoclear loop devices when needed.
- Checks device size/access, performs file growth, and calculates adjusted activation sizes.
- Reports topology alignment, read-ahead, rotational/DAX/zoned/NOP-DIF properties.
- Integrates metadata read/write locking via `utils_device_locking.c`.

## Important Details
- Regular files initially return `-ENOTBLK` from readiness checks so loop setup can be deferred.
- Direct I/O is validated with `read_lseek_blockwise()` on non-block devices.
- `device_block_adjust()` converts real device size to sectors and applies read-only activation flags.
- `device_is_identical()` compares block-device `st_rdev` or regular-file inode/device pairs.
- `device_internal_prepare()` requires root for loopback device use.
- Locked opens verify that the opened fd still corresponds to the locked resource.

## Dependencies
Uses Linux block ioctls, loop helpers, devpath/sysfs helpers, metadata locking, blockwise I/O, and libcryptsetup logging/error APIs.
