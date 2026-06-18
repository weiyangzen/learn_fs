# File Research: sources/block-storage/lvm2/lib/misc/lvm-flock.h

This header declares the flock helper interface.

APIs:
- `init_flock(struct cmd_context *cmd)`.
- `lock_file(const char *file, uint32_t flags)`.
- `release_flocks(int unlock)`.

Dependencies:
- `<stdint.h>` and forward-declared `cmd_context`.

Role:
- Used by higher-level locking code to manage local file locks.
