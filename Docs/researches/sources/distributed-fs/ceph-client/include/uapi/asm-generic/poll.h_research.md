# sources/distributed-fs/ceph-client/include/uapi/asm-generic/poll.h

Purpose: Defines generic poll/select event masks and `struct pollfd`.

Important APIs/types/functions: Exports standard masks `POLLIN`, `POLLPRI`, `POLLOUT`, `POLLERR`, `POLLHUP`, `POLLNVAL`, normalization/band masks, optional `POLLMSG/POLLREMOVE/POLLRDHUP`, internal `POLLFREE`, `POLL_BUSY_LOOP`, and `struct pollfd { int fd; short events; short revents; }`.

Control flow: Preprocessor guards allow architectures to define some nonstandard values before inclusion.

State/persistence: No runtime state; constants and struct layout define poll syscall ABI.

Dependencies/integration: Used by libc, event loops, and kernel poll implementations.

Risks: Mask value changes break every poll/select consumer. `__force __poll_t` casts rely on Linux type annotations.

Test signals: Headers compile checks and poll/epoll/select runtime tests.
