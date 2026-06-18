# sources/distributed-fs/ceph-client/fs/dlm/user.c

## Purpose
`user.c` implements the DLM userspace device ABI. It provides the `dlm-control` misc device for lockspace create/remove, per-lockspace misc devices for lock/unlock/deadlock/purge requests and AST reads, and a `dlm-monitor` device used to detect userspace daemon availability.

## Important APIs, Types, And Functions
Key exports are `dlm_user_add_ast()`, `dlm_user_init()`, `dlm_user_exit()`, `dlm_device_deregister()`, and `dlm_user_daemon_available()`. Important internal functions include compat translators, `device_write()`, `device_read()`, `device_open()`, `device_close()`, `device_create_lockspace()`, `device_remove_lockspace()`, `device_user_lock()`, `device_user_unlock()`, `device_user_deadlock()`, `device_user_purge()`, and `copy_result_to_user()`.

## Control Flow
Control-device writes create or remove lockspaces after `CAP_SYS_ADMIN` checks. Creating a lockspace calls `dlm_new_user_lockspace()`, finds the lockspace, registers a per-lockspace misc device named `dlm_<name>`, and returns the minor. Removing looks up by minor, optionally force-frees, and calls `dlm_release_lockspace()`.

Per-lockspace device open allocates `struct dlm_user_proc`, initializes AST/lock/unlocking lists and waitqueue, and holds a lockspace reference. Writes validate the device ABI version, handle compat 32-bit input when needed, reject operations after close starts, and dispatch to core user lock functions. Reads either return ABI version information or block until an AST/callback is available; callback data is copied as `struct dlm_lock_result` plus optional LVB bytes.

`dlm_user_add_ast()` is called from lock/AST code. It suppresses callbacks for orphan/dead locks, marks end-of-life locks after terminal completion statuses, obtains/skips callback records through `ast.c`, snapshots user args and optional LVB data, queues callbacks on the process AST list, wakes readers, and removes EOL locks from the process lock list.

Monitor-device open/close tracks whether `dlm_controld` is live. When the final monitor fd closes, `dlm_stop_lockspaces()` is invoked.

## State And Persistence
State is in misc-device registrations, per-open `dlm_user_proc` structures, queued `dlm_callback` records, per-process lock lists, monitor open counters, and per-lockspace device names. It is volatile kernel memory tied to open file and lockspace lifetimes.

## Dependencies And Integration Points
This file integrates with UAPI headers `linux/dlm_device.h` and `linux/dlm.h`, lockspace creation/lookup, lock operations in `lock.c`, AST helpers in `ast.c`, LVB operation policy, config cluster name, memory allocators, miscdevice, poll/waitqueue, compat ABI, and tracepoints.

## Risks
The userspace ABI has strict struct size/version rules and compat pointer translation. AST delivery races with process close are guarded by `ls_clear_proc_locks` and lock flags; mistakes can use freed `lkb_ua`. End-of-life lock removal must match terminal status semantics. Device registration failure after lockspace creation must release the lockspace.

## Test Signals
Test ABI version reads, 32-bit compat requests, lock/convert/unlock/cancel/deadlock/purge commands, blocking and nonblocking AST reads, LVB copy sizing, process close with outstanding locks, control-device permission checks, monitor open/close behavior, and daemon-availability checks.
