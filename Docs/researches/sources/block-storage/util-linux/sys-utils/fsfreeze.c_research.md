# File Research: sources/block-storage/util-linux/sys-utils/fsfreeze.c

Purpose: Implements `fsfreeze(8)`, a small Linux utility that freezes or thaws a mounted filesystem through VFS ioctls.

Core behavior:
- Accepts exactly one action, `--freeze` or `--unfreeze`, enforced as mutually exclusive.
- Requires a single mountpoint argument, opens it read-only, verifies it is a directory, and then issues `ioctl(fd, FIFREEZE, 0)` or `ioctl(fd, FITHAW, 0)`.
- Reports open/stat/ioctl failures with util-linux translated diagnostics and exits success only after the selected ioctl succeeds.

Dependencies and integration:
- Uses Linux `FIFREEZE`/`FITHAW` definitions from `<linux/fs.h>`.
- Uses util-linux common CLI helpers (`optutils.h`, `closestream.h`, `nls.h`) and is documented as `fsfreeze(8)`.

Risks and edge cases:
- It validates that the path is a directory, not that it is the root of a mount; the kernel ioctl decides whether the target is a valid freeze point.
- The file includes `blkdev.h` but does not use block-device helpers directly.
