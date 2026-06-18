# File Research: sources/block-storage/lvm2/lib/locking/file_locking.c

## Purpose
Implements the file-locking backend for LVM metadata locks. It maps LVM lock resources to lock files under the configured locking directory and connects the generic locking dispatch table to flock-based helpers.

## Main Responsibilities
- Stores the configured lock directory in `_lock_dir`.
- Releases all or command-held flocks through `_fin_file_locking` and `_reset_file_locking`.
- Builds lock filenames with `P_` prefix for the global lock and `V_` prefix for VG locks.
- Calls `lock_file` with LVM lock flags to acquire, convert, or release file locks.
- Initializes flock support, fills `struct locking_type`, creates the lock directory with SELinux context handling, and rejects read-only lock directories.

## Important Control Flow
`init_file_locking` reads `global/locking_dir`, validates/copies it, prepares SELinux directory context, creates the directory, checks for read-only filesystem access failure, and installs `_file_lock_resource` plus reset/finalize callbacks in the generic locking backend.

## Dependencies
Depends on `locking.h`, `locking_types.h`, metadata constants such as `VG_GLOBAL`, config lookup, string helpers, directory creation helpers, SELinux context helpers, and `lib/misc/lvm-flock.h`.

## Risk Notes
Lock file path construction must remain bounded by `PATH_MAX`. The global lock uses `resource + 1` to strip the leading `#` from `#global`, so resource naming conventions are part of the backend contract.
