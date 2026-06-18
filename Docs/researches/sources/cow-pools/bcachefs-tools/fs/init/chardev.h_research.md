# File Research: sources/cow-pools/bcachefs-tools/fs/init/chardev.h

## Purpose
Public header for bcachefs character-device ioctl integration, with no-op stubs when filesystem support is disabled.

## Main Contents
- Under normal builds:
  - `bch2_copy_ioctl_err_msg()`
  - `bch2_fs_ioctl()`
  - per-filesystem chardev init/exit
  - module/global chardev init/exit
- Under `NO_BCACHEFS_FS`:
  - `bch2_fs_ioctl()` returns `-ENOTTY`
  - init/exit functions are empty success/no-op stubs.

## Integration Notes
Filesystem initialization calls the init/exit functions to publish or remove control devices. VFS ioctl paths and global character-device file ops call `bch2_fs_ioctl()` for command dispatch.

## Risks and Edge Cases
- Callers must tolerate `-ENOTTY` in `NO_BCACHEFS_FS` builds.
- The header intentionally hides all implementation details; lifetime and permission checks live in `chardev.c`.
