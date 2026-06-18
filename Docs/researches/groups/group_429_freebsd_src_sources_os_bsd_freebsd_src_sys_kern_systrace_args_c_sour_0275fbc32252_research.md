# Group Research: group_429_freebsd_src_sources_os_bsd_freebsd_src_sys_kern_systrace_args_c_sour_0275fbc32252

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/freebsd-src`, and all files in this group are under that source tree. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/systrace_args.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/systrace_args.c

## Purpose

`systrace_args.c` is an automatically generated DTrace syscall-provider helper. It does not implement syscall behavior. It translates FreeBSD syscall argument structs and syscall metadata into uniform DTrace-visible argument arrays and textual type descriptions.

The file explicitly says it is generated and should not be edited by hand.

## Structure

The file contains three static functions:

- `systrace_args(int sysnum, void *params, uint64_t *uarg, int *n_args)`
- `systrace_entry_setargdesc(int sysnum, int ndx, char *desc, size_t descsz)`
- `systrace_return_setargdesc(int sysnum, int ndx, char *desc, size_t descsz)`

Each function is a large `switch (sysnum)` table covering the same 422 syscall case labels, from syscall number `0` through the highest listed syscall `602` (`renameat2`). Sparse syscall numbers are intentionally omitted or grouped according to the generated syscall table.

## `systrace_args()`

`systrace_args()` converts a syscall-specific argument struct into a DTrace register-style argument vector:

- Casts `uarg` to both unsigned and signed views:
  - `uint64_t *uarg`
  - `int64_t *iarg = (int64_t *)uarg`
- Uses an incrementing index `a`.
- For each syscall with arguments:
  - Casts `params` to `struct <syscall>_args *`.
  - Copies integer-like signed values into `iarg[a++]`.
  - Copies unsigned sizes, flags, and pointer addresses into `uarg[a++]`.
  - Casts user pointers through `(intptr_t)` before storing.
  - Sets `*n_args` to the number of copied arguments.
- For syscalls without arguments, sets `*n_args = 0`.
- The `default` case also sets `*n_args = 0`.

The largest argument counts in the table are seven arguments, including `sendfile`, `afs3_syscall`, and several SCTP generic send/receive syscalls. Six-argument examples include `recvfrom`, `sendto`, `mmap`, `__sysctl`, `kevent`, `copy_file_range`, and `wait6`.

## `systrace_entry_setargdesc()`

`systrace_entry_setargdesc()` maps `(sysnum, argument_index)` to a human-readable entry argument type string. It mirrors the syscall argument table used by `systrace_args()`.

Important behavior:

- Initializes `const char *p = NULL`.
- Switches on syscall number.
- For each syscall with arguments, switches on `ndx`.
- Assigns strings such as:
  - `int`
  - `size_t`
  - `off_t`
  - `uid_t`
  - `userland const char *`
  - `userland void *`
  - `userland struct stat *`
  - `userland const struct timespec *`
- Copies the string with `strlcpy(desc, p, descsz)` only when `p != NULL`.
- Unknown syscall numbers or out-of-range indexes leave `desc` unchanged.

The generated descriptions preserve an important distinction between scalar kernel-visible values and userland pointers, which is useful for DTrace consumers and probe argument display.

## `systrace_return_setargdesc()`

`systrace_return_setargdesc()` maps syscall number and return-value index to return type descriptions.

Behavior:

- Uses `p = NULL` and a syscall-number switch.
- Most syscalls describe return indexes `0` and `1` identically.
- Common return descriptions include:
  - `int`
  - `ssize_t`
  - `void`
  - `void *`
  - `off_t`
  - `mode_t`
- Examples:
  - read/write style syscalls return `ssize_t`.
  - descriptor-creating syscalls commonly return `int`.
  - `mmap` and `shmat` return `void *`.
  - `_exit`, `thr_exit`, and `abort2` are described as `void`.
- Unknown syscalls or unsupported indexes leave `desc` unchanged.

## Dependencies and Integration

This file assumes the generated syscall argument structs, syscall numbers, and helper prototypes are available from the surrounding compilation unit or generated include context. It uses standard kernel string copying via `strlcpy()` but has no includes of its own in this generated body.

It is coupled tightly to the FreeBSD syscall table. Any syscall ABI change requires regeneration, not manual editing.

## Research Notes

This is metadata plumbing for observability. The main maintenance risk is stale generated output: mismatches between syscall numbers, `struct <name>_args` layout, and DTrace descriptions would cause incorrect tracing metadata rather than syscall execution bugs. Because all three generated switches must stay synchronized, regeneration from the canonical syscall definitions is the right update path.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/systrace_args.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sysv_ipc.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/sysv_ipc.c

## Purpose

`sysv_ipc.c` provides shared System V IPC support code used by System V message queues, shared memory, and semaphores. In this group, its most important role is the common `ipcperm()` discretionary permission check used by `sysv_msg.c`.

## SYSVSHM Stub Hooks

When `SYSVSHM` is not compiled in, the file defines hook pointers and wrappers for shared-memory lifecycle integration:

- `shmfork_hook`
- `shmexit_hook`
- `shmobjinfo_hook`
- `shmfork(struct proc *p1, struct proc *p2)`
- `shmexit(struct vmspace *vm)`
- `shmobjinfo(struct vm_object *obj, key_t *key, unsigned short *seq)`

The wrappers call hooks when present. `shmobjinfo()` defaults `key` and `seq` to zero for absent `sysvshm.ko`.

## `ipcperm()`

`ipcperm(struct thread *td, struct ipc_perm *perm, int acc_mode)` implements common System V IPC permission checks.

Permission model:

- If the caller is the creator or current owner (`cuid` or `uid`), it uses owner mode bits and grants `IPC_M`.
- If the caller is in the creator/current group (`cgid` or `gid`), it uses group mode bits.
- Otherwise, it uses other mode bits.
- Read/write permissions are derived from `IPC_R` and `IPC_W`.
- Although System V IPC mode bits can represent `IPC_M`, this implementation requires privilege for administrative rights unless the caller is owner/creator.

Privilege fallback:

- Missing `IPC_M` can be satisfied by `PRIV_IPC_ADMIN`.
- Missing `IPC_R` can be satisfied by `PRIV_IPC_READ`.
- Missing `IPC_W` can be satisfied by `PRIV_IPC_WRITE`.
- If DAC plus privilege covers all requested bits, the function returns `0`; otherwise it returns `EACCES`.

The comment notes MAC Framework checks are intentionally not embedded in `ipcperm()`. MAC checks are performed at primitive-specific entry points, complementing these discretionary checks.

## Compatibility Conversions

For older FreeBSD compatibility builds, the file converts between old and current IPC permission layouts:

- `ipcperm_old2new()`
- `ipcperm_new2old()`

For 32-bit compatibility builds, it converts between 32-bit user-visible structures and native kernel structures:

- `freebsd32_ipcperm_old_in()`
- `freebsd32_ipcperm_old_out()`
- `freebsd32_ipcperm_in()`
- `freebsd32_ipcperm_out()`

These conversions use field-by-field copies for credential IDs, mode, sequence, and key fields.

## Research Notes

This file is small but security-sensitive. Its central contract is that System V IPC objects share one DAC permission implementation, while subsystem-specific files add MAC, jail, accounting, object lifecycle, and syscall semantics. Changes to `ipcperm()` affect all System V IPC primitives.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sysv_ipc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sysv_msg.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/sysv_msg.c

## Purpose

`sysv_msg.c` implements FreeBSD System V message queues. It provides module initialization/unload, message queue allocation and removal, `msgctl`, `msgget`, `msgsnd`, `msgrcv`, sysctl visibility, jail scoping, MAC Framework hooks, RACCT accounting, and compatibility syscall wrappers.

It exposes the feature as:

- `FEATURE(sysv_msg, "System V message queues support")`
- Kernel module name: `sysvmsg`

## Core Data and Limits

The implementation stores message bodies in fixed-size segments and tracks them with header and map pools:

- `msgpool`: contiguous message data segment storage.
- `msgmaps`: segment free-list metadata.
- `msghdrs`: message header pool.
- `msqids`: message queue descriptor array.
- `msq_mtx`: global mutex for message queue state.
- `free_msgmaps`, `nfree_msgmaps`: free segment tracking.
- `free_msghdrs`: free message header list.

Default tunables and derived limits include:

- `MSGSSZ` default `8`
- `MSGSEG` default `2048`
- `MSGMAX = MSGSSZ * MSGSEG`
- `MSGMNB` default `2048`
- `MSGMNI` default `40`
- `MSGTQL` default `40`

`msginit()` validates that `msgssz` is a small power of two and that `msgseg <= 32767`.

Queue IDs are sequence/index encoded through macros such as `MSQID`, `MSQID_IX`, `MSQID_SEQ`, and FreeBSD IPC ID helpers used later in syscall paths.

## Module Lifecycle

`msginit()` allocates and initializes all global message queue pools, MAC labels, the mutex, jail OSD slot state, and syscall helper registrations.

`msgunload()` unregisters syscalls, refuses unload with `EBUSY` if any queue is active or locked, deregisters jail OSD state, destroys MAC labels, frees pools, and destroys `msq_mtx`.

`sysvmsg_modload()` dispatches module load/unload/shutdown events.

## Queue and Message Cleanup

`msg_freehdr(struct msg *msghdr)` releases all segments owned by a message header back to the segment free list, returns the header to `free_msghdrs`, and cleans MAC message state.

`msq_remove(struct msqid_kernel *msqkptr)` removes an entire queue:

- Subtracts RACCT counts and sizes from the queue credential.
- Releases the held credential.
- Frees every message header and its segments.
- Verifies `msg_cbytes` and `msg_qnum` reach zero.
- Sets `msg_qbytes = 0` to mark the queue slot free.
- Cleans MAC queue state.
- Wakes sleepers on the queue.

## Jail Scoping

System V message queues are jail-aware. The file uses an OSD jail slot, `msg_prison_slot`, to associate jails with a System V message queue root.

Key helpers:

- `msg_find_prison()` returns the queue root prison visible to a credential.
- `msq_prison_cansee()` permits visibility only when the queue credential prison matches the root prison or is a child.
- `msg_prison_check()`, `msg_prison_set()`, `msg_prison_get()`, and `msg_prison_remove()` implement jail parameter handling for `sysvmsg`.
- `msg_prison_cleanup()` removes queues owned by a jail when its independent System V message queue namespace is removed.

The jail parameter supports disabled, new, and inherited behavior, and legacy `allow.sysvipc` flags are mapped into this model.

## `msgctl`

`sys_msgctl()` handles user copyin/copyout around `kern_msgctl()`.

`kern_msgctl()` validates the queue ID and sequence, checks jail visibility, applies MAC checks, and implements:

- `IPC_RMID`: requires `IPC_M`, checks per-message MAC removal permissions, and calls `msq_remove()`.
- `IPC_SET`: requires `IPC_M`, checks privilege for increasing queue byte limits, caps to `msginfo.msgmnb`, rejects zero queue byte size, updates owner/group/mode/qbytes/ctime.
- `IPC_STAT`: requires `IPC_R`, returns queue metadata, hides keys across prison boundaries, and clears kernel pointers before returning to userland.

## `msgget`

`sys_msgget()` finds or creates queues.

Behavior:

- Rejects operation with `ENOSYS` if the caller has no visible System V message queue prison.
- For non-private keys, searches existing queues in the caller’s prison.
- Enforces `IPC_CREAT | IPC_EXCL`, permission checks, and MAC `msqget` checks.
- For creation, finds an unused and unlocked queue slot.
- Applies RACCT `RACCT_NMSGQ`.
- Initializes permissions, credential hold, sequence number, timestamps, byte limits, and queue pointers.
- Returns a sequence/index encoded IPC ID.

## `msgsnd`

`sys_msgsnd()` copies in the leading message type and delegates to `kern_msgsnd()`.

`kern_msgsnd()` performs:

- Jail visibility and queue ID/sequence validation.
- Write permission through `ipcperm(..., IPC_W)`.
- MAC queue send checks.
- RACCT reservation for queued message count and byte size.
- Resource checks for queue byte capacity, free segments, free headers, and `MSG_LOCKED`.
- Optional blocking with `msleep()` unless `IPC_NOWAIT` is set.
- Temporary queue locking with `MSG_LOCKED` while copying from userland.
- Segment allocation from `free_msgmaps`.
- Message type validation (`mtype >= 1`).
- Copyin of message body into `msgpool`.
- MAC message-to-queue enqueue check.
- Queue append, byte/count/pid/time accounting, wakeup, and return value setup.

On errors after RACCT reservation, it rolls back RACCT message count and size.

## `msgrcv`

`sys_msgrcv()` delegates to `kern_msgrcv()` and then copies out the returned message type.

`kern_msgrcv()` performs:

- Jail visibility and queue ID/sequence validation.
- Read permission through `ipcperm(..., IPC_R)`.
- MAC queue receive checks.
- Message selection:
  - `msgtyp == 0`: first message.
  - Positive `msgtyp`: exact type match.
  - Negative `msgtyp`: first message with type less than or equal to absolute value.
- Size enforcement with `MSG_NOERROR` truncation semantics.
- Optional blocking with `msleep()` unless `IPC_NOWAIT` is set.
- `EIDRM` detection if the queue is removed while sleeping.
- Queue unlink and bookkeeping before copyout.
- RACCT subtraction for queued message count and size.
- Segment-by-segment copyout from `msgpool`.
- Header/segment release through `msg_freehdr()`.
- Wakeup of senders and return of actual copied byte count.

## Visibility and Sysctls

`sysctl_msqids()` exports the queue array through `kern.ipc.msqids`, hiding entries invisible to the caller’s jail and clearing kernel pointers/labels/credentials before output.

`kern_get_msqids()` returns a sanitized allocated snapshot of queue descriptors for kernel consumers.

The file also exposes sysctls for:

- `kern.ipc.msgmax`
- `kern.ipc.msgmni`
- `kern.ipc.msgmnb`
- `kern.ipc.msgtql`
- `kern.ipc.msgssz`
- `kern.ipc.msgseg`
- `kern.ipc.msqids`

## Compatibility Paths

The file includes 32-bit and older FreeBSD ABI support when configured:

- 32-bit wrappers for `msgctl`, `msgsnd`, `msgrcv`, and legacy `msgsys`.
- Older `freebsd7_msgctl()` conversion paths.
- Legacy multiplexed `sys_msgsys()` dispatch through `msgcalls[]`.

These wrappers convert structure layouts and message type widths, then delegate to the native kernel implementations.

## Security and Correctness Notes

This file is concurrency- and security-sensitive. Important invariants include:

- `msq_mtx` protects global queue/message state.
- `MSG_LOCKED` prevents queue slot reuse and concurrent mutation while user copy operations may fault.
- Queue sequence numbers prevent stale IPC IDs from accessing recycled slots.
- `msg_qbytes == 0` marks a queue slot free.
- Kernel pointers are scrubbed before user-visible sysctl/stat export.
- MAC hooks are placed around queue operations and individual message operations.
- Jail namespace checks are required before exposing or operating on queues.
- RACCT reservations are rolled back on send failure and subtracted on receive/removal.

The main implementation risk areas are changes around sleep/retry paths, `MSG_LOCKED` handling, RACCT rollback, and sanitization of exported queue structures.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sysv_msg.c -->