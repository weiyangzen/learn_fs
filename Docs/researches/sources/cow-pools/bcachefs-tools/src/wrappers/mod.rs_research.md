# File Research: sources/cow-pools/bcachefs-tools/src/wrappers/mod.rs

Declares wrapper submodules and provides two shared helpers.

Exports:
- `accounting`, `bdev`, `handle`, `ioctl`, `sb_display`, `super_io`, and `sysfs`.

Helpers:
- `bch_err_str` converts a bcachefs error code to a lossy Rust string via C `bch2_err_str`.
- `SbLockGuard` is an RAII wrapper around the bcachefs superblock pthread mutex.
- `sb_lock` locks `fs->sb_lock.lock` and returns the guard.

Potential concerns:
- `sb_lock` is unsafe and assumes the `bch_fs` pointer and embedded mutex layout are valid.
- `pthread_mutex_lock` return value is ignored.
