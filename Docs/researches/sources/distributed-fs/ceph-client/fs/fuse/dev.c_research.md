# sources/distributed-fs/ceph-client/fs/fuse/dev.c

## Purpose
`dev.c` implements the classic `/dev/fuse` transport and much of the common FUSE request lifecycle. It allocates requests, queues foreground/background work, copies requests and replies between kernel and daemon via read/write/splice, handles notifications, aborts connections, exposes device ioctls, and registers the FUSE misc device.

## Important APIs, Types, and Functions
- Request lifecycle: `fuse_get_req()`, `fuse_put_request()`, `fuse_send_one()`, `fuse_request_end()`, `__fuse_simple_request()`, and `fuse_simple_background()`.
- Queue ops: `fuse_dev_queue_forget()`, `fuse_dev_queue_interrupt()`, `fuse_dev_queue_req()`, and exported `fuse_dev_fiq_ops`.
- Copy helpers: `fuse_copy_init/finish()`, `fuse_copy_args()`, `fuse_copy_out_args()`, folio and splice helpers.
- Device paths: `fuse_dev_do_read()`, `fuse_dev_do_write()`, `fuse_dev_read/write()`, `splice_read/write()`, `poll()`, `fasync()`, and `release()`.
- Notifications: poll, inode/entry invalidation, delete, store, retrieve, resend, epoch increment, and prune.
- Teardown: `fuse_abort_conn()`, `fuse_wait_aborted()`, `fuse_dev_end_requests()`.
- Ioctls: clone, passthrough backing open/close, and sync init.

## Control Flow
Kernel FUSE operations allocate a `fuse_req`, fill credentials and headers, adjust for protocol compatibility, and queue through `fuse_iqueue_ops`. Foreground requests wait in `request_wait_answer()`, optionally sending `FUSE_INTERRUPT` on signal and removing pending requests on fatal signals when possible. Background requests are throttled by `max_background`, `num_background`, `active_background`, and `bg_queue`.

The daemon reads `/dev/fuse`; `fuse_dev_do_read()` waits for pending interrupts, forgets, or requests, copies headers and input args to userspace, then moves reply-expected requests into the per-device processing hash with `FR_SENT`. The daemon writes replies; `fuse_dev_do_write()` validates `fuse_out_header`, dispatches unsolicited notifications when `unique == 0`, finds processing requests by unique id, copies output args/pages, and ends the request. Splice paths use the same copy state but move through pipe buffers, including optional folio replacement.

Abort clears connection state, cancels timeout work, drains per-device IO/processing queues, pending queues, forget lists, background queues, and polls, wakes waiters, and delegates io_uring abort outside `fc->lock`. Releasing the last device aborts the connection.

## State and Persistence
State is in `fuse_conn`, `fuse_iqueue`, `fuse_pqueue`, `fuse_dev`, `fuse_req`, background counters, request flags, unique IDs, and the `fuse_request` kmem cache. No data is persisted directly here; the userspace daemon owns filesystem persistence. Page-cache mutations can occur through notify store/retrieve and reply page copying.

## Dependencies and Integration Points
This file integrates with the FUSE inode/file/dir layers, FUSE protocol headers, tracepoints, misc device registration, waitqueues, fasync, pipe/splice, page cache, io_uring transport hooks, passthrough backing-file management, and `fusectl` abort/limit controls.

## Risks
The risk surface is broad: request flag transitions must be atomic and ordered; copying must not fault while a request is locked; abort races with read/write/splice must not leak or double-end requests; background throttling must wake waiters correctly; notify handlers must validate sizes and names from userspace; resend is only safe for idempotent or duplicate-aware daemons. Timeout scanning checks list heads and can miss transient reordered cases, but should eventually catch stuck requests. Passthrough ioctls are feature-gated but share the same device interface.

## Test Signals
Signals include libfuse mount smoke tests, foreground and background operations, signal interruption, interrupt replies, large read buffers, SETXATTR too-large behavior, splice read/write, notify invalidation/store/retrieve/delete/resend/prune, abort from fusectl, daemon death, cloned devices, passthrough ioctls, io_uring-enabled fallback, timeout-induced abort, kmemleak/refcount checks, and lockdep under concurrent teardown.
