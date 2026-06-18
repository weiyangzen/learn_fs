# sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/socket-collection-epoll.c

## Purpose

This file implements the epoll-backed socket collection used by `bmi-tcp.c` when `__PVFS2_USE_EPOLL__` is enabled. It tracks a server listening socket and connected address sockets in a Linux epoll fd and reports ready BMI method addresses plus read/write/error status bits.

## Important APIs, Types, And Functions

- `BMI_socket_collection_init(int new_server_socket)` allocates `struct socket_collection`, creates `epfd` with `epoll_create`, and optionally registers the listening socket with `event.data.ptr = NULL`.
- `BMI_socket_collection_finalize(socket_collection_p scp)` frees the collection object.
- `BMI_socket_collection_testglobal(...)` calls `epoll_wait`, converts epoll events into `SC_READ_BIT`, `SC_WRITE_BIT`, and `SC_ERROR_BIT`, and returns either a temporary server-port method address or the registered normal method address.
- The companion header supplies the add/remove/write-bit macros that call `epoll_ctl`.

## Control Flow

Initialization creates one epoll instance and optionally registers the server socket for read, error, and hangup events. Test calls clear caller output arrays, cap the wait batch at `BMI_EPOLL_MAX_PER_CYCLE`, wait for events, and translate each result. A `NULL` event pointer identifies the server socket; this causes allocation of a temporary method address marked `server_port = 1` so `bmi-tcp.c` can accept a connection. Non-NULL event pointers are returned directly as method addresses.

## State And Persistence Behavior

The only persistent state is `epfd`, `event_array`, and `server_socket` inside the collection object. Per-address registration state lives in the kernel epoll set and in each `struct tcp_addr`'s socket and write reference count, mutated by header macros.

## Dependencies And Integration Points

The file depends on Linux `<sys/epoll.h>`, OrangeFS BMI method address allocation (`alloc_tcp_method_addr`), TCP address metadata, gossip logging, and the shared socket collection status-bit contract. `bmi-tcp.c` consumes returned server-port pseudo-addresses in `handle_new_connection` and normal addresses in send/receive/error progress handlers.

## Risks And Edge Cases

- `BMI_socket_collection_finalize` frees the collection but does not close `epfd`, so ownership must be verified at a higher level or this leaks an fd.
- If registering the server socket fails after `epoll_create`, the error path frees `tmp_scp` but also does not close `epfd`.
- `epoll_wait` returns raw `-errno` rather than converting through `bmi_tcp_errno_to_pvfs`, unlike the poll implementation.
- The code tests `scp->event_array[i].events & POLLIN/POLLOUT`; on Linux these values match epoll event bits, but the source includes `<sys/poll.h>` to make that implicit dependency work.
- Server pseudo-address allocation uses `assert`, so allocation failure can abort.

## Test Signals

Tests should exercise server socket readiness, normal read/write readiness, EPOLLERR/EPOLLHUP conversion, empty waits, interrupted `epoll_wait`, more ready fds than `BMI_EPOLL_MAX_PER_CYCLE`, duplicate add handling from the header macros, write-bit add/remove transitions, and finalize under fd-leak checking.
