# File Research: sources/cow-pools/bcachefs-tools/src/wrappers/bdev.rs

Provides Rust replacements for low-level block-device utilities formerly in C.

Functions:
- `get_size` returns block-device size via `BLKGETSIZE64` or regular file `st_size`.
- `get_blocksize_physical_hint` returns physical block size via `BLKPBSZGET` or `st_blksize`.
- `fd_to_dev_model` reads model/backing file information from sysfs.
- `fd_to_dev_serial` reads serial number from sysfs.
- `nonrot` uses `BLKROTATIONAL` ioctl to detect non-rotational devices.
- `open_device` maps `BLK_OPEN_*` flags to POSIX `open` flags, including `O_DIRECT`, `O_EXCL`, and `O_CREAT`.
- `blkid_check` calls a C helper for filesystem probing.

Potential concerns:
- `get_size` and `get_blocksize_physical_hint` ignore ioctl return values and may return zero on failure.
- `open_device` initializes flags to 0 if no read/write mode is supplied, which means an accidental default can become `O_RDONLY`-like behavior on Linux.
- Helper `fstat` exits the process via `super_io::die` instead of returning a recoverable error.
