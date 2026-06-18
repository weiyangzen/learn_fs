# File Research: sources/cow-pools/bcachefs-tools/include/linux/dcache.h

This header provides a minimal `struct dentry` for user-space code, containing `d_sb`, `d_inode`, an `is_debugfs` bit, and a name pointer. It forward-declares `struct super_block` and `struct inode`.

`shrink_dcache_sb()` is a no-op. It also defines `QSTR_INIT` and `QSTR()` helpers for constructing `struct qstr` values, relying on `strlen()` and the `qstr` definition from the broader compatibility layer.
