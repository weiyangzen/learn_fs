# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/ioctl.h

Purpose: small header declaring the VFS file ioctl entry points.

Key contents:
- `bch2_fs_file_ioctl(struct file *, unsigned, unsigned long)`
- `bch2_compat_fs_ioctl(struct file *, unsigned, unsigned long)`

Important interactions:
- Included by `fs.c` to attach ioctl handlers to file and directory `file_operations`.
- Included by `ioctl.c` as its implementation contract.
