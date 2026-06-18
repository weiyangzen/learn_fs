# sources/distributed-fs/ceph-client/drivers/android/binder/deferred_close.rs

## Purpose

This Rust file implements Binder-specific deferred file-descriptor closing. It schedules `task_work` so a file whose descriptor was closed during Binder ioctl handling keeps an extra file reference until the current task returns to userspace. This mirrors the C Binder pattern that avoids use-after-free hazards when Binder closes a descriptor that might be held by an active `fdget()` light reference.

## Important APIs, types, and functions

The public helper is `DeferredFdCloser`. It owns a heap-allocated `DeferredFdCloserInner`, which is C-layout and contains a `callback_head` plus a raw `struct file *`. `DeferredFdCloser::new()` allocates the inner object. `DeferredFdCloser::close_fd()` schedules task work, removes the fd from the current file table, calls `filp_close()`, and transfers the final file ref to the task-work callback. `DeferredFdCloser::do_close_fd()` is the unsafe extern callback that reconstructs the `KBox`, calls `fput()` if needed, and frees the allocation. `DeferredFdCloseError` reports `TaskWorkUnavailable` or `BadFd` and maps to `ESRCH` or `EBADF`.

## Control flow

Callers allocate a closer before attempting the close. `close_fd()` rejects kernel threads because task work cannot run for them. It then converts the box to a raw pointer, initializes the embedded `callback_head`, and calls `task_work_add(current, ..., TWA_RESUME)` before touching the fd table. If scheduling fails, ownership returns to a `KBox` and the allocation is dropped.

After task work is scheduled, `file_close_fd(fd)` removes the descriptor and returns a file pointer if the fd was valid. Invalid fds leave the task work queued with a null file pointer, and the callback later frees the allocation. Valid fds get an extra `get_file()` ref, `filp_close()` consumes the close path's ref, and the extra ref is stored in the inner object so `do_close_fd()` releases it on return to userspace.

## State and persistence behavior

The only persistent state is the scheduled task-work allocation and the optional file ref it owns. It is bound to the current task and is expected to execute before userspace resumes. The helper is single-use: `close_fd(self, fd)` consumes the closer and either schedules ownership into task work or drops it on scheduling failure.

## Dependencies and integration points

The file depends on Rust-for-Linux allocation, raw kernel bindings for `callback_head`, task flags, `init_task_work`, `task_work_add`, `file_close_fd`, `get_file`, `filp_close`, and `fput`. It is used by allocation cleanup for Binder buffers with close-on-free fds. The comments cite the historical C Binder fix for avoiding `ksys_close()` during active `fdget()`.

## Risks

This code is unsafe-boundary heavy. The raw pointer must always refer to the first field of `DeferredFdCloserInner` so the callback cast is valid. The file pointer invariant must hold: a non-null pointer owns exactly one ref that `do_close_fd()` may release. Scheduling task work before closing avoids a half-closed fd on task-work failure, but a bad fd still queues a no-op callback; callers must tolerate `BadFd`. Calling from a kthread returns `TaskWorkUnavailable`, so higher-level cleanup must not assume closure always succeeds.

## Test signals

Useful tests include valid fd deferred close from a normal task, invalid fd returning `EBADF`, kthread context returning `ESRCH`, stress where Binder frees buffers while holding descriptors obtained through fd lookup, leak checks proving task-work allocations are freed, and KASAN tests around concurrent close/return-to-userspace paths.
