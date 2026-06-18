# File Research: sources/block-storage/lvm2/lib/misc/lvm-file.h

This header declares file utility APIs and small macros.

Content:
- `struct custom_fds` for output/error/report descriptors.
- Temp file, rename, existence, directory creation, directory sync, fcntl lock, fclose, and ctime helpers.
- `is_same_inode(buf1, buf2)` compares inode and device.
- `is_valid_fd(fd)` checks `F_GETFD`.
- Defines `timespeccmp` fallback for BSD-like compatibility.

Dependencies:
- `<stddef.h>`, `<stdio.h>`, `<time.h>`, `<sys/stat.h>` and fcntl usage via macro.

Role:
- Common file/lock helper interface for metadata and command code.
