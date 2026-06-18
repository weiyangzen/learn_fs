# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/chardev.h

This header declares the chardev ioctl interface and provides no-op fallbacks when filesystem support is disabled.

Key elements:
- Declares:
  - `bch2_copy_ioctl_err_msg()`
  - `bch2_fs_ioctl()`
  - per-filesystem chardev init/exit
  - global chardev init/exit
- Under `NO_BCACHEFS_FS`, `bch2_fs_ioctl()` returns `-ENOTTY` and init/exit helpers are no-ops.

Role:
- Used by filesystem lifecycle code to register control devices and by VFS paths that route ioctl requests.
