# File Research: sources/block-storage/lvm2/lib/misc/lvm-flock.c

This file implements flock-based lock-file management with optional write-lock prioritization.

Main entry points:
- `init_flock()`: initializes lock list and reads `global_prioritise_write_locks`.
- `lock_file()`: acquire, convert, or release read/write locks.
- `release_flocks()`: releases all tracked locks.

Implementation details:
- Tracks locks in `_lock_list` as resource path plus fd.
- `_do_flock()` opens/creates lock file, takes flock, and validates fd inode against path inode to avoid races.
- Blocking locks temporarily allow SIGINT via `sigint_allow()`/`sigint_restore()`.
- `_do_write_priority_flock()` uses an auxiliary `:aux` lock file so write locks can serialize ahead of readers.
- `_undo_flock()` takes exclusive lock, verifies inode, unlinks lock file, and closes fd.

Dependencies:
- LVM lock flag constants, signal helpers, config, `is_same_inode`.

Correctness notes:
- `LCK_CONVERT` uses existing lock entry and calls `flock()` on the same fd.
- Releasing with `unlock=0` only closes shared fd without unlink/unlock cleanup.

Risks:
- Lock files are unlinked when no longer used; behavior assumes all participants follow the same protocol.
- Signal interruption during blocking flock causes “Giving up waiting for lock.”
