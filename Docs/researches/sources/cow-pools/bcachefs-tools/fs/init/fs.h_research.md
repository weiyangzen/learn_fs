# File Research: sources/cow-pools/bcachefs-tools/fs/init/fs.h

Public lifecycle header for filesystem superblock/open/start/stop and RO/RW operations.

Key contents:
- Defines `KTYPE(type)`, a helper macro for constructing kobject type metadata from local release/sysfs/files symbols.
- Declares string tables:
  - `bch2_fs_flag_strs`
  - `bch2_write_refs`
  - `bch2_dev_read_refs`
  - `bch2_dev_write_refs`
- Declares the global open-filesystem list and lock:
  - `bch2_fs_list`
  - `bch2_fs_list_lock`
- Declares UUID lookup:
  - `__bch2_uuid_to_fs()`
  - `bch2_uuid_to_fs()`
- Declares emergency and normal RO/RW transitions:
  - `bch2_fs_emergency_read_only()`
  - `bch2_fs_emergency_read_only_locked()`
  - `bch2_fs_read_only()`
  - `bch2_fs_read_write()`
  - `bch2_fs_read_write_early()`
  - `bch2_fs_init_rw()`
- Declares resize-on-mount, missing-device formatting, lifecycle start/stop/exit, and open:
  - `bch2_fs_resize_on_mount()`
  - `bch2_missing_devs_to_text()`
  - `bch2_fs_start()`
  - `bch2_fs_stop()`
  - `bch2_fs_exit()`
  - `bch2_fs_open()`

Role:
- This is the cross-subsystem API for mounting/opening, startup, shutdown, read-only emergency handling, and RW enabling.
- Included by recovery, journal, and other subsystems that need to force RO, start RW early, or inspect lifecycle state.
