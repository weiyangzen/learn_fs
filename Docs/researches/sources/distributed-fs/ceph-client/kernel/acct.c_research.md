# sources/distributed-fs/ceph-client/kernel/acct.c

## Purpose
`acct.c` implements BSD process accounting. When enabled through the `acct()` syscall, the kernel writes a compact `acct_t` record for exiting processes to a configured regular file. It handles enabling/disabling accounting per PID namespace, accounting file lifetime across mounts, free-space based pause/resume, record encoding, and collection of per-process CPU, memory, fault, UID/GID, TTY, and exit information.

## Important APIs, types, and functions
The central state is `struct bsd_acct_struct`, which contains an `fs_pin`, refcount, RCU head, mutex, active/check-space flags, next check time, accounting file, PID namespace, close work item, completion, and reusable `acct_t` record buffer. `acct_on()` opens and validates the target file, clones an internal mount, allocates state, inserts the fs pin, and atomically swaps `ns->bacct`. `SYSCALL_DEFINE1(acct)` enforces `CAP_SYS_PACCT` and enables or disables accounting.

Lifetime helpers include `acct_get()`, `acct_put()`, `acct_pin_kill()`, `close_work()`, and `acct_exit_ns()`. Record helpers include `fill_ac()`, `acct_write_process()`, `do_acct_process()`, `acct_collect()`, `slow_acct_process()`, and `acct_process()`. Encoding helpers implement legacy compressed fields: `encode_comp_t()`, `encode_comp2_t()`, and `encode_float()` depending on `ACCT_VERSION`.

## Control flow
Enabling accounting opens the user path with `O_WRONLY|O_APPEND|O_LARGEFILE`, rejects non-regular, internal, procfs/sysfs-visible, or non-writable files, builds an internal mount-backed file, and installs a new pin in the active PID namespace. Replacing a file kills the previous pin. Disabling accounting calls `pin_kill()` on the namespace's active pin.

On process exit, `acct_collect()` accumulates signal-shared accounting fields while holding `siglock`; for the last thread it walks VMAs under `mmap_read_lock()` to compute memory use. `acct_process()` walks the current PID namespace and its parents, obtains each active accounting state with RCU/refcount protection, fills the record, temporarily removes `RLIMIT_FSIZE`, writes under the file owner's credentials, and restores the limit. Free space is checked periodically by `check_free_space()`, which toggles active state according to sysctl-controlled resume/suspend thresholds.

## State and persistence behavior
Persistent output is the append-only accounting file. Runtime state is per PID namespace via `ns->bacct`, protected by RCU, mutexes, fs pins, and atomic references. The fs pin prevents unsafe unmount/remount interactions; if the mount is killed, `acct_pin_kill()` writes a final record for the current task, schedules synchronous close work, clears `ns->bacct`, removes the pin, and releases the state.

## Dependencies and integration points
The file integrates with sysctl (`kernel.acct`), syscall dispatch, capabilities, PID namespaces, VFS open/write/statfs/freeze protection, mount pinning, workqueues, RCU, task signal accounting, credentials, TTY handling, time conversion, and user namespace UID/GID mapping.

## Risks and invariants
Key risks are lifetime races around `ns->bacct`, mount teardown, and concurrent file replacement. The lock order around `acct_on_mutex`, per-accounting mutex, RCU, and fs pins must be preserved. Writes intentionally bypass `RLIMIT_FSIZE` and use the opener's credentials; regressions here can break ABI expectations. Free-space logic must avoid writing to frozen filesystems and must not deadlock during unmount or remount.

## Test signals
Test enabling/disabling accounting with valid and invalid files, replacing the active file, PID namespace parent accounting, mount unmount/remount while accounting is active, low-space pause/resume thresholds, exiting multithreaded processes, UID/GID mapping, and all supported `ACCT_VERSION` encodings. Lockdep, KASAN, and fault injection around allocation/open/write paths are useful.
