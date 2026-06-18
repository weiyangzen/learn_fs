# sources/distributed-fs/ceph-client/fs/fuse/dev_uring.c

## Purpose
`dev_uring.c` implements an optional FUSE transport over `IORING_OP_URING_CMD`. It registers per-CPU userspace ring entries, switches the FUSE input queue to io_uring ops when all queues are ready, sends requests into registered header/payload buffers, commits replies, and coordinates abort/teardown.

## Important APIs, Types, and Functions
- `enable_uring` is a module parameter gating new io_uring use.
- `fuse_uring_enabled()` reports module-level enablement.
- Ring setup: `fuse_uring_create()`, `fuse_uring_create_queue()`, `fuse_uring_register()`, and `fuse_uring_do_register()`.
- Request transfer: `fuse_uring_queue_fuse_req()`, `fuse_uring_queue_bq_req()`, `fuse_uring_dispatch_ent()`, `fuse_uring_send_in_task()`, and `fuse_uring_send_next_to_ring()`.
- Reply path: `fuse_uring_commit_fetch()`, `fuse_uring_commit()`, `fuse_uring_copy_from_ring()`, and `fuse_uring_out_header_has_err()`.
- Teardown: `fuse_uring_abort_end_requests()`, `fuse_uring_stop_queues()`, `fuse_uring_entry_teardown()`, `fuse_uring_destruct()`, and cancellation handlers.
- Timeout integration: `fuse_uring_request_expired()`.

## Control Flow
Userspace submits register commands with SQE128 command payloads and two iovecs: one header area and one payload area. Registration creates the shared ring if needed, creates the queue for the requested CPU id, validates buffer sizes, allocates a `fuse_ring_ent`, marks the command cancelable, and puts the entry on the available list. Once every queue has an available entry, the code swaps `fiq->ops` to `fuse_io_uring_ops`, marks the ring ready, and wakes blocked request allocators.

Queued FUSE requests choose a queue based on `task_cpu(current)`, receive a classic FUSE unique id, and either bind to an available entry or wait in the queue's request list. Dispatch happens as io_uring task work so the daemon task context can access the registered user buffers. The send path copies the operation-specific input header to `op_in`, payload pages/args to the payload iovec, metadata to `ring_ent_in_out`, and `fuse_in_header` to `in_out`, then completes the uring command so userspace can process it.

Userspace replies with `FUSE_IO_URING_CMD_COMMIT_AND_FETCH` containing the commit id and queue id. The kernel finds the request in that queue's processing hash, transitions the entry to commit state, copies the out header and payload back into request args, ends the request, and immediately makes the same entry available/fetches the next request. This combined commit-and-fetch is required so queued kernel requests continue to flow.

## State and Persistence
State is in `fc->ring`, `struct fuse_ring`, per-queue lists, per-entry states (`FRRS_*`), queue background counters, per-queue processing hash, request `FR_URING` flags, and request backpointers to queues/entries. There is no persistent storage. Ring entries are moved to a released list instead of freed immediately to tolerate io_uring cancel races.

## Dependencies and Integration Points
This file depends on FUSE core request helpers in `dev.c`, `dev_uring_i.h`, FUSE UAPI io_uring structures in `include/uapi/linux/fuse.h`, `io_uring/cmd.h`, task-work completion, FUSE timeout scans, background request throttling, and classic FUSE ops for forget and interrupt requests. `fs/fuse/inode.c` negotiates `fc->io_uring`.

## Risks
The transport is concurrency-heavy. Queue readiness requires at least one registered entry per possible CPU, so CPU hotplug or missing queue registration can leave request allocation blocked while `fc->io_uring` is set. Entry state transitions must match list membership or teardown may leak entries. `IO_URING_F_CANCEL` can access entries directly, so released entries are intentionally retained until connection destruction. Notifications and interrupt replies are not fully supported through io_uring and fall back or reject. Background accounting is split between global `fc` counters and per-queue counters and must remain balanced on errors and abort. Unique mismatch or invalid out headers must end requests with errors without corrupting queues.

## Test Signals
Exercise register on all queues, invalid iovec/header/payload sizes, disabled module parameter, command without SQE128, commit/fetch success, wrong commit id, unique mismatch, daemon cancel/death, abort with in-userspace entries, background request flow, timeout detection, fallback forget/interrupt behavior, and lockdep/KASAN under concurrent request dispatch and teardown.
