# sources/distributed-fs/ceph-client/fs/ocfs2/locks.c

## Purpose
`locks.c` implements userspace file locking support for OCFS2. It maps BSD `flock()` operations onto OCFS2 file cluster locks plus VFS lock bookkeeping, and maps POSIX byte-range locks to the cluster stack's plock implementation.

## Important APIs, types, and functions
- `ocfs2_flock()` handles `FL_FLOCK` requests, using local VFS locks for local mounts or `localflocks`, and cluster-aware helpers otherwise.
- `ocfs2_lock()` handles `FL_POSIX` requests through `ocfs2_plock()`.
- `ocfs2_do_flock()` serializes per-file flock state with `fp_mutex`, converts existing cluster flock levels by unlocking first, obtains an OCFS2 file lock, then installs the VFS lock.
- `ocfs2_do_funlock()` releases the OCFS2 file lock and then updates VFS lock state.

## Control flow
For clustered flock, the code chooses PR/EX-like level from lock type and trylock behavior from `SETLK` versus `SETLKW`. If a lock resource is already attached at a different level, it first installs an unlock request in the VFS lock layer and releases the OCFS2 file lock because conversion is not guaranteed atomic. It then obtains the desired cluster file lock and calls `locks_lock_file_wait()`. If VFS locking fails, it releases the cluster lock.

## State and persistence behavior
There is no persistent disk state. Runtime state lives in `struct ocfs2_file_private`, especially `fp_flock` and `fp_mutex`, plus VFS file lock state and DLM/plock state in the cluster stack.

## Dependencies and integration points
The file depends on Linux file locking APIs, OCFS2 file-private state, DLM glue, mount options, and cluster connection plock support. It is wired into OCFS2 file operations through the regular and no-plock operation tables selected at inode population time.

## Risks and edge cases
- Flock conversion is explicitly non-atomic; there is a window between unlock and relock.
- Nonblocking flock maps `-EAGAIN` to `-EWOULDBLOCK`.
- Local mounts and `OCFS2_MOUNT_LOCALFLOCKS` intentionally bypass cluster locks.
- `ocfs2_lock()` requires `FL_POSIX`; passing other lock types returns `-ENOLCK`.

## Test signals
Exercise flock shared/exclusive/unlock, blocking and nonblocking contention across nodes, conversion from shared to exclusive, localflocks/local mount bypass, POSIX byte-range lock propagation through plocks, and VFS failure rollback of cluster flock state.
