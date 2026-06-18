# File Research: sources/block-storage/util-linux/libmount/src/tab_update.c

## Scope

Implements libmount's userspace mount-table update abstraction, centered on `struct libmnt_update`. It prepares and applies updates to the private utab file, writes/replaces fstab-like tables, handles mount/umount/move/remount update cases, and emits activity/event files used by libmount monitoring.

## Public And Internal APIs Covered

- Lifecycle: `mnt_new_update()`, `mnt_free_update()`.
- Update setup: `mnt_update_set_filename()`, `mnt_update_get_filename()`, `mnt_update_set_fs()`, `mnt_update_get_fs()`, `mnt_update_get_mflags()`, `mnt_update_is_ready()`, `mnt_update_force_rdonly()`.
- Table writing: `mnt_table_write_file()`, `mnt_table_replace_file()`.
- Update execution: `mnt_update_table()`, `mnt_update_already_done()`.
- Event/activity coordination: `mnt_update_emit_event()`, `mnt_update_start()`, `mnt_update_end()`.
- Internal operations: `utab_new_entry()`, `set_fs_root()`, `update_add_entry()`, `update_remove_entry()`, `update_modify_target()`, `update_modify_options()`, `update_add_options()`.

## Control Flow And Behavior

- `mnt_update_set_fs()` resets the update object and classifies the operation:
  - `target` with no `fs` means umount/removal.
  - `fs` with normal mount flags prepares a new utab entry.
  - `MS_MOVE` copies an mtab-style fs template for later target rewriting.
  - `MS_REMOUNT` prepares option modification.
  - propagation-only flags return `1` because no utab update is needed.
- `utab_new_entry()` extracts only mtab-visible userspace options, preserves attributes, and skips utab creation when no user options or attributes exist.
- `set_fs_root()` uses `/proc/self/mountinfo` for bind mounts and btrfs/auto cases to resolve source path, filesystem type, bind source, and root.
- `update_table()` writes a temporary unique file, serializes entries with `fprintf_utab_fs()`, flushes, chmods, copies ownership from the old file when present, and atomically renames.
- `mnt_table_write_file()` and `mnt_table_replace_file()` serialize fstab/mtab-style entries with mangled source, target, fstype, options, freq, passno, and comments.
- `mnt_update_table()` locks the utab file and dispatches to remove/add/move/remount/missing-option update paths.
- `mnt_update_already_done()` detects whether a helper already added/removed an entry; for mounts it also marks `missing_options` if helper-written options do not contain all expected userspace options.
- `mnt_update_start()` creates and shared-locks `<utab>.act` so monitors can suppress intermediate kernel events; `mnt_update_end()` unlocks and removes the activity file only when no other shared users remain.

## State And Data Structures

- `struct libmnt_update` stores target, prepared fs, utab filename, mount flags, activity-file fd/name, readiness flags, parsed mountinfo, and an optional lock.
- Utab entries are serialized as key-value fields: `ID`, `UNIQID`, `SRC`, `TARGET`, `ROOT`, `BINDSRC`, `ATTRS`, and `OPTS`.

## Dependencies

- libmount fs/table/cache/lock helpers from `mountP.h`.
- Option filtering from `mnt_optstr_get_options()` and `mnt_optstr_get_missing()`.
- Path and table sources including `/proc/self/mountinfo`, utab path detection, and mangle/unmangle helpers.
- POSIX file APIs: `mkstemp`, `fdopen`, `fflush`, `fchmod`, `fchown`, `rename`, `flock`, `umask`.

## Risks And Invariants

- The update object must only be marked ready after filename and operation state are valid.
- Atomic replacement depends on successful write/flush/metadata setup before `rename()`.
- File locking is required around read-modify-write table updates.
- Move updates rewrite targets whose paths begin with the old source target and preserve subpaths.
- Activity-file deletion is coordinated with advisory locks to avoid removing an in-use marker.
