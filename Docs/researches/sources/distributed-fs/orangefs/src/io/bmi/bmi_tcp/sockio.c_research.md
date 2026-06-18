# sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/sockio.c

## Purpose

This file is a small socket utility layer for the TCP BMI method. It wraps IPv4 socket creation, bind, connect, address initialization, nonblocking receive/send/vector I/O, optional sendfile, and socket option get/set helpers.

## Important APIs, Types, And Functions

- `BMI_sockio_new_sock()` creates an `AF_INET`, `SOCK_STREAM`, `IPPROTO_TCP` socket.
- `BMI_sockio_bind_sock()` binds a socket to `INADDR_ANY` and a service port, retrying on `EINTR`.
- `BMI_sockio_bind_sock_specific()` initializes a named address and binds to it, returning BMI/PVFS error codes.
- `BMI_sockio_connect_sock()` initializes a named address and connects, retrying on `EINTR`, returning BMI/PVFS error codes.
- `BMI_sockio_init_sock()` has either a `gethostbyname` implementation with host-error conversion or an `inet_aton` implementation.
- `BMI_sockio_nbrecv()` loops nonblocking `recv` until the requested length is read, an error occurs, or `EAGAIN/EWOULDBLOCK` returns partial progress.
- `BMI_sockio_nbpeek()` peeks without consuming bytes and maps closed sockets to `EPIPE`.
- `BMI_sockio_nbsend()` loops nonblocking `send` until complete, blocked, interrupted, or errored.
- `BMI_sockio_nbvector()` performs one `readv` or `writev` attempt after retrying `EINTR`.
- `BMI_sockio_get_sockopt`, `BMI_sockio_set_tcpopt`, and `BMI_sockio_set_sockopt` wrap socket options.

## Control Flow

The bind/connect helpers construct `sockaddr_in` values through `BMI_sockio_init_sock`, then perform the syscall with `EINTR` retry. Nonblocking scalar I/O helpers loop to maximize progress until they hit would-block. Vector I/O intentionally does only one `readv` or `writev` call so the BMI progress loop can bound work per readiness event.

## State And Persistence Behavior

This file stores no global mutable state except compile-time `DEFAULT_MSG_FLAGS`. It mutates kernel socket state through bind, connect, send/receive, and socket options. Hostname resolution output is copied into caller-provided sockaddr storage.

## Dependencies And Integration Points

It depends on POSIX sockets, fcntl nonblocking flags asserted by callers, optional `gethostbyname`, optional `arpa/inet`, optional `sendfile`, BMI error conversion, and gossip logging. `bmi-tcp.c` uses this layer for all socket creation, connection, payload progress, header peeking, TCP_NODELAY, SO_REUSEADDR, and buffer-size options.

## Risks And Edge Cases

- `BMI_sockio_nbrecv` asserts the socket is nonblocking; `BMI_sockio_nbsend` does not assert but is used as nonblocking.
- `BMI_sockio_nbpeek` treats `EWOULDBLOCK` specially but not `EAGAIN` unless they are the same value on the platform.
- The fallback `inet_aton` resolver only accepts numeric IPv4 addresses.
- `BMI_sockio_init_sock` with `gethostbyname` is not reentrant/thread-safe on many platforms.
- `BMI_sockio_connect_sock` converts negative errno through `bmi_errno_to_pvfs`; callers must not convert it a second time.
- `DEFAULT_MSG_FLAGS` uses `MSG_NOSIGNAL` when available, but vector I/O via `writev` does not use `MSG_NOSIGNAL`.

## Test Signals

Tests should cover interrupted bind/connect/send/recv, nonblocking partial read/write, zero-length peer close mapping to `EPIPE`, would-block behavior, hostname and numeric address initialization, socket option wrappers, vector I/O partial progress, and builds with and without `HAVE_GETHOSTBYNAME`, `MSG_NOSIGNAL`, and `__USE_SENDFILE__`.
