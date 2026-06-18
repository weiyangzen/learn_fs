# File Research: sources/block-storage/lvm2/libdm/libdm-file.c

## Purpose

`libdm-file.c` contains small filesystem and lockfile utilities used by libdevmapper and device-mapper userspace tooling. It handles recursive directory creation, empty-directory detection, reliable `fclose()` error reporting, PID lockfile creation, and daemon-running checks through advisory locks.

## Main Functions

- `_is_dir()`
  - Uses `stat()` to verify an existing path is a directory.
  - Logs an error for non-directory paths.
- `_create_dir_recursive()`
  - Creates each missing parent directory in a path using `mkdir(..., 0777)`.
  - Accepts existing directories.
  - Fails on existing non-directories.
  - Suppresses noisy logging for `EROFS`.
- `dm_create_dir()`
  - Public wrapper that treats an empty string as success.
  - Returns success if the directory already exists.
  - Falls back to recursive creation.
- `dm_is_empty_dir()`
  - Opens a directory and returns true only if it contains no entries other than `.` and `..`.
- `dm_fclose()`
  - Combines prior stream error state from `ferror()` with the result of `fclose()`.
  - Clears `errno` when only a prior stream error existed but `fclose()` itself succeeded.
- `dm_create_lockfile()`
  - Opens/creates a lockfile.
  - Acquires a write lock with `fcntl(F_SETLK)`.
  - Retries transient `EACCES`/`EAGAIN` lock conflicts up to 20 times with 1 ms sleeps.
  - Truncates the file, writes the current PID, and sets `FD_CLOEXEC`.
  - Intentionally leaves the file descriptor open to keep the lock held.
  - Unlinks and closes on failure after lock acquisition.
- `dm_daemon_is_running()`
  - Opens an existing lockfile and uses `fcntl(F_GETLK)` to determine whether another process holds a write lock.

## Behavior Details

Recursive directory creation duplicates the input path, temporarily inserts null terminators at `/` boundaries, and attempts to create each component. It skips the empty prefix so absolute paths are handled correctly.

The lockfile API uses POSIX advisory locks rather than just PID-file contents. The PID is written for observability, but process liveness is inferred from the kernel lock state. `dm_create_lockfile()` deliberately leaks the locked fd on success; the lock is released by process exit or explicit descriptor close elsewhere.

## Dependencies

- Includes `libdm/misc/dmlib.h` for logging and memory helpers.
- Uses POSIX filesystem APIs:
  - `stat`
  - `mkdir`
  - `opendir`
  - `readdir`
  - `closedir`
  - `open`
  - `fcntl`
  - `ftruncate`
  - `write`
  - `close`
  - `unlink`
  - `usleep`

## Notable Edge Cases

- `dm_create_dir("")` returns success.
- `dm_is_empty_dir()` returns false when `opendir()` fails.
- `dm_fclose()` preserves the important distinction between buffered stream errors and close errors.
- `dm_create_lockfile()` treats `EINTR` during lock acquisition by retrying immediately.
- `dm_daemon_is_running()` returns false if the lockfile cannot be opened.
