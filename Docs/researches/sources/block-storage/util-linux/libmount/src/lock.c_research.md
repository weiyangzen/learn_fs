# File Research: sources/block-storage/util-linux/libmount/src/lock.c

This file implements libmount file locking. Since util-linux v2.39, libmount uses `flock()` only rather than classic mtab locking.

Key APIs:

- `mnt_new_lock(datafile, id)` creates a lock object whose lock path is `<datafile>.lock`; `id` is ignored.
- `mnt_ref_lock()`, `mnt_unref_lock()`, and `mnt_free_lock()` implement reference-counted lifecycle.
- `mnt_lock_block_signals()` configures signal blocking while a lock is held.
- `mnt_lock_file()` acquires an exclusive flock.
- `mnt_unlock_file()` releases the lock, closes the FD, clears state, and restores signal masks.

Important behavior:

- Lock files are opened with `O_RDONLY|O_CREAT|O_CLOEXEC` and mode `0600`; mode is corrected with `fchmod()` if needed.
- If signal blocking is enabled, all signals are blocked before opening/flocking and the previous mask is restored on error or unlock.
- `flock(LOCK_EX)` retries on `EAGAIN` and `EINTR`.
- The lock object records whether it currently owns a lock and the lockfile FD.

Dependencies and interactions:

- Used by update-table code for files such as `/run/mount/utab`.
- Debug output uses the lock debug mask from `init.c`.
- The optional test program runs concurrent lock/increment cycles.

Risk notes:

- `mnt_free_lock()` does not unlock; callers should call `mnt_unlock_file()` or use the reference lifecycle carefully.
- If a process exits while holding an FD lock, the kernel releases it, but the lock file remains.
