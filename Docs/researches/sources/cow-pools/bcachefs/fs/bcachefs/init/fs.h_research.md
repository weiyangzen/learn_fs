# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/fs.h

This header declares filesystem lifecycle, global fs lookup, read-only/read-write, resize, and open APIs.

Key elements:
- `KTYPE(type)` macro builds kobject type boilerplate from per-type attributes, release function, and sysfs ops.
- Exports string tables for filesystem flags, filesystem write refs, and device read/write refs.
- Exports global `bch2_fs_list` and `bch2_fs_list_lock`.
- Declares UUID lookup:
  - `__bch2_uuid_to_fs()`
  - `bch2_uuid_to_fs()`
- Declares emergency/read-only/read-write APIs.
- Declares RW init and mount-time resize.
- Declares missing-device formatting and start/stop/exit/open functions.

Role:
- Shared by init, chardev, error, logged-ops, recovery, and VFS-facing code that needs filesystem lifecycle control.
