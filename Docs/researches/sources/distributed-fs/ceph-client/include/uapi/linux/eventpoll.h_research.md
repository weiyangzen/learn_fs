# sources/distributed-fs/ceph-client/include/uapi/linux/eventpoll.h

This UAPI header defines the epoll userspace ABI: creation flags, control operation codes, event mask bits, the packed `struct epoll_event`, and busy-poll parameter ioctls. It is consumed directly by libc, applications, and kernel compatibility layers.

Important exports include `EPOLL_CLOEXEC`, `EPOLL_CTL_ADD`, `EPOLL_CTL_DEL`, `EPOLL_CTL_MOD`, readiness bits `EPOLLIN`, `EPOLLPRI`, `EPOLLOUT`, `EPOLLERR`, `EPOLLHUP`, `EPOLLRDHUP`, edge/one-shot flags `EPOLLET` and `EPOLLONESHOT`, power-management flag `EPOLLWAKEUP`, exclusive wakeup flag `EPOLLEXCLUSIVE`, and internal recursion marker `EPOLL_URING_WAKE`. `struct epoll_event` carries `__poll_t events` and opaque `__u64 data`; `struct epoll_params` is used with `EPIOCSPARAMS` and `EPIOCGPARAMS`.

Control flow is the standard epoll lifecycle: create an epoll fd, add/modify/delete target fds with `epoll_ctl`, then block or poll with `epoll_wait` variants. Kernel state consists of interest lists, ready lists, target file callbacks, busy-poll settings, and wakeup bookkeeping. Persistence is fd lifetime only; closing the epoll fd drops all registrations.

Dependencies include `linux/fcntl.h` for `O_CLOEXEC`, `linux/types.h` for `__poll_t`, and architecture-specific packing behavior. Integration points are virtually all pollable file types, io_uring poll paths, network busy-poll support, suspend blockers, and userspace event loops.

Risks include structure packing mismatches on x86-64/compat, incorrect use of edge-triggered or one-shot modes causing missed wakeups, `EPOLLEXCLUSIVE` semantics surprises, CAP requirements for `EPOLLWAKEUP`, and recursion issues involving io_uring wakeups. Test signals include libc header compatibility, epoll ctl/wait selftests, 32-bit compat ABI tests, busy-poll ioctl validation, and race tests for close, dup, fork, and nested epoll.
