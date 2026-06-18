# sources/distributed-fs/ceph-client/io_uring/epoll.c

## Purpose
`epoll.c` provides io_uring operations for `epoll_ctl` and `epoll_wait`-style event delivery.

## Important APIs, Types, And Functions
- `struct io_epoll` stores epoll fd, operation, target fd, and optional event.
- `struct io_epoll_wait` stores max events and userspace event array.
- `io_epoll_ctl_prep()` parses the SQE and copies an event from userspace when the operation needs one.
- `io_epoll_ctl()` calls `do_epoll_ctl()`.
- `io_epoll_wait_prep()` parses wait output buffer and count.
- `io_epoll_wait()` calls `epoll_sendevents()` on `req->file`.

## Control Flow
Prep rejects unsupported SQE fields. `epoll_ctl` can be issued nonblocking; if `do_epoll_ctl()` returns `-EAGAIN` under nonblocking issue flags, the request is retried later. `epoll_wait` returns `-EAGAIN` when no events are sent so io_uring can arm/retry instead of completing with zero.

## State And Persistence
Persistent effects occur in the target epoll instance through `do_epoll_ctl()`. Wait operations copy events to userspace and otherwise keep no local state.

## Dependencies And Integration Points
The file depends on eventpoll internals, uaccess, io_uring request helpers, and `CONFIG_EPOLL` object inclusion. `epoll.h` exposes handlers to `opdef`.

## Risks And Edge Cases
Userspace event copy can fault. Nonblocking `epoll_ctl` needs careful `-EAGAIN` propagation. `epoll_wait` must use the request file as the epoll file and returns retry semantics for empty results.

## Test Signals
Tests should cover add/mod/del control operations, invalid event pointers, nonblocking retry paths, wait returning events, and empty wait producing retry.
