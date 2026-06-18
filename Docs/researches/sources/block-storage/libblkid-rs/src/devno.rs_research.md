# File Research: sources/block-storage/libblkid-rs/src/devno.rs

Purpose: Provides a Rust newtype for device numbers and conversions between device numbers, major/minor values, device names, and whole-disk devices.

Key APIs:
- `from_device_numbers`
- `major`
- `minor`
- `to_devname`
- `to_wholedisk`

Implementation notes:
- Uses platform-specific `maj_t` and `min_t` aliases.
- Frees the string returned by `blkid_devno_to_devname`.

Notable risks:
- `to_wholedisk` converts the entire 4096-byte buffer with `std::str::from_utf8`, preserving trailing NUL bytes. It should read only up to the first NUL.
- No `ty` module is defined for Android because the cfgs cover Linux and non-Linux/non-Android Unix only.
- `to_wholedisk` uses a fixed buffer size matching the crate docs, but truncation behavior depends on libblkid.
