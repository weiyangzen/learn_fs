# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/ioctl.h

Declares the bcachefs VFS ioctl entry points.

Key declarations:
- `bch2_fs_file_ioctl()` handles native file ioctls.
- `bch2_compat_fs_ioctl()` handles supported compat ioctls when `CONFIG_COMPAT` is enabled by callers.

Filesystem relevance:
- This header connects file and directory operation tables in `fs.c` to the ioctl implementation in `ioctl.c`.
