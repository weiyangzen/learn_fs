# File Research: sources/cow-pools/bcachefs-tools/src/wrappers/ioctl.rs

Provides const helpers for encoding bcachefs ioctl numbers.

Functions:
- `bch_ioc_w<T>(nr)` computes `_IOW(0xbc, nr, T)`.
- `bch_ioc_wr<T>(nr)` computes `_IOWR(0xbc, nr, T)`.

Use:
- Shared by command and wrapper modules that manually issue bcachefs ioctls with Rust-defined struct layouts.

Potential concerns:
- Direction/type/number constants are Linux ioctl ABI-specific.
