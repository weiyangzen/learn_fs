# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_share_nfs.c

This file implements common NFS exports-file update helpers used by the NFS sharing backend. It provides locking, temporary-file replacement, mountpoint escaping, exports scanning, and reset behavior.

Primary responsibilities:
- Serialize updates to an exports file with `flock()`.
- Rewrite generated exports content atomically using a temporary file plus `rename()`.
- Escape mountpoints containing whitespace or backslashes for NFS exports syntax.
- Scan exports files and identify entries matching a mountpoint.
- Copy exports entries while omitting an entry for a target mountpoint.
- Truncate generated exports state under lock.

Important functions:
- `nfs_exports_lock()` opens/creates the lockfile and obtains an exclusive flock, retrying on `EINTR`.
- `nfs_exports_unlock()` releases the flock, closes the fd, and resets the fd to `-1`.
- `nfs_init_tmpfile()` optionally creates the exports directory, creates a `mkostemp()` temp file based on the exports path, and wraps it in `FILE *`.
- `nfs_abort_tmpfile()` unlinks and closes a temp file after failure.
- `nfs_fini_tmpfile()` flushes, renames the temp file over the exports file, chmods it to `0644`, and closes it.
- `nfs_escape_mountpoint()` returns either the original mountpoint or a newly allocated escaped string where whitespace/backslash characters become octal escapes.
- `nfs_process_exports()` opens the exports file, escapes the target mountpoint, reads lines with `getline()`, skips blank/comment lines, and invokes a callback with a match flag.
- `nfs_copy_entries_cb()` writes through nonmatching lines.
- `nfs_copy_entries()` emits `NFS_FILE_HEADER`, then copies all existing entries except the target mountpoint.
- `nfs_toggle_share()` is the core update routine: create temp file, lock exports, copy old entries minus target, invoke caller callback to add/remove/update target entry, rename temp file, unlock.
- `nfs_reset_shares()` locks and truncates the exports file.
- `nfs_is_shared_impl()` scans exports and returns true if the mountpoint exists.

Data structures:
- `struct tmpfile` stores a short temp filename buffer and the open `FILE *`.

Important behavior:
- Temporary filename buffer is fixed at 64 bytes, based on the comment that the target exports path plus suffix is bounded in this usage.
- Exports parsing matches the mountpoint only as the first token ending at whitespace/newline.
- `nfs_process_exports()` ignores callback output for blank/comment lines; those lines are not passed to callbacks.
- File update uses `rename()` for atomic replacement after writing.
- If `fdopen()` fails after `mkostemp()`, the fd is closed but the temp path is not unlinked in that local failure path.

Dependencies:
- `libzfs_impl.h` and `libzfs_share.h` declarations.
- `libzutil` for `zfs_strerror()`.
- POSIX file APIs: `open`, `flock`, `mkostemp`, `fdopen`, `getline`, `rename`, `truncate`, `fchmod`.

Research relevance:
- This file shows the userland persistence pattern for generated NFS shares: lock, rewrite filtered exports, atomically replace, and commit/reset through backend-specific hooks.
