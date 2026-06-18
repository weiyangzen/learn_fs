# sources/distributed-fs/openafs/src/afs/LINUX/osi_misc.c

## Purpose
This file contains Linux miscellaneous OSI helpers: signal masking, pathname lookup, absolute path resolution, kernel thread startup wrappers, and fatal-signal detection.

## Important APIs, types, and functions
- `osi_linux_mask` blocks all signals for the current task.
- `osi_linux_unmaskrxk` unblocks `SIGKILL` for the RX kernel listener task during shutdown.
- `osi_lookupname_internal` resolves a kernel pathname to dentry/mount references.
- `osi_lookupname` handles user/kernel path strings and returns a dentry.
- `osi_abspath` resolves a user pathname and formats its absolute path with `d_path`.
- `afs_start_thread` starts a named kernel thread with optional `AFS_GLOCK` around the target function.
- `osi_kill_pending` reports fatal pending signals when the kernel provides `fatal_signal_pending`.

## Control flow and behavior
Path lookup uses `afs_getname` for user paths, copying through `strncpy_from_user` into a kernel name buffer with `PATH_MAX` validation. `osi_lookupname_internal` builds lookup flags with `LOOKUP_FOLLOW` as requested, calls `afs_kern_path`, then extracts dentry/mount references with compatibility helpers. `osi_abspath` resolves a path, calls `afs_d_path`, stores the returned pointer in the caller output, releases references, and frees the copied name.

Thread startup wraps the requested `void (*)(void)` in a kthread function that increments the module reference count, optionally takes `AFS_GLOCK`, runs the function, drops locks/reference, and exits. Signal mask helpers use `SIG_LOCK` and `RECALC_SIGPENDING`.

## State and persistence
The file mutates the current task's signal mask and may mutate the RX listener task signal mask. It starts kernel threads and temporarily increments module references. It stores no persistent file or module state beyond globals declared elsewhere (`afs_osi_cred`, `afs_osicred_initialized`).

## Dependencies and integration points
It depends on Linux dcache/namei/kthread/signal APIs, `osi_compat.h` path helpers, OpenAFS global locking, RX listener task state, and module reference management. Lookup helpers are used by cache initialization and other path-based AFS operations.

## Risks
`afs_start_thread` does not check `kthread_run` failure, so thread start failure can be silent. Signal mask manipulation on another task (`rxk_ListenerTask`) assumes that pointer remains valid. Pathname copies from userspace must preserve negative errno conversion exactly. `osi_abspath` returns a pointer into the caller-supplied buffer after releasing dentry/mount references, which is normal for `d_path` but requires caller buffer lifetime.

## Test signals
Test user and kernel pathname lookup, follow/no-follow behavior, `ENAMETOOLONG` and bad pointer cases, absolute path formatting, kthread startup with and without `AFS_GLOCK`, module unload sequencing, RX listener shutdown signal unmasking, and fatal-signal detection.
